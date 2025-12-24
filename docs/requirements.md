# Requirements Analysis - Question Paper Generator

## Project Goal
Build a web application that enables educators to automatically generate customized question papers from a syllabus using AI (Google Gemini). The system should parse syllabus content into units/topics and generate questions with configurable mark distributions.

## User Stories

### US-1: Syllabus Upload
**As an** educator  
**I want to** upload my course syllabus (text or PDF file)  
**So that** the system can understand the topics to generate questions from

**Acceptance Criteria:**
- Support plain text input via text area
- Support PDF file upload (max 10MB)
- Support TXT file upload
- Parse and display extracted units/topics for confirmation
- Show error messages for invalid formats

### US-2: Question Generation Configuration
**As an** educator  
**I want to** specify the number and type of questions needed  
**So that** I can create a question paper matching my exam requirements

**Acceptance Criteria:**
- Configure multiple question types (1-mark, 2-mark, 5-mark, 8-mark, 10-mark)
- Specify count for each question type
- Set difficulty levels (Easy, Medium, Hard)
- Optionally select specific units to include/exclude
- Preview total marks and question distribution

### US-3: Question Paper Generation
**As an** educator  
**I want to** generate a question paper based on my configuration  
**So that** I can use it for examinations

**Acceptance Criteria:**
- Generate questions using Google Gemini AI
- Ensure questions are distributed across all units
- Apply randomization to avoid duplicate papers
- Generate within reasonable time (< 30 seconds)
- Show progress indicator during generation

### US-4: Question Paper Preview & Download
**As an** educator  
**I want to** preview and download the generated question paper  
**So that** I can review and use it for exams

**Acceptance Criteria:**
- Display generated questions in a clean format
- Show marks allocation for each question
- Provide download options (PDF, DOCX, HTML)
- Allow regeneration if unsatisfied
- Include answer key (optional toggle)

### US-5: Syllabus Management
**As an** educator  
**I want to** save and reuse my uploaded syllabi  
**So that** I can generate multiple question papers from the same content

**Acceptance Criteria:**
- Store uploaded syllabi with metadata (course name, date)
- List previously uploaded syllabi
- Edit/delete saved syllabi
- Quick load for new generation

## Input Formats

### Syllabus Input
1. **Plain Text**
   - Direct paste into text area
   - Expected format: Units separated by clear headings
   - Example:
     ```
     Unit 1: Introduction to Programming
     - Variables and Data Types
     - Control Structures
     - Functions
     
     Unit 2: Object-Oriented Programming
     - Classes and Objects
     - Inheritance
     - Polymorphism
     ```

2. **PDF File**
   - Max size: 10MB
   - Must contain text content (not scanned images)
   - Automatically extract text and parse units

3. **TXT File**
   - Max size: 5MB
   - UTF-8 encoding
   - Same format expectations as plain text

### Question Generation Rules
```json
{
  "question_types": [
    {"marks": 1, "count": 20, "type": "multiple_choice"},
    {"marks": 2, "count": 10, "type": "short_answer"},
    {"marks": 5, "count": 3, "type": "descriptive"},
    {"marks": 8, "count": 2, "type": "essay"}
  ],
  "difficulty_distribution": {
    "easy": 40,
    "medium": 40,
    "hard": 20
  },
  "unit_selection": "all",  // or specific unit IDs
  "include_answer_key": true
}
```

## Output Formats

### Question Paper Output
1. **HTML Preview**
   - Clean, printable format
   - Institution header section
   - Proper question numbering
   - Mark allocation display
   - Instructions section

2. **PDF Download**
   - Professional formatting
   - Page breaks and margins
   - Header/footer with course info
   - Separate answer key page (if enabled)

3. **DOCX Download**
   - Editable format
   - Consistent styling
   - Table of questions
   - Easy customization

