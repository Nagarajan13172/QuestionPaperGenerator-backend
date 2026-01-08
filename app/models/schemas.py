"""
Pydantic models for Question Paper Generator
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class DifficultyLevel(str, Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, Enum):
    """Types of questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    DESCRIPTIVE = "descriptive"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"


class Unit(BaseModel):
    """Represents a syllabus unit/chapter"""
    id: str = Field(..., description="Unique identifier for the unit")
    title: str = Field(..., description="Unit title")
    topics: List[str] = Field(default_factory=list, description="List of topics in the unit")
    order: int = Field(..., description="Sequential order of the unit")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "unit_1",
                "title": "Introduction to Programming",
                "topics": ["Variables", "Data Types", "Control Structures"],
                "order": 1
            }
        }


class Syllabus(BaseModel):
    """Represents a course syllabus"""
    id: Optional[str] = Field(None, description="Unique identifier")
    course_name: str = Field(..., description="Name of the course")
    content: str = Field(..., description="Raw syllabus content")
    units: List[Unit] = Field(default_factory=list, description="Parsed units")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "Introduction to Computer Science",
                "content": "Unit 1: Programming Basics\n- Variables\n- Data Types",
                "units": []
            }
        }


class SyllabusUploadRequest(BaseModel):
    """Request model for uploading syllabus as text"""
    course_name: str = Field(..., description="Name of the course")
    content: str = Field(..., min_length=10, description="Syllabus content")

    class Config:
        json_schema_extra = {
            "example": {
                "course_name": "Data Structures",
                "content": "Unit 1: Arrays and Lists\nUnit 2: Trees and Graphs"
            }
        }


class QuestionTypeConfig(BaseModel):
    """Configuration for a specific question type"""
    marks: int = Field(..., gt=0, description="Marks for each question")
    count: int = Field(..., gt=0, description="Number of questions")
    type: QuestionType = Field(..., description="Type of question")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Preferred difficulty")

    class Config:
        json_schema_extra = {
            "example": {
                "marks": 1,
                "count": 20,
                "type": "multiple_choice",
                "difficulty": "easy"
            }
        }


class DifficultyDistribution(BaseModel):
    """Distribution of difficulty levels in percentage"""
    easy: int = Field(default=40, ge=0, le=100, description="Percentage of easy questions")
    medium: int = Field(default=40, ge=0, le=100, description="Percentage of medium questions")
    hard: int = Field(default=20, ge=0, le=100, description="Percentage of hard questions")

    @validator('hard')
    def validate_total(cls, v, values):
        """Ensure percentages add up to 100"""
        total = values.get('easy', 0) + values.get('medium', 0) + v
        if total != 100:
            raise ValueError(f"Difficulty percentages must sum to 100, got {total}")
        return v


class GenerationRules(BaseModel):
    """Rules for generating question paper"""
    question_types: List[QuestionTypeConfig] = Field(..., description="Question type configurations")
    difficulty_distribution: DifficultyDistribution = Field(
        default_factory=DifficultyDistribution,
        description="Difficulty distribution"
    )
    unit_selection: str = Field(default="all", description="'all' or comma-separated unit IDs")
    include_answer_key: bool = Field(default=True, description="Include answer key")
    randomize_order: bool = Field(default=True, description="Randomize question order")
    randomize_options: bool = Field(default=True, description="Randomize MCQ options")

    class Config:
        json_schema_extra = {
            "example": {
                "question_types": [
                    {"marks": 1, "count": 20, "type": "multiple_choice"},
                    {"marks": 5, "count": 3, "type": "descriptive"}
                ],
                "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20},
                "unit_selection": "all",
                "include_answer_key": True
            }
        }


