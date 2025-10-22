# 📚 Question Paper Generator - Complete API Documentation

## 🌐 Base Information

- **Base URL**: `http://localhost:8000/api`
- **API Version**: `1.0.0`
- **Content-Type**: `application/json`
- **Documentation**: 
  - Swagger UI: http://localhost:8000/api/docs
  - ReDoc: http://localhost:8000/api/redoc
  - OpenAPI JSON: http://localhost:8000/api/openapi.json

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Syllabus Management](#syllabus-management)
3. [Question Paper Generation](#question-paper-generation)
4. [Health Check](#health-check)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## 🔐 Authentication

**Current Status**: No authentication required (v1.0.0)

**Future Implementation**: JWT-based authentication planned

```http
Authorization: Bearer <token>
```

---

## 📝 Syllabus Management

### 1. Upload Syllabus (Text)

Upload syllabus content as plain text.

**Endpoint**: `POST /api/syllabus/upload/text`

**Request Body**:
```json
{
  "course_name": "Data Structures",
  "content": "Unit 1: Lists\n- Abstract Data Types\n- Array implementation\n\nUnit 2: Trees\n- Binary Trees\n- AVL Trees"
}
```

**Response** (`201 Created`):
```json
{
  "id": "syl_b6bf97c8",
  "course_name": "Data Structures",
  "content": "Unit 1: Lists\n- Abstract Data Types...",
  "units": [
    {
      "id": "unit_1",
      "title": "Lists",
      "topics": [
        "Abstract Data Types",
        "Array implementation"
      ],
      "order": 1
    },
    {
      "id": "unit_2",
      "title": "Trees",
      "topics": [
        "Binary Trees",
        "AVL Trees"
      ],
      "order": 2
    }
  ],
  "created_at": "2025-01-17T14:30:00.123456",
  "updated_at": "2025-01-17T14:30:00.123456"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Data Structures",
    "content": "Unit 1: Lists\n- Array implementation\n- Linked lists"
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/syllabus/upload/text",
    json={
        "course_name": "Data Structures",
        "content": "Unit 1: Lists\n- Arrays\n- Linked Lists"
    }
)

syllabus = response.json()
print(f"Created syllabus: {syllabus['id']}")
```

**Validation Rules**:
- `course_name`: Required, string, min 1 character
- `content`: Required, string, min 10 characters

**Error Responses**:
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Server error during parsing

---

### 2. Upload Syllabus (File)

Upload syllabus as PDF, TXT, DOC, or DOCX file.

**Endpoint**: `POST /api/syllabus/upload/file`

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file`: File to upload (PDF, TXT, DOC, DOCX)
- `course_name`: Course name (string)

**Response** (`201 Created`):
```json
{
  "id": "syl_abc123",
  "course_name": "Operating Systems",
  "content": "Extracted text from PDF...",
  "units": [...],
  "created_at": "2025-01-17T14:30:00",
  "updated_at": "2025-01-17T14:30:00"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/file" \
  -F "file=@syllabus.pdf" \
  -F "course_name=Operating Systems"
```

**Python Example**:
```python
import requests

with open('syllabus.pdf', 'rb') as f:
    files = {'file': f}
    data = {'course_name': 'Operating Systems'}
    
    response = requests.post(
        "http://localhost:8000/api/syllabus/upload/file",
        files=files,
        data=data
    )

syllabus = response.json()
```

**Validation Rules**:
- File size: Max 10MB
- Allowed types: `.pdf`, `.txt`, `.doc`, `.docx`
- `course_name`: Required

**Error Responses**:
- `400 Bad Request`: Invalid file type or size
- `415 Unsupported Media Type`: File type not allowed
- `500 Internal Server Error`: File processing error

---

### 3. Get Syllabus by ID

Retrieve a specific syllabus by its ID.

**Endpoint**: `GET /api/syllabus/{syllabus_id}`

**Path Parameters**:
- `syllabus_id`: Unique syllabus identifier (string)

**Response** (`200 OK`):
```json
{
  "id": "syl_b6bf97c8",
  "course_name": "Data Structures",
  "content": "Unit 1: Lists...",
  "units": [
    {
      "id": "unit_1",
      "title": "Lists",
      "topics": ["Arrays", "Linked Lists"],
      "order": 1
    }
  ],
  "created_at": "2025-01-17T14:30:00",
  "updated_at": "2025-01-17T14:30:00"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/syllabus/syl_b6bf97c8"
```

**Python Example**:
```python
import requests

syllabus_id = "syl_b6bf97c8"
response = requests.get(f"http://localhost:8000/api/syllabus/{syllabus_id}")

syllabus = response.json()
print(f"Course: {syllabus['course_name']}")
print(f"Units: {len(syllabus['units'])}")
```

**Error Responses**:
- `404 Not Found`: Syllabus with given ID not found

---

### 4. List All Syllabi

Get a list of all uploaded syllabi.

**Endpoint**: `GET /api/syllabus/list`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

**Response** (`200 OK`):
```json
{
  "total": 5,
  "syllabi": [
    {
      "id": "syl_abc123",
      "course_name": "Data Structures",
      "created_at": "2025-01-17T14:30:00",
      "unit_count": 5
    },
    {
      "id": "syl_def456",
      "course_name": "Operating Systems",
      "created_at": "2025-01-17T15:00:00",
      "unit_count": 6
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/syllabus/list?skip=0&limit=10"
```

**Python Example**:
```python
import requests

response = requests.get(
    "http://localhost:8000/api/syllabus/list",
    params={"skip": 0, "limit": 20}
)

data = response.json()
print(f"Total syllabi: {data['total']}")
for syl in data['syllabi']:
    print(f"- {syl['course_name']} ({syl['unit_count']} units)")
```

---

### 5. Delete Syllabus

Delete a syllabus by ID.

**Endpoint**: `DELETE /api/syllabus/{syllabus_id}`

**Path Parameters**:
- `syllabus_id`: Unique syllabus identifier

**Response** (`200 OK`):
```json
{
  "message": "Syllabus deleted successfully",
  "id": "syl_b6bf97c8"
}
```

**cURL Example**:
```bash
curl -X DELETE "http://localhost:8000/api/syllabus/syl_b6bf97c8"
```

**Python Example**:
```python
import requests

syllabus_id = "syl_b6bf97c8"
response = requests.delete(f"http://localhost:8000/api/syllabus/{syllabus_id}")

print(response.json()['message'])
```

**Error Responses**:
- `404 Not Found`: Syllabus not found

---

## 🎯 Question Paper Generation

### 1. Generate Question Paper

Generate a new question paper from a syllabus.

**Endpoint**: `POST /api/question-paper/generate`

**Request Body**:
```json
{
  "syllabus_id": "syl_b6bf97c8",
  "total_marks": 73,
  "question_types": [
    {
      "type": "multiple_choice",
      "marks": 1,
      "count": 10,
      "difficulty": "easy"
    },
    {
      "type": "descriptive",
      "marks": 5,
      "count": 5,
      "difficulty": "medium"
    },
    {
      "type": "essay",
      "marks": 8,
      "count": 3,
      "difficulty": "hard"
    }
  ],
  "difficulty_distribution": {
    "easy": 40,
    "medium": 40,
    "hard": 20
  },
  "unit_selection": "all",
  "include_answer_key": true,
  "randomize_order": true,
  "randomize_options": true
}
```

**Simplified Request** (with defaults):
```json
{
  "syllabus_id": "syl_b6bf97c8",
  "total_marks": 73,
  "question_types": [
    {"type": "multiple_choice", "marks": 1, "count": 10},
    {"type": "descriptive", "marks": 5, "count": 5},
    {"type": "essay", "marks": 8, "count": 3}
  ]
}
```

**Response** (`201 Created`):
```json
{
  "id": "paper_xyz789",
  "syllabus_id": "syl_b6bf97c8",
  "course_name": "Data Structures",
  "generated_at": "2025-01-17T14:30:00",
  "total_marks": 73,
  "total_questions": 18,
  "questions": [
    {
      "id": "q_1",
      "unit_id": "unit_1",
      "unit_name": "Lists",
      "question_text": "What is an Abstract Data Type (ADT)?",
      "marks": 1,
      "type": "multiple_choice",
      "difficulty": "easy",
      "options": [
        "A) A data type defined by its behavior",
        "B) A physical storage structure",
        "C) A programming language",
        "D) A hardware component"
      ],
      "correct_answer": "A",
      "answer_explanation": "An ADT is defined by its behavior (operations) rather than implementation."
    },
    {
      "id": "q_11",
      "unit_id": "unit_2",
      "unit_name": "Stacks and Queues",
      "question_text": "Explain the process of converting infix notation to postfix notation with an example.",
      "marks": 5,
      "type": "descriptive",
      "difficulty": "medium",
      "options": null,
      "correct_answer": null,
      "answer_explanation": "Use a stack to hold operators. Scan expression left to right..."
    },
    {
      "id": "q_16",
      "unit_id": "unit_4",
      "unit_name": "Graphs",
      "question_text": "Discuss Dijkstra's algorithm for finding shortest paths. Include time complexity analysis and compare with Bellman-Ford algorithm.",
      "marks": 8,
      "type": "essay",
      "difficulty": "hard",
      "options": null,
      "correct_answer": null,
      "answer_explanation": "Dijkstra's algorithm uses greedy approach..."
    }
  ],
  "generation_rules": {
    "question_types": [...],
    "difficulty_distribution": {...},
    "unit_selection": "all",
    "include_answer_key": true,
    "randomize_order": true,
    "randomize_options": true
  },
  "units_coverage": {
    "unit_1": 4,
    "unit_2": 3,
    "unit_3": 4,
    "unit_4": 4,
    "unit_5": 3
  }
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/question-paper/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_id": "syl_b6bf97c8",
    "total_marks": 73,
    "question_types": [
      {"type": "multiple_choice", "marks": 1, "count": 10},
      {"type": "descriptive", "marks": 5, "count": 5},
      {"type": "essay", "marks": 8, "count": 3}
    ]
  }'
```

**Python Example**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/question-paper/generate",
    json={
        "syllabus_id": "syl_b6bf97c8",
        "total_marks": 73,
        "question_types": [
            {"type": "multiple_choice", "marks": 1, "count": 10},
            {"type": "descriptive", "marks": 5, "count": 5},
            {"type": "essay", "marks": 8, "count": 3}
        ]
    }
)

paper = response.json()
print(f"Generated paper: {paper['id']}")
print(f"Total questions: {paper['total_questions']}")

# Print all questions
for q in paper['questions']:
    print(f"\n[{q['type']}] ({q['marks']} marks)")
    print(f"Q: {q['question_text']}")
    if q['options']:
        for opt in q['options']:
            print(f"   {opt}")
```

**Question Types**:
- `multiple_choice`: MCQ with 4 options (A, B, C, D)
- `short_answer`: Short answer questions (2-5 marks)
- `descriptive`: Descriptive questions (5-8 marks)
- `essay`: Essay questions (8-15 marks)
- `true_false`: True/False questions
- `fill_blank`: Fill in the blank questions

**Difficulty Levels**:
- `easy`: Basic recall and understanding (Bloom's: Remember, Understand)
- `medium`: Application and analysis (Bloom's: Apply, Analyze)
- `hard`: Synthesis and evaluation (Bloom's: Evaluate, Create)

**Validation Rules**:
- `syllabus_id`: Must exist
- `total_marks`: Must match sum of (marks × count) for all question types
- `question_types`: At least one type required
- `difficulty_distribution`: Must sum to 100%
- `count`: Each type must have count > 0
- `marks`: Each type must have marks > 0

**Error Responses**:
- `400 Bad Request`: Invalid request (marks mismatch, invalid types, etc.)
- `404 Not Found`: Syllabus not found
- `500 Internal Server Error`: AI generation error

---

### 2. Get Question Paper by ID

Retrieve a generated question paper.

**Endpoint**: `GET /api/question-paper/{paper_id}`

**Path Parameters**:
- `paper_id`: Unique question paper identifier

**Response** (`200 OK`):
```json
{
  "id": "paper_xyz789",
  "syllabus_id": "syl_b6bf97c8",
  "course_name": "Data Structures",
  "generated_at": "2025-01-17T14:30:00",
  "total_marks": 73,
  "total_questions": 18,
  "questions": [...],
  "generation_rules": {...},
  "units_coverage": {...}
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/question-paper/paper_xyz789"
```

**Python Example**:
```python
import requests

paper_id = "paper_xyz789"
response = requests.get(f"http://localhost:8000/api/question-paper/{paper_id}")

paper = response.json()
print(f"Course: {paper['course_name']}")
print(f"Total Questions: {paper['total_questions']}")
print(f"Total Marks: {paper['total_marks']}")
```

**Error Responses**:
- `404 Not Found`: Question paper not found

---

### 3. List All Question Papers

Get a list of all generated question papers.

**Endpoint**: `GET /api/question-paper/list`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records (default: 100)
- `syllabus_id`: Filter by syllabus ID (optional)

**Response** (`200 OK`):
```json
{
  "total": 10,
  "papers": [
    {
      "id": "paper_xyz789",
      "syllabus_id": "syl_b6bf97c8",
      "course_name": "Data Structures",
      "generated_at": "2025-01-17T14:30:00",
      "total_marks": 73,
      "total_questions": 18
    },
    {
      "id": "paper_abc123",
      "syllabus_id": "syl_def456",
      "course_name": "Operating Systems",
      "generated_at": "2025-01-17T15:00:00",
      "total_marks": 100,
      "total_questions": 25
    }
  ]
}
```

**cURL Example**:
```bash
# List all papers
curl -X GET "http://localhost:8000/api/question-paper/list"

# Filter by syllabus
curl -X GET "http://localhost:8000/api/question-paper/list?syllabus_id=syl_b6bf97c8"

# Pagination
curl -X GET "http://localhost:8000/api/question-paper/list?skip=10&limit=20"
```

**Python Example**:
```python
import requests

# Get all papers for a syllabus
response = requests.get(
    "http://localhost:8000/api/question-paper/list",
    params={"syllabus_id": "syl_b6bf97c8"}
)

data = response.json()
print(f"Found {data['total']} papers")
for paper in data['papers']:
    print(f"- {paper['course_name']}: {paper['total_questions']} questions ({paper['total_marks']} marks)")
```

---

### 4. Delete Question Paper

Delete a question paper by ID.

**Endpoint**: `DELETE /api/question-paper/{paper_id}`

**Path Parameters**:
- `paper_id`: Unique question paper identifier

**Response** (`200 OK`):
```json
{
  "message": "Question paper deleted successfully",
  "id": "paper_xyz789"
}
```

**cURL Example**:
```bash
curl -X DELETE "http://localhost:8000/api/question-paper/paper_xyz789"
```

**Python Example**:
```python
import requests

paper_id = "paper_xyz789"
response = requests.delete(f"http://localhost:8000/api/question-paper/{paper_id}")

print(response.json()['message'])
```

**Error Responses**:
- `404 Not Found`: Question paper not found

---

## ❤️ Health Check

### Health Status

Check if the API is running.

**Endpoint**: `GET /api/health`

**Response** (`200 OK`):
```json
{
  "status": "healthy",
  "timestamp": "2025-01-17T14:30:00",
  "version": "1.0.0"
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/health"
```

**Python Example**:
```python
import requests

response = requests.get("http://localhost:8000/api/health")
health = response.json()

if health['status'] == 'healthy':
    print(f"✅ API is running (v{health['version']})")
else:
    print("❌ API is not healthy")
```

---

## 📊 Data Models

### Syllabus Model

```typescript
{
  id: string,              // Unique identifier (e.g., "syl_b6bf97c8")
  course_name: string,     // Course name
  content: string,         // Raw syllabus text
  units: Unit[],          // Array of parsed units
  created_at: datetime,    // Creation timestamp
  updated_at: datetime     // Last update timestamp
}
```

### Unit Model

```typescript
{
  id: string,         // Unit identifier (e.g., "unit_1")
  title: string,      // Unit title
  topics: string[],   // Array of topics
  order: number       // Sequential order
}
```

### Question Model

```typescript
{
  id: string,                    // Question identifier
  unit_id: string,               // Associated unit ID
  unit_name: string,             // Unit name
  question_text: string,         // The question
  marks: number,                 // Marks allocated
  type: QuestionType,            // Question type enum
  difficulty: DifficultyLevel,   // Difficulty enum
  options?: string[],            // MCQ options (if applicable)
  correct_answer?: string,       // Correct answer (if applicable)
  answer_explanation?: string    // Answer explanation
}
```

### Question Paper Model

```typescript
{
  id: string,                      // Paper identifier
  syllabus_id: string,             // Associated syllabus
  course_name: string,             // Course name
  generated_at: datetime,          // Generation timestamp
  total_marks: number,             // Total marks
  total_questions: number,         // Total questions
  questions: Question[],           // Array of questions
  generation_rules: GenerationRules, // Rules used
  units_coverage: {[key: string]: number} // Questions per unit
}
```

### Question Type Config

```typescript
{
  type: QuestionType,              // Type of question
  marks: number,                   // Marks per question (> 0)
  count: number,                   // Number of questions (> 0)
  difficulty?: DifficultyLevel     // Optional preferred difficulty
}
```

### Generation Rules

```typescript
{
  question_types: QuestionTypeConfig[],  // Array of question configs
  difficulty_distribution: {              // Difficulty percentages
    easy: number,      // 0-100
    medium: number,    // 0-100
    hard: number       // 0-100 (must sum to 100)
  },
  unit_selection: string,        // "all" or comma-separated unit IDs
  include_answer_key: boolean,   // Include answers (default: true)
  randomize_order: boolean,      // Randomize questions (default: true)
  randomize_options: boolean     // Randomize MCQ options (default: true)
}
```

### Enums

**QuestionType**:
```
- multiple_choice
- short_answer
- descriptive
- essay
- true_false
- fill_blank
```

**DifficultyLevel**:
```
- easy
- medium
- hard
```

---

## ⚠️ Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful GET/DELETE request |
| 201 | Created | Successful POST request (resource created) |
| 400 | Bad Request | Invalid input data, validation failed |
| 404 | Not Found | Resource not found |
| 415 | Unsupported Media Type | Invalid file type |
| 422 | Unprocessable Entity | Request validation error |
| 500 | Internal Server Error | Server-side error |

### Common Error Examples

**400 Bad Request - Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "course_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**404 Not Found**:
```json
{
  "detail": "Syllabus with id 'syl_invalid' not found"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to generate questions. Please try again."
}
```

---

## 💡 Examples

### Example 1: Complete Workflow

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Step 1: Upload syllabus
syllabus_content = """
Unit 1: Introduction to Programming
- Variables and Data Types
- Control Structures
- Functions

Unit 2: Object-Oriented Programming
- Classes and Objects
- Inheritance
- Polymorphism
"""

response = requests.post(
    f"{BASE_URL}/syllabus/upload/text",
    json={
        "course_name": "Programming 101",
        "content": syllabus_content
    }
)

syllabus = response.json()
syllabus_id = syllabus['id']
print(f"✅ Uploaded syllabus: {syllabus_id}")
print(f"   Found {len(syllabus['units'])} units")

# Step 2: Generate question paper
response = requests.post(
    f"{BASE_URL}/question-paper/generate",
    json={
        "syllabus_id": syllabus_id,
        "total_marks": 48,
        "question_types": [
            {"type": "multiple_choice", "marks": 1, "count": 10},
            {"type": "descriptive", "marks": 5, "count": 4},
            {"type": "essay", "marks": 8, "count": 2}
        ]
    }
)

paper = response.json()
paper_id = paper['id']
print(f"\n✅ Generated paper: {paper_id}")
print(f"   Total questions: {paper['total_questions']}")
print(f"   Total marks: {paper['total_marks']}")

# Step 3: Display questions by type
print("\n📝 Questions:")
for q in paper['questions']:
    print(f"\n{q['type'].upper()} ({q['marks']} marks) - {q['difficulty']}")
    print(f"Q: {q['question_text']}")
    if q.get('options'):
        for opt in q['options']:
            print(f"   {opt}")
    if q.get('correct_answer'):
        print(f"   Answer: {q['correct_answer']}")
```

### Example 2: Batch Upload Multiple Syllabi

```python
import requests
import os

BASE_URL = "http://localhost:8000/api"

# Upload multiple PDF files
pdf_files = ["ds.pdf", "os.pdf", "dbms.pdf"]

for pdf_file in pdf_files:
    if os.path.exists(pdf_file):
        course_name = os.path.splitext(pdf_file)[0].upper()
        
        with open(pdf_file, 'rb') as f:
            files = {'file': f}
            data = {'course_name': course_name}
            
            response = requests.post(
                f"{BASE_URL}/syllabus/upload/file",
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                syllabus = response.json()
                print(f"✅ {course_name}: {len(syllabus['units'])} units")
            else:
                print(f"❌ {course_name}: Failed to upload")
```

### Example 3: Generate Multiple Papers with Different Configurations

```python
import requests

BASE_URL = "http://localhost:8000/api"
syllabus_id = "syl_b6bf97c8"

# Configuration 1: Quiz (25 marks)
quiz_config = {
    "syllabus_id": syllabus_id,
    "total_marks": 25,
    "question_types": [
        {"type": "multiple_choice", "marks": 1, "count": 20},
        {"type": "short_answer", "marks": 5, "count": 1}
    ]
}

# Configuration 2: Mid-term (50 marks)
midterm_config = {
    "syllabus_id": syllabus_id,
    "total_marks": 50,
    "question_types": [
        {"type": "multiple_choice", "marks": 1, "count": 10},
        {"type": "descriptive", "marks": 5, "count": 6},
        {"type": "essay", "marks": 10, "count": 1}
    ]
}

# Configuration 3: Final Exam (100 marks)
final_config = {
    "syllabus_id": syllabus_id,
    "total_marks": 100,
    "question_types": [
        {"type": "multiple_choice", "marks": 1, "count": 20},
        {"type": "descriptive", "marks": 5, "count": 8},
        {"type": "essay", "marks": 10, "count": 4}
    ]
}

# Generate all three papers
configs = [
    ("Quiz", quiz_config),
    ("Mid-term", midterm_config),
    ("Final", final_config)
]

for name, config in configs:
    response = requests.post(
        f"{BASE_URL}/question-paper/generate",
        json=config
    )
    
    if response.status_code == 201:
        paper = response.json()
        print(f"✅ {name}: {paper['total_questions']} questions ({paper['total_marks']} marks)")
        print(f"   Paper ID: {paper['id']}")
    else:
        print(f"❌ {name}: Generation failed")
```

### Example 4: Download Question Paper as Text

```python
import requests

BASE_URL = "http://localhost:8000/api"
paper_id = "paper_xyz789"

# Get the paper
response = requests.get(f"{BASE_URL}/question-paper/{paper_id}")
paper = response.json()

# Format as text file
output = []
output.append(f"{'='*70}")
output.append(f"QUESTION PAPER")
output.append(f"{'='*70}")
output.append(f"Course: {paper['course_name']}")
output.append(f"Total Marks: {paper['total_marks']}")
output.append(f"Total Questions: {paper['total_questions']}")
output.append(f"Date: {paper['generated_at']}")
output.append(f"{'='*70}\n")

# Group by type
by_type = {}
for q in paper['questions']:
    qtype = q['type']
    if qtype not in by_type:
        by_type[qtype] = []
    by_type[qtype].append(q)

# Print questions
q_num = 1
for qtype, questions in by_type.items():
    output.append(f"\n{qtype.upper().replace('_', ' ')} QUESTIONS")
    output.append("-" * 70)
    
    for q in questions:
        output.append(f"\n{q_num}. {q['question_text']} ({q['marks']} marks)")
        
        if q.get('options'):
            for opt in q['options']:
                output.append(f"   {opt}")
        
        output.append("")
        q_num += 1

# Save to file
with open(f"question_paper_{paper_id}.txt", 'w') as f:
    f.write('\n'.join(output))

print(f"✅ Saved to question_paper_{paper_id}.txt")
```

---

## 🔧 Testing the API

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Upload syllabus
curl -X POST http://localhost:8000/api/syllabus/upload/text \
  -H "Content-Type: application/json" \
  -d '{"course_name": "Test Course", "content": "Unit 1: Test\n- Topic 1"}'

# Generate questions
curl -X POST http://localhost:8000/api/question-paper/generate \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_id": "syl_xxx",
    "total_marks": 10,
    "question_types": [{"type": "multiple_choice", "marks": 1, "count": 10}]
  }'
```

### Using Python Requests

```python
import requests

# Test connection
try:
    response = requests.get("http://localhost:8000/api/health")
    if response.status_code == 200:
        print("✅ API is reachable")
    else:
        print("❌ API returned error")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API")
```

### Using Postman

1. Import the OpenAPI spec: http://localhost:8000/api/openapi.json
2. Create a new collection
3. Add environment variables:
   - `base_url`: http://localhost:8000/api
4. Test endpoints with pre-configured requests

---

## 📚 Best Practices

### 1. Always Check Response Status

```python
response = requests.post(url, json=data)
if response.status_code in [200, 201]:
    result = response.json()
else:
    print(f"Error: {response.status_code}")
    print(response.json().get('detail'))
```

### 2. Handle Errors Gracefully

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Use Proper Content Types

```python
# For JSON
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=data, headers=headers)

# For file upload
files = {'file': open('syllabus.pdf', 'rb')}
data = {'course_name': 'Course Name'}
response = requests.post(url, files=files, data=data)
```

### 4. Validate Before Sending

```python
# Check marks calculation
total_marks = sum(qt['marks'] * qt['count'] for qt in question_types)
assert total_marks == expected_total, "Marks mismatch!"

# Check difficulty distribution
diff_dist = difficulty_distribution
assert sum(diff_dist.values()) == 100, "Must sum to 100%"
```

### 5. Store IDs for Later Use

```python
# Upload syllabus
response = requests.post(url, json=syllabus_data)
syllabus_id = response.json()['id']

# Save to database or file for later use
save_to_db(syllabus_id)

# Use later for generation
paper_response = requests.post(
    generate_url,
    json={"syllabus_id": syllabus_id, ...}
)
```

---

## 🚀 Rate Limiting & Performance

**Current Status**: No rate limiting (v1.0.0)

**Best Practices**:
- Avoid generating multiple papers simultaneously
- Wait for generation to complete before next request
- Gemini AI has rate limits (check your quota)

**Future Implementation**:
- Rate limiting: 100 requests/minute
- Caching for repeated syllabus parsing
- Background job queue for long-running generations

---

## 📞 Support & Resources

- **API Documentation**: http://localhost:8000/api/docs
- **GitHub Repository**: [Your repo URL]
- **Issue Tracker**: [Your issues URL]

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial API release
- Syllabus upload (text/PDF)
- Question generation with Gemini AI
- MCQ, Descriptive, Essay question types
- Difficulty levels support

### Planned Features
- Authentication & user management
- Question bank management
- Export to PDF/Word
- Bulk operations
- Webhooks for async generation
- Question history & versioning

---

**Last Updated**: January 17, 2025  
**API Version**: 1.0.0  
**Documentation Version**: 1.0.0
