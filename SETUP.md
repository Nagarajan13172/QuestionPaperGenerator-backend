# 🚀 Quick Setup Guide

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or use your preferred editor
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Step 3: Run the Server

### Option A: Using the start script (Linux/Mac)
```bash
./start.sh
```

### Option B: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option C: Using Python
```bash
python main.py
```

## Step 4: Test the API

Open your browser and visit:
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

Or run the test script:
```bash
python test_api.py
```

## Quick Test with cURL

```bash
# 1. Upload a syllabus
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Test Course",
    "content": "Unit 1: Introduction\n- Topic A\n- Topic B\n\nUnit 2: Advanced\n- Topic C"
  }'

# Note the syllabus_id from the response, then use it below

# 2. Generate questions
curl -X POST "http://localhost:8000/api/question-paper/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_id": "YOUR_SYLLABUS_ID_HERE",
    "generation_rules": {
      "question_types": [
        {"marks": 1, "count": 5, "type": "multiple_choice"}
      ],
      "include_answer_key": true
    }
  }'
```

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── main.py            # FastAPI app
│   ├── config.py          # Configuration
│   ├── models/            # Pydantic schemas
│   ├── routers/           # API endpoints
│   └── services/          # Business logic
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── .env                   # Your config (create this!)
└── README.md             # Full documentation
```

## Common Issues

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

### Module Not Found
```bash
# Make sure you're in the virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

### Gemini API Error
- Check your API key in `.env`
- Verify the key is valid at https://makersuite.google.com/app/apikey
- Check your API quota

## Next Steps

1. ✅ Upload a syllabus via the API
2. ✅ Generate a question paper
3. ✅ Explore the API documentation
4. 🚀 Integrate with your frontend
5. 📝 Customize question generation rules

For detailed documentation, see `README.md`
