# Testing Guide - Question Paper Generator

## 🔧 Issues Fixed

### 1. ✅ Syllabus Parser Improvements
- **Better unit detection**: Now supports multiple formats (Unit, Chapter, Module, numbered sections)
- **Roman numerals**: Supports Unit I, Unit II, etc.
- **Smart fallback**: If no units found, intelligently splits content
- **Better logging**: See exactly what's being parsed

### 2. ✅ Gemini Question Generation Improvements
- **Retry logic**: 3 attempts before fallback
- **Better prompts**: More specific instructions for each question type
- **Validation**: Checks response before accepting
- **Error handling**: Detailed logging of API errors
- **Improved parsing**: Better JSON extraction from responses

### 3. ✅ Enhanced Logging
- Debug-level logging for API calls
- Track each question generation attempt
- See what Gemini returns
- Identify parsing failures

## 🚀 How to Test

### Step 1: Make sure server is running

```bash
cd /home/allyhari/questionpaper-generator/backend
uvicorn app.main:app --reload
```

### Step 2: Test with the test script

```bash
python test_api_detailed.py
```

This will:
- ✅ Check server health
- ✅ Upload a proper syllabus with 4 units
- ✅ Generate 10 MCQ + 5 (5-mark) + 3 (8-mark) questions
- ✅ Show results and timing

### Step 3: Manual test with curl

#### A. Upload your syllabus

**Option 1: Use the sample syllabus file**
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d "{
    \"course_name\": \"Data Structures\",
    \"content\": \"$(cat sample_syllabus.md | sed 's/"/\\"/g' | tr '\n' ' ')\"
  }"
```

**Option 2: Simple inline test**
```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Data Structures",
    "content": "Unit 1: Arrays and Linked Lists\n- Array operations\n- Singly linked lists\n- Doubly linked lists\n- Circular linked lists\n\nUnit 2: Stacks and Queues\n- Stack implementation\n- Queue implementation\n- Applications of stacks\n- Priority queues\n\nUnit 3: Trees\n- Binary trees\n- Binary search trees\n- Tree traversals\n- AVL trees\n\nUnit 4: Graphs\n- Graph representation\n- BFS and DFS\n- Shortest path\n- Minimum spanning tree"
  }'
```

Save the `syllabus_id` from the response!

#### B. Generate question paper

Replace `YOUR_SYLLABUS_ID` with the ID from step A:

```bash
curl -X POST "http://localhost:8000/api/question-paper/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "syllabus_id": "YOUR_SYLLABUS_ID",
    "generation_rules": {
      "question_types": [
        {"marks": 1, "count": 10, "type": "multiple_choice"},
        {"marks": 5, "count": 5, "type": "descriptive"},
        {"marks": 8, "count": 3, "type": "essay"}
      ],
      "difficulty_distribution": {"easy": 40, "medium": 40, "hard": 20},
      "unit_selection": "all",
      "include_answer_key": true
    }
  }'
```

## 📝 Proper Syllabus Format

For best results, format your syllabus like this:

```
Unit 1: Introduction to Topic
- Subtopic 1
- Subtopic 2
- Subtopic 3

Unit 2: Advanced Concepts
- Subtopic A
- Subtopic B
- Subtopic C

Unit 3: Applications
- Topic X
- Topic Y
```

**Alternative formats also work:**
- `Chapter 1: Title`
- `Module 1: Title`
- `1. Title` (numbered sections)
- `Unit I: Title` (Roman numerals)

## 🐛 Troubleshooting

### Problem: All questions are the same

**Cause**: Gemini API might not be working (check API key)

**Solution**:
1. Check `.env` file has valid `GEMINI_API_KEY`
2. Check API quota at https://makersuite.google.com/
3. Look at server logs for "Gemini" errors

### Problem: Only one "General Topics" unit created

**Cause**: Syllabus format not recognized

**Solution**:
- Use clear unit headers: `Unit 1:`, `Chapter 1:`, etc.
- Put topics on separate lines with `-` or `•` bullets
- Add blank lines between units
- See sample_syllabus.md for reference

### Problem: Questions generation is slow

**Cause**: Making individual API calls for each question

**Expected**: 
- 10 questions ≈ 10-20 seconds
- 20 questions ≈ 20-40 seconds
- Network speed dependent

### Problem: API returns fallback questions

**Cause**: Gemini API failed after 3 retries

**Check**:
1. Look at terminal logs for error messages
2. Verify API key is valid
3. Check if you hit rate limits
4. Try with fewer questions first

## 📊 Expected Results

With the fixed code, you should see:

### ✅ Syllabus Parsing
```json
{
  "id": "syl_abc123",
  "course_name": "Data Structures",
  "units": [
    {
      "id": "unit_1",
      "title": "Arrays and Linked Lists",
      "topics": ["Array operations", "Singly linked lists", ...],
      "order": 1
    },
    {
      "id": "unit_2",
      "title": "Stacks and Queues",
      "topics": ["Stack implementation", ...],
      "order": 2
    },
    ...
  ]
}
```

### ✅ Question Generation
```json
{
  "id": "qp_xyz789",
  "total_questions": 18,
  "total_marks": 64,
  "questions": [
    {
      "id": "q_abc",
      "unit_id": "unit_1",
      "unit_name": "Arrays and Linked Lists",
      "question_text": "What is the time complexity of...",
      "marks": 1,
      "type": "multiple_choice",
      "options": ["A) O(1)", "B) O(n)", "C) O(log n)", "D) O(n^2)"],
      "correct_answer": "B",
      "answer_explanation": "Because..."
    },
    ...
  ],
  "units_coverage": {
    "unit_1": 5,
    "unit_2": 4,
    "unit_3": 5,
    "unit_4": 4
  }
}
```

## 🎯 Testing Checklist

- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] Upload syllabus detects multiple units (not just "General Topics")
- [ ] Each unit has proper title and topics
- [ ] Question generation completes in reasonable time
- [ ] Questions are DIFFERENT from each other
- [ ] Questions are relevant to their units
- [ ] MCQ questions have 4 options
- [ ] MCQ questions have correct_answer set
- [ ] Descriptive questions have proper question text
- [ ] Questions are distributed across all units

## 💡 Tips

1. **Start small**: Test with 5-10 questions first
2. **Check logs**: Watch terminal for detailed debug info
3. **Use proper format**: Follow Unit 1: format for best results
4. **Be patient**: Gemini API can take 1-3 seconds per question
5. **Test API key**: Try a simple Gemini API call first

## 📞 Need Help?

If issues persist:
1. Check terminal logs carefully
2. Verify `.env` file has correct API key
3. Test with the sample_syllabus.md file
4. Run test_api_detailed.py for automated testing
