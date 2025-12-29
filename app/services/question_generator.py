"""
Question Generator Service
Uses Google Gemini to generate questions based on syllabus
"""
import logging
import json
import uuid
from typing import List, Dict
import google.generativeai as genai

from app.models import (
    Syllabus,
    GenerationRules,
    Question,
    QuestionType,
    DifficultyLevel,
    Unit
)
from app.config import settings

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate questions using Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info("Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            raise
    
    async def generate_questions(
        self,
        syllabus: Syllabus,
        rules: GenerationRules
    ) -> List[Question]:
        """
        Generate questions based on syllabus and rules
        
        Args:
            syllabus: Syllabus object with units
            rules: Generation rules
            
        Returns:
            List of generated questions
        """
        try:
            questions = []
            
            # Calculate distribution
            distribution = self._calculate_distribution(syllabus.units, rules)
            
            # Generate questions for each unit and type
            for unit_id, type_counts in distribution.items():
                unit = next(u for u in syllabus.units if u.id == unit_id)
                
                for question_type, config in type_counts.items():
                    for _ in range(config['count']):
                        question = await self._generate_single_question(
                            unit=unit,
                            marks=config['marks'],
                            question_type=question_type,
                            difficulty=config['difficulty']
                        )
                        if question:
                            questions.append(question)
            
            # Randomize if requested
            if rules.randomize_order:
                import random
                random.shuffle(questions)
            
            logger.info(f"Generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}", exc_info=True)
            raise
    
    def _calculate_distribution(
        self,
        units: List[Unit],
        rules: GenerationRules
    ) -> Dict:
        """
        Calculate how to distribute questions across units
        
        Returns:
            Dict with structure: {unit_id: {question_type: {marks, count, difficulty}}}
        """
        distribution = {}
        num_units = len(units)
        
        for qt_config in rules.question_types:
            # Distribute evenly across units
            base_count = qt_config.count // num_units
            remainder = qt_config.count % num_units
            
            for i, unit in enumerate(units):
                if unit.id not in distribution:
                    distribution[unit.id] = {}
                
                # Add extra question to first units to handle remainder
                count = base_count + (1 if i < remainder else 0)
                
                if count > 0:
                    distribution[unit.id][qt_config.type] = {
                        'marks': qt_config.marks,
                        'count': count,
                        'difficulty': qt_config.difficulty or DifficultyLevel.MEDIUM
                    }
        
        return distribution
    
    async def _generate_single_question(
        self,
        unit: Unit,
        marks: int,
        question_type: QuestionType,
        difficulty: DifficultyLevel
    ) -> Question:
        """
        Generate a single question using Gemini
        
        Args:
            unit: Unit to generate question for
            marks: Marks for the question
            question_type: Type of question
            difficulty: Difficulty level
            
        Returns:
            Generated question
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Create prompt based on question type
                prompt = self._create_prompt(unit, marks, question_type, difficulty)
                
                logger.debug(f"Generating {question_type.value} question for unit '{unit.title}' (attempt {attempt + 1}/{max_retries})")
                
                # Generate with Gemini - note: this is synchronous, not async
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.GEMINI_TEMPERATURE,
                        max_output_tokens=settings.GEMINI_MAX_TOKENS or 1024,
                    )
                )
                
                # Check if response was blocked or empty
                if not response or not response.text:
                    logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        continue
                    raise ValueError("Gemini returned empty response")
                
                logger.debug(f"Gemini response: {response.text[:200]}...")
                
                # Parse response
                question_data = self._parse_response(response.text, question_type)
                
                # Validate question data
                if not question_data.get('question') or len(question_data.get('question', '')) < 10:
                    logger.warning(f"Invalid question data received (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        continue
                    raise ValueError("Invalid question generated")
                
                # Create Question object
                question = Question(
                    id=f"q_{uuid.uuid4().hex[:8]}",
                    unit_id=unit.id,
                    unit_name=unit.title,
                    question_text=question_data.get('question', ''),
                    marks=marks,
                    type=question_type,
                    difficulty=difficulty,
                    options=question_data.get('options'),
                    correct_answer=question_data.get('correct_answer'),
                    answer_explanation=question_data.get('explanation'),
                    course_outcome=question_data.get('course_outcome', 'CO1'),
                    blooms_level=question_data.get('blooms_level', 'K1')
                )
                
                logger.info(f"✓ Successfully generated {question_type.value} question: {question.question_text[:60]}...")
                return question
                
            except Exception as e:
                logger.error(f"Error generating question (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    # Only use fallback after all retries exhausted
                    logger.error(f"All retries exhausted, using fallback question for {unit.title}")
                    return self._create_fallback_question(unit, marks, question_type, difficulty)
        
        # This shouldn't be reached, but just in case
        return self._create_fallback_question(unit, marks, question_type, difficulty)
    
    def _create_fallback_question(
        self,
        unit: Unit,
        marks: int,
        question_type: QuestionType,
        difficulty: DifficultyLevel
    ) -> Question:
        """Create a fallback question when API fails"""
        topics_str = ", ".join(unit.topics[:3]) if unit.topics else unit.title
        
        # Determine CO and BL based on marks and type
        if marks == 1:
            co = "CO1"
            bl = "K1"
        elif marks <= 3:
            co = "CO2"
            bl = "K2"
        elif marks <= 5:
            co = "CO3"
            bl = "K3"
        else:
            co = "CO4"
            bl = "K4"
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                unit_id=unit.id,
                unit_name=unit.title,
                question_text=f"Which of the following is related to {unit.title}?",
                marks=marks,
                type=question_type,
                difficulty=difficulty,
                options=[
                    f"A) {unit.topics[0] if unit.topics else 'Option A'}",
                    f"B) {unit.topics[1] if len(unit.topics) > 1 else 'Option B'}",
                    "C) None of the above",
                    "D) All of the above"
                ],
                correct_answer="A",
                answer_explanation="This is a fallback question due to API error.",
                course_outcome=co,
                blooms_level=bl
            )
        else:
            return Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                unit_id=unit.id,
                unit_name=unit.title,
                question_text=f"Explain the key concepts covered in {unit.title}. Topics include: {topics_str}",
                marks=marks,
                type=question_type,
                difficulty=difficulty,
                correct_answer=f"Students should explain: {topics_str}",
                answer_explanation="This is a fallback question due to API error.",
                course_outcome=co,
                blooms_level=bl
            )
    
    def _create_prompt(
        self,
        unit: Unit,
        marks: int,
        question_type: QuestionType,
        difficulty: DifficultyLevel
    ) -> str:
        """Create a prompt for Gemini based on question parameters"""
        
        # Get topics for this unit
        topics_list = unit.topics[:5] if unit.topics else [unit.title]
        topics_str = "\n- ".join(topics_list)
        
        base_prompt = f"""You are an expert educator creating exam questions for a course.

UNIT: {unit.title}
TOPICS TO COVER:
- {topics_str}

TASK: Create ONE {difficulty.value} difficulty {question_type.value.replace('_', ' ')} question worth {marks} marks.

REQUIREMENTS:
- Question MUST be specific to the topics listed above
- Use clear, unambiguous language
- Appropriate difficulty for {difficulty.value} level
- Test real understanding, not just recall"""
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            if marks == 1:
                base_prompt += f"""
- 1-mark questions should test recall or basic understanding
- Create exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- All distractors should be plausible but clearly wrong

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{{
  "question": "What is [specific concept] in {unit.title}?",
  "options": [
    "A) First option",
    "B) Second option",
    "C) Third option", 
    "D) Fourth option"
  ],
  "correct_answer": "A",
  "explanation": "Why A is correct (1-2 sentences)",
  "course_outcome": "CO1",
  "blooms_level": "K1"
}}"""
            else:
                base_prompt += f"""
- {marks}-mark questions should test application/analysis
- Create exactly 4 options (A, B, C, D)
- Only ONE option should be correct

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{{
  "question": "A specific scenario or problem related to {unit.title}",
  "options": [
    "A) First option",
    "B) Second option",
    "C) Third option",
    "D) Fourth option"
  ],
  "correct_answer": "A",
  "explanation": "Detailed explanation (2-3 sentences)",
  "course_outcome": "CO2",
  "blooms_level": "K2"
}}"""
        
        elif question_type == QuestionType.TRUE_FALSE:
            base_prompt += """
- Create a clear statement about a specific concept
- Statement should be clearly true OR clearly false

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{
  "question": "Specific statement about the topic",
  "options": ["True", "False"],
  "correct_answer": "True",
  "explanation": "Why this statement is true/false",
  "course_outcome": "CO1",
  "blooms_level": "K1"
}"""
        
        elif question_type == QuestionType.SHORT_ANSWER:
            base_prompt += f"""
- {marks}-mark questions should require brief explanation
- Question should have 2-4 key points in the answer

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{{
  "question": "Specific question about {unit.title} concepts?",
  "correct_answer": "Key points: 1) point one 2) point two 3) point three",
  "explanation": "Marking scheme: 1 mark per key point",
  "course_outcome": "CO2",
  "blooms_level": "K2"
}}"""
        
        elif question_type == QuestionType.DESCRIPTIVE:
            base_prompt += f"""
- {marks}-mark questions need detailed explanation
- Should test deep understanding and ability to elaborate

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{{
  "question": "Explain/Describe/Analyze [specific aspect of {unit.title}] in detail.",
  "correct_answer": "Expected answer structure with key points",
  "explanation": "Marking scheme: marks for each major point",
  "course_outcome": "CO3",
  "blooms_level": "K3"
}}"""
        
        elif question_type == QuestionType.ESSAY:
            base_prompt += f"""
- {marks}-mark questions require comprehensive answer
- Should allow student to demonstrate broad understanding

IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{{
  "question": "Comprehensive question about {unit.title} requiring essay-type answer.",
  "correct_answer": "Structure: Introduction, main points, examples, conclusion",
  "explanation": "Marking scheme breakdown",
  "course_outcome": "CO4",
  "blooms_level": "K4"
}}"""
        
        else:  # FILL_BLANK
            base_prompt += """
IMPORTANT: Return ONLY valid JSON in this exact format (no extra text):
{
  "question": "Statement with _____ blank to fill",
  "correct_answer": "word or phrase for blank",
  "explanation": "Why this is the answer",
  "course_outcome": "CO1",
  "blooms_level": "K1"
}"""
        
        return base_prompt
    
    def _parse_response(self, response_text: str, question_type: QuestionType) -> Dict:
        """Parse Gemini response into structured data"""
        try:
            # Try to extract JSON from response
            # Sometimes Gemini wraps JSON in markdown code blocks
            json_str = response_text.strip()
            
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                # Try to find JSON in any code block
                parts = json_str.split("```")
                for i, part in enumerate(parts):
                    if part.strip().startswith('{'):
                        json_str = part.strip()
                        break
            
            # Remove any leading/trailing whitespace and newlines
            json_str = json_str.strip()
            
            # Try to find JSON object if mixed with other text
            if not json_str.startswith('{'):
                # Look for JSON object in the text
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = json_str[start:end]
            
            logger.debug(f"Attempting to parse JSON: {json_str[:200]}...")
            data = json.loads(json_str)
            
            # Validate required fields
            if 'question' not in data:
                raise ValueError("Missing 'question' field in response")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw response: {response_text[:500]}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            logger.error(f"Raw response: {response_text[:500]}")
            raise