class Question(BaseModel):
    """Represents a single question"""
    id: str = Field(..., description="Unique question identifier")
    unit_id: str = Field(..., description="Associated unit ID")
    unit_name: str = Field(..., description="Unit name for reference")
    question_text: str = Field(..., description="The question text")
    marks: int = Field(..., gt=0, description="Marks allocated")
    type: QuestionType = Field(..., description="Type of question")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    options: Optional[List[str]] = Field(None, description="Options for MCQ/True-False")
    correct_answer: Optional[str] = Field(None, description="Correct answer")
    answer_explanation: Optional[str] = Field(None, description="Explanation for the answer")
    course_outcome: Optional[str] = Field(None, description="Course Outcome (CO) - e.g., CO1, CO2, CO3")
    blooms_level: Optional[str] = Field(None, description="Bloom's Taxonomy Level - e.g., K1, K2, K3")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "q1",
                "unit_id": "unit_1",
                "unit_name": "Introduction to Programming",
                "question_text": "What is a variable?",
                "marks": 1,
                "type": "multiple_choice",
                "difficulty": "easy",
                "options": ["A) A constant value", "B) A storage location", "C) A function", "D) A loop"],
                "correct_answer": "B",
                "answer_explanation": "A variable is a storage location identified by a name.",
                "course_outcome": "CO1",
                "blooms_level": "K1"
            }
        }


class QuestionPaper(BaseModel):
    """Represents a complete question paper"""
    id: str = Field(..., description="Unique question paper ID")
    syllabus_id: str = Field(..., description="Associated syllabus ID")
    course_name: str = Field(..., description="Course name")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_marks: int = Field(..., description="Total marks")
    total_questions: int = Field(..., description="Total number of questions")
    questions: List[Question] = Field(..., description="List of questions")
    generation_rules: GenerationRules = Field(..., description="Rules used for generation")
    units_coverage: Dict[str, int] = Field(..., description="Number of questions per unit")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "qp_12345",
                "syllabus_id": "syl_789",
                "course_name": "Data Structures",
                "total_marks": 100,
                "total_questions": 35,
                "questions": [],
                "generation_rules": {},
                "units_coverage": {"unit_1": 10, "unit_2": 8}
            }
        }


class GenerateQuestionPaperRequest(BaseModel):
    """Request model for generating a question paper"""
    syllabus_id: str = Field(..., description="ID of the syllabus to use")
    generation_rules: GenerationRules = Field(..., description="Generation rules")

    class Config:
        json_schema_extra = {
            "example": {
                "syllabus_id": "syl_789",
                "generation_rules": {
                    "question_types": [
                        {"marks": 1, "count": 20, "type": "multiple_choice"}
                    ],
                    "include_answer_key": True
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AnswerKeyItem(BaseModel):
    """Represents a single answer in the answer key"""
    question_id: str = Field(..., description="ID of the question")
    question_number: int = Field(..., description="Question number in the paper")
    question_text: Optional[str] = Field(None, description="Question text context")
    type: QuestionType = Field(..., description="Type of question")
    marks: int = Field(..., description="Marks allocated")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: Optional[str] = Field(None, description="Explanation for the answer")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "question_number": 1,
                "question_text": "What is a variable?",
                "type": "multiple_choice",
                "marks": 1,
                "correct_answer": "B",
                "explanation": "A variable is a storage location identified by a name."
            }
        }


class AnswerKey(BaseModel):
    """Represents the complete answer key for a question paper"""
    paper_id: str = Field(..., description="ID of the question paper")
    course_name: str = Field(..., description="Course name")
    total_marks: int = Field(..., description="Total marks")
    generated_at: datetime = Field(..., description="When the paper was generated")
    answers: List[AnswerKeyItem] = Field(..., description="List of answers")

    class Config:
        json_schema_extra = {
            "example": {
                "paper_id": "qp_12345",
                "course_name": "Data Structures",
                "total_marks": 100,
                "generated_at": "2023-01-01T12:00:00Z",
                "answers": [
                    {
                        "question_id": "q1",
                        "question_number": 1,
                        "type": "multiple_choice",
                        "marks": 1,
                        "correct_answer": "B"
                    }
                ]
            }
        }