### API Response Format
```json
{
  "question_paper_id": "qp_12345",
  "generated_at": "2025-10-17T10:30:00Z",
  "total_marks": 100,
  "total_questions": 35,
  "questions": [
    {
      "id": "q1",
      "unit_id": "unit_1",
      "unit_name": "Introduction to Programming",
      "question_text": "What is a variable?",
      "marks": 1,
      "type": "multiple_choice",
      "difficulty": "easy",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "answer_explanation": "..."
    }
  ],
  "metadata": {
    "syllabus_id": "syl_789",
    "generation_rules": {...},
    "units_coverage": {"unit_1": 10, "unit_2": 8, ...}
  }
}
```

## Question Generation Logic

### Phase 1: Syllabus Parsing
1. **Text Extraction**
   - For PDF: Use PyMuPDF or pdfplumber
   - Extract all text content
   - Preserve structure (headings, lists)

2. **Unit Detection**
   - Identify unit headings (keywords: "Unit", "Chapter", "Module")
   - Extract unit titles and numbers
   - Parse topics under each unit (bullet points, sub-headings)

3. **Topic Structuring**
   ```python
   {
     "unit_1": {
       "title": "Introduction to Programming",
       "topics": [
         "Variables and Data Types",
         "Control Structures",
         "Functions"
       ]
     }
   }
   ```

### Phase 2: Question Distribution
1. **Calculate Distribution**
   - Total questions requested: 35 (example)
   - Number of units: 5
   - Base allocation: 7 questions per unit
   - Adjust based on unit content density

2. **Stratified Sampling**
   - Ensure each unit gets representation
   - Distribute by difficulty level
   - Balance across marks allocation

3. **Example Distribution**
   ```python
   {
     "unit_1": {"1_mark": 4, "2_mark": 2, "5_mark": 1},
     "unit_2": {"1_mark": 4, "2_mark": 2, "8_mark": 1},
     ...
   }
   ```

### Phase 3: Gemini AI Integration
1. **Prompt Engineering**
   - Create structured prompts for each question type
   - Include unit content and topics
   - Specify marks, difficulty, and format
   - Request multiple variations for randomization

2. **Example Prompt Template**
   ```
   You are an expert educator creating exam questions.
   
   Subject Unit: {unit_title}
   Topics: {topic_list}
   
   Generate a {marks}-mark {difficulty} {type} question.
   
   Requirements:
   - Question must be clear and unambiguous
   - Align with Bloom's taxonomy level for {marks} marks
   - Include 4 options (A-D) for MCQ
   - Provide correct answer and brief explanation
   
   Format response as JSON:
   {
     "question": "...",
     "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
     "correct_answer": "A",
     "explanation": "..."
   }
   ```

3. **Batch Generation**
   - Group similar questions for efficient API calls
   - Implement retry logic for API failures
   - Cache responses to avoid duplicates
   - Validate generated content quality

### Phase 4: Quality Control
1. **Validation Rules**
   - Check question uniqueness (no duplicates)
   - Verify correct answer is provided
   - Ensure marks distribution matches request
   - Validate unit coverage

2. **Post-Processing**
   - Number questions sequentially
   - Group by marks or type (user preference)
   - Add instructions and formatting
   - Generate answer key separately

### Phase 5: Randomization
1. **Question Selection**
   - Generate 2x required questions per category
   - Randomly select from pool
   - Ensure different papers for multiple requests

2. **Order Randomization**
   - Shuffle question order within sections
   - Shuffle MCQ options (track correct answer)
   - Seed-based randomization for reproducibility

## Technical Constraints

### Performance
- Syllabus parsing: < 5 seconds
- Question generation: < 30 seconds
- PDF generation: < 10 seconds
- Max concurrent users: 50

### API Limits
- Google Gemini: Rate limits apply (track usage)
- Implement queuing for high-load scenarios
- Cache common question patterns

### Security
- Validate file uploads (type, size, content)
- Sanitize text inputs
- Rate limiting on API endpoints
- Secure API key storage (environment variables)

### Data Storage
- Store syllabi for reuse
- Cache generated questions (30 days)
- Log generation history for analytics
- Optional user authentication for data persistence

## Future Enhancements (Post-MVP)
- Multiple AI model support (OpenAI, Claude)
- Image-based question generation
- Question bank management
- Collaborative editing
- Question difficulty auto-detection
- Plagiarism checking for generated content
- Export to Learning Management Systems (LMS)
- Mobile app version
