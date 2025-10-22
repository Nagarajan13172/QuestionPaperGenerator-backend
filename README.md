# Question Paper Generator - Backend

AI-powered question paper generator using Google Gemini and FastAPI. Upload a syllabus and generate customized question papers with configurable question types, marks distribution, and difficulty levels.

> **⭐ NEW: PDF Extraction Helper!** If your PDF syllabus isn't parsing correctly, use `extract_from_pdf.py` to properly format it first. See [FINAL_SOLUTION.md](FINAL_SOLUTION.md) for details.

## 🚀 Features

- **Syllabus Upload**: Support for text, PDF, and TXT files
- **Intelligent Parsing**: Automatically extracts units and topics from syllabus
- **AI-Powered Generation**: Uses Google Gemini to generate contextual questions
- **Customizable Rules**: Configure question types, marks, difficulty, and distribution
- **Multiple Question Types**: MCQ, Short Answer, Descriptive, Essay, True/False
- **RESTful API**: Clean, documented API with Swagger/ReDoc
- **Answer Keys**: Optional answer key generation with explanations

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

### 1. Clone the repository

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## 🏃 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Alternative: Using Python directly

```bash
python -m app.main
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📚 API Endpoints

### Health Check

```bash
GET /health
```

### Syllabus Management

#### Upload syllabus as text
```bash
POST /api/syllabus/upload/text
Content-Type: application/json

{
  "course_name": "Introduction to Computer Science",
  "content": "Unit 1: Programming Basics\n- Variables\n- Data Types..."
}
```

#### Upload syllabus as file
```bash
POST /api/syllabus/upload/file
Content-Type: multipart/form-data

file: [PDF or TXT file]
course_name: "Data Structures"
```

#### Get a syllabus
```bash
GET /api/syllabus/{syllabus_id}
```

#### List all syllabi
```bash
GET /api/syllabus/
```

#### Delete a syllabus
```bash
DELETE /api/syllabus/{syllabus_id}
```

### Question Paper Generation

#### Generate question paper
```bash
POST /api/question-paper/generate
Content-Type: application/json

{
  "syllabus_id": "syl_abc123",
  "generation_rules": {
    "question_types": [
      {"marks": 1, "count": 20, "type": "multiple_choice", "difficulty": "easy"},
      {"marks": 5, "count": 3, "type": "descriptive", "difficulty": "medium"}
    ],
    "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20},
    "unit_selection": "all",
    "include_answer_key": true,
    "randomize_order": true
  }
}
```

#### Get a question paper
```bash
GET /api/question-paper/{paper_id}
```

#### List all question papers
```bash
GET /api/question-paper/
```

#### Delete a question paper
```bash
DELETE /api/question-paper/{paper_id}
```

## 🧪 Testing the API

### Using cURL

#### 1. Upload a syllabus
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Data Structures",
    "content": "Unit 1: Arrays and Linked Lists\n- Array operations\n- Linked list implementation\n\nUnit 2: Trees\n- Binary trees\n- Tree traversals"
  }'
```

#### 2. Generate a question paper
```bash
curl -X POST "http://localhost:8000/api/question-paper/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_id": "syl_abc123",
    "generation_rules": {
      "question_types": [
        {"marks": 1, "count": 5, "type": "multiple_choice"}
      ],
      "include_answer_key": true
    }
  }'
```

### Using Python

```python
import requests

# Upload syllabus
response = requests.post(
    "http://localhost:8000/api/syllabus/upload/text",
    json={
        "course_name": "Algorithms",
        "content": "Unit 1: Sorting\nUnit 2: Searching"
    }
)
syllabus = response.json()
print(f"Syllabus ID: {syllabus['id']}")

# Generate question paper
response = requests.post(
    "http://localhost:8000/api/question-paper/generate",
    json={
        "syllabus_id": syllabus['id'],
        "generation_rules": {
            "question_types": [
                {"marks": 2, "count": 10, "type": "short_answer"}
            ]
        }
    }
)
paper = response.json()
print(f"Generated {paper['total_questions']} questions")
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── syllabus.py      # Syllabus endpoints
│   │   └── question_paper.py # Question paper endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── syllabus_parser.py    # Syllabus parsing logic
│   │   └── question_generator.py # Question generation with Gemini
│   └── utils/               # Utility functions
├── uploads/                 # Temporary file uploads
├── generated/              # Generated question papers
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore
├── requirements.md        # Detailed requirements documentation
└── README.md             # This file
```

## 🔧 Configuration

Environment variables (in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | *Required* |
| `DEBUG` | Enable debug mode | `True` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | `10485760` (10MB) |
| `GEMINI_MODEL` | Gemini model to use | `gemini-pro` |
| `GEMINI_TEMPERATURE` | Generation temperature | `0.7` |

## 🎯 Question Types

| Type | Description | Features |
|------|-------------|----------|
| `multiple_choice` | MCQ with 4 options | Auto-generated distractors |
| `short_answer` | Brief answer questions | 2-5 marks typically |
| `descriptive` | Detailed explanation | 5-10 marks typically |
| `essay` | Long-form answers | 10+ marks |
| `true_false` | True/False statements | Quick assessment |
| `fill_blank` | Fill in the blanks | Testing specific knowledge |

## 🎓 Difficulty Levels

- **Easy**: Basic recall and understanding (Bloom's: Remember, Understand)
- **Medium**: Application and analysis (Bloom's: Apply, Analyze)
- **Hard**: Evaluation and creation (Bloom's: Evaluate, Create)

## 🚧 Limitations & Future Enhancements

### Current Limitations
- In-memory storage (data lost on restart)
- No user authentication
- Limited to text-based syllabi (no images)
- Single language support (English)

### Planned Features
- [ ] Database integration (MongoDB/PostgreSQL)
- [ ] User authentication and authorization
- [ ] PDF export with custom templates
- [ ] Question bank management
- [ ] Multi-language support
- [ ] Image-based question generation
- [ ] Batch generation
- [ ] Question difficulty auto-detection
- [ ] LMS integration (Moodle, Canvas)

## 🐛 Troubleshooting

### "Import pydantic_settings could not be resolved"
This is just a linting issue. The package will be installed when you run `pip install -r requirements.txt`.

### "Gemini API key not found"
Make sure you've created a `.env` file and added your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### "PDF parsing failed"
Ensure the PDF contains text (not scanned images). PDFs created from Word documents work best.

### Port already in use
Change the port in `.env` or specify a different port:
```bash
uvicorn app.main:app --port 8001
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For issues and questions, please check the documentation or create an issue in the repository.

---

**Happy Question Generating! 🎓✨**
