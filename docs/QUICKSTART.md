# 🚀 Quick Start Guide - Question Paper Generator

## 📖 TL;DR - Get Started in 3 Steps

```bash
# 1. Extract from your PDF
python3 extract_from_pdf.py "Data Structures Syllabus.pdf"

# 2. Start server
source .venv/bin/activate
uvicorn app.main:app --reload

# 3. Run test (auto-uploads & generates questions)
python3 test_cleaned_syllabus.py
```

## 🎯 Common Tasks

### Upload Syllabus (Text Format)

**From file:**
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d "{\"course_name\": \"Data Structures\", \"content\": \"$(cat cleaned_syllabus.txt)\"}"
```

**From Python:**
```python
import requests

with open('cleaned_syllabus.txt', 'r') as f:
    content = f.read()

response = requests.post(
    "http://localhost:8000/api/syllabus/upload/text",
    json={"course_name": "Data Structures", "content": content}
)

syllabus_id = response.json()['id']
print(f"Uploaded: {syllabus_id}")
```

### Generate Questions

**Standard Template (10 MCQ + 5 Descriptive + 3 Essay):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/question-paper/generate",
    json={
        "syllabus_id": "your_syllabus_id_here",
        "total_marks": 73,
        "question_types": [
            {"type": "mcq", "marks": 1, "count": 10},
            {"type": "descriptive", "marks": 5, "count": 5},
            {"type": "essay", "marks": 8, "count": 3}
        ]
    }
)

paper = response.json()

# Show questions
for q in paper['questions']:
    print(f"\n[{q['type'].upper()}] ({q['marks']} marks)")
    print(q['question_text'])
```

## 🔧 Troubleshooting Cheat Sheet

| Problem | Quick Fix |
|---------|-----------|
| "Only 1 unit found" | Use `extract_from_pdf.py` script |
| "All questions identical" | Upload text, not PDF |
| "Connection refused" | Start server: `uvicorn app.main:app --reload` |
| "API key error" | Check `GEMINI_API_KEY` in `.env` |
| "Module not found" | Activate venv: `source .venv/bin/activate` |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `extract_from_pdf.py` | **Extract & format PDF syllabus** |
| `test_cleaned_syllabus.py` | Full end-to-end test |
| `cleaned_syllabus.txt` | Formatted syllabus output |
| `FINAL_SOLUTION.md` | **Complete guide** |
| `README.md` | Full documentation |

## 🎯 Perfect Syllabus Format

```
Unit 1: First Topic Name
- Subtopic 1
- Subtopic 2
- Subtopic 3

Unit 2: Second Topic Name
- Another subtopic
- More details

Unit 3: Third Topic Name
- Keep it organized
- One topic per line
```

## 📊 Question Distribution Examples

**Example 1: University Exam (100 marks)**
```json
{
  "total_marks": 100,
  "question_types": [
    {"type": "mcq", "marks": 1, "count": 20},
    {"type": "descriptive", "marks": 5, "count": 8},
    {"type": "essay", "marks": 10, "count": 4}
  ]
}
```

**Example 2: Quick Quiz (25 marks)**
```json
{
  "total_marks": 25,
  "question_types": [
    {"type": "mcq", "marks": 1, "count": 15},
    {"type": "descriptive", "marks": 2, "count": 5}
  ]
}
```

**Example 3: Assignment (50 marks)**
```json
{
  "total_marks": 50,
  "question_types": [
    {"type": "descriptive", "marks": 5, "count": 6},
    {"type": "essay", "marks": 10, "count": 2}
  ]
}
```

## 🌐 API URLs

- **API Base:** http://localhost:8000/api
- **Interactive Docs:** http://localhost:8000/api/docs
- **Upload Text:** POST `/api/syllabus/upload/text`
- **Upload PDF:** POST `/api/syllabus/upload/file`
- **Generate Questions:** POST `/api/question-paper/generate`
- **List Syllabi:** GET `/api/syllabus/list`
- **List Papers:** GET `/api/question-paper/list`

## 🎓 Question Types

| Type | Typical Marks | Best For |
|------|---------------|----------|
| `mcq` | 1 | Quick recall, testing concepts |
| `descriptive` | 2-5 | Explain processes, compare concepts |
| `essay` | 8-15 | Deep analysis, application, evaluation |

## ⚡ One-Liner Commands

```bash
# Kill running server
pkill -f "uvicorn app.main:app"

# Start server in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# Check if server is running
curl http://localhost:8000/api/health || echo "Server not running"

# View recent logs
tail -f server.log

# Install all deps
pip install -r requirements.txt

# Activate virtualenv
source .venv/bin/activate
```

## 💾 Batch Processing Script

```bash
#!/bin/bash
# process_all_pdfs.sh

for pdf in *.pdf; do
    echo "Processing: $pdf"
    python3 extract_from_pdf.py "$pdf"
    
    course_name=$(basename "$pdf" .pdf)
    response=$(curl -s -X POST "http://localhost:8000/api/syllabus/upload/text" \
      -H "Content-Type: application/json" \
      -d "{\"course_name\": \"$course_name\", \"content\": \"$(cat cleaned_syllabus.txt | sed 's/"/\\"/g')\"}")
    
    echo "✅ $course_name uploaded"
done
```

## 🎯 Success Checklist

Before declaring success, verify:

- ✅ Extraction shows correct number of units (e.g., 5 units)
- ✅ Each unit has multiple distinct topics (not all crammed together)
- ✅ Generated questions are all unique (no duplicates)
- ✅ Questions are relevant to specific topics (not generic)
- ✅ No fallback questions like "Explain the key concepts..."
- ✅ Mix of difficulty levels (easy, medium, hard)
- ✅ Proper distribution of question types

## 📞 Getting Help

1. **Check the docs:** `FINAL_SOLUTION.md` has everything
2. **View API docs:** http://localhost:8000/api/docs
3. **Check logs:** `tail -f /tmp/fastapi_server.log`
4. **Test extraction:** `python3 extract_from_pdf.py "your.pdf"`
5. **Verify .env:** Make sure `GEMINI_API_KEY` is set

## 🎉 You're Ready!

The system is working. Follow the 3-step quick start at the top of this file!

---

**For complete documentation, see [FINAL_SOLUTION.md](FINAL_SOLUTION.md)**
