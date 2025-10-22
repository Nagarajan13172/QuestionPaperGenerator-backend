#!/usr/bin/env python3
"""
Test PDF syllabus upload and question generation
Uses the actual Data Structures Syllabus.pdf file
"""
import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"
PDF_FILE = "Data Structures Syllabus.pdf"

def test_pdf_upload():
    """Test uploading the PDF syllabus"""
    print("🚀 Testing PDF Syllabus Upload")
    print("=" * 60)
    
    if not os.path.exists(PDF_FILE):
        print(f"❌ PDF file not found: {PDF_FILE}")
        print("   Make sure the file is in the current directory")
        sys.exit(1)
    
    print(f"\n📤 Step 1: Uploading PDF syllabus...")
    print(f"   File: {PDF_FILE}")
    print(f"   Size: {os.path.getsize(PDF_FILE) / 1024:.1f} KB")
    
    try:
        # Upload PDF file
        with open(PDF_FILE, 'rb') as f:
            files = {'file': (PDF_FILE, f, 'application/pdf')}
            data = {'course_name': 'Data Structures'}
            
            response = requests.post(
                f"{BASE_URL}/api/syllabus/upload/file",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code != 201:
            print(f"❌ Upload failed: {response.text}")
            sys.exit(1)
        
        syllabus = response.json()
        syllabus_id = syllabus['id']
        
        print(f"\n✅ PDF uploaded and parsed successfully!")
        print(f"   Syllabus ID: {syllabus_id}")
        print(f"   Course: {syllabus['course_name']}")
        print(f"   Units found: {len(syllabus['units'])}")
        
        print(f"\n📚 Parsed Units:")
        for i, unit in enumerate(syllabus['units'], 1):
            print(f"\n   {i}. {unit['title']}")
            print(f"      ID: {unit['id']}")
            print(f"      Topics ({len(unit['topics'])}):")
            for j, topic in enumerate(unit['topics'][:5], 1):
                print(f"        {j}. {topic}")
            if len(unit['topics']) > 5:
                print(f"        ... and {len(unit['topics']) - 5} more topics")
        
        # Check if parsing was successful
        if len(syllabus['units']) == 0:
            print("\n⚠️  Warning: No units found!")
            print("   The PDF might need better formatting or manual text extraction")
            return None
        
        if len(syllabus['units']) == 1 and syllabus['units'][0]['title'] == "General Topics":
            print("\n⚠️  Warning: Only generic unit found")
            print("   PDF might not have clear unit headers")
            print("   Proceeding with available content...")
        
        return syllabus_id
        
    except requests.ConnectionError:
        print("❌ Cannot connect to server.")
        print("   Make sure server is running: uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_question_generation(syllabus_id):
    """Generate questions from the uploaded syllabus"""
    print("\n" + "=" * 60)
    print("📝 Step 2: Generating Questions")
    print("=" * 60)
    
    if not syllabus_id:
        print("❌ No syllabus ID available")
        sys.exit(1)
    
    # Request: 10 MCQ (1 mark) + 5 descriptive (5 marks) + 3 essay (8 marks)
    print("\n📋 Question Configuration:")
    print("   - 10 Multiple Choice Questions (1 mark each)")
    print("   - 5 Descriptive Questions (5 marks each)")
    print("   - 3 Essay Questions (8 marks each)")
    print("   Total: 18 questions, 64 marks")
    
    print("\n⏳ Generating... (this may take 30-90 seconds)")
    print("   Please wait while Gemini AI creates each question...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/question-paper/generate",
            json={
                "syllabus_id": syllabus_id,
                "generation_rules": {
                    "question_types": [
                        {"marks": 1, "count": 10, "type": "multiple_choice"},
                        {"marks": 5, "count": 5, "type": "descriptive"},
                        {"marks": 8, "count": 3, "type": "essay"}
                    ],
                    "difficulty_distribution": {
                        "easy": 40,
                        "medium": 40,
                        "hard": 20
                    },
                    "unit_selection": "all",
                    "include_answer_key": True,
                    "randomize_order": True
                }
            },
            timeout=180  # 3 minutes
        )
        
        if response.status_code != 201:
            print(f"\n❌ Generation failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            sys.exit(1)
        
        paper = response.json()
        
        print(f"\n✅ Question Paper Generated Successfully!")
        print("=" * 60)
        print(f"   Paper ID: {paper['id']}")
        print(f"   Total Questions: {paper['total_questions']}")
        print(f"   Total Marks: {paper['total_marks']}")
        
        print(f"\n📊 Distribution by Unit:")
        for unit_id, count in sorted(paper['units_coverage'].items()):
            print(f"   {unit_id}: {count} questions")
        
        # Analyze question types
        print(f"\n📋 Questions by Type:")
        type_counts = {}
        for q in paper['questions']:
            type_counts[q['type']] = type_counts.get(q['type'], 0) + 1
        
        for qtype, count in type_counts.items():
            marks_sum = sum(q['marks'] for q in paper['questions'] if q['type'] == qtype)
            print(f"   {qtype.replace('_', ' ').title()}: {count} questions ({marks_sum} marks)")
        
        # Show sample questions
        print("\n" + "=" * 60)
        print("📝 SAMPLE QUESTIONS")
        print("=" * 60)
        
        # Show 2 MCQ questions
        mcqs = [q for q in paper['questions'] if q['type'] == 'multiple_choice']
        if mcqs:
            print("\n1️⃣  MULTIPLE CHOICE QUESTIONS (1 mark each):")
            for i, q in enumerate(mcqs[:2], 1):
                print(f"\n   Q{i}. {q['question_text']}")
                if q.get('options'):
                    for opt in q['options']:
                        print(f"       {opt}")
                    print(f"       ✓ Correct Answer: {q.get('correct_answer', 'N/A')}")
                else:
                    print(f"       ⚠️  No options provided")
                print(f"       Unit: {q['unit_name']}")
        
        # Show 1 descriptive question
        descs = [q for q in paper['questions'] if q['type'] == 'descriptive']
        if descs:
            print("\n5️⃣  DESCRIPTIVE QUESTIONS (5 marks each):")
            q = descs[0]
            print(f"\n   Q. {q['question_text']}")
            if q.get('answer_explanation'):
                print(f"      Marking Scheme: {q['answer_explanation'][:100]}...")
            print(f"      Unit: {q['unit_name']}")
        
        # Show 1 essay question
        essays = [q for q in paper['questions'] if q['type'] == 'essay']
        if essays:
            print("\n8️⃣  ESSAY QUESTIONS (8 marks each):")
            q = essays[0]
            print(f"\n   Q. {q['question_text']}")
            if q.get('answer_explanation'):
                print(f"      Marking Scheme: {q['answer_explanation'][:100]}...")
            print(f"      Unit: {q['unit_name']}")
        
        # Quality checks
        print("\n" + "=" * 60)
        print("🔍 QUALITY CHECK")
        print("=" * 60)
        
        # Check uniqueness
        unique_questions = len(set(q['question_text'] for q in paper['questions']))
        if unique_questions == paper['total_questions']:
            print(f"   ✅ All {unique_questions} questions are unique")
        else:
            print(f"   ⚠️  Only {unique_questions}/{paper['total_questions']} unique questions")
            duplicates = paper['total_questions'] - unique_questions
            print(f"       {duplicates} duplicate(s) found")
        
        # Check MCQ options
        mcq_count = len(mcqs)
        mcq_with_options = sum(1 for q in mcqs if q.get('options') and len(q['options']) >= 4)
        if mcq_with_options == mcq_count:
            print(f"   ✅ All {mcq_count} MCQs have proper options")
        else:
            print(f"   ⚠️  Only {mcq_with_options}/{mcq_count} MCQs have 4+ options")
        
        # Check answers
        with_answers = sum(1 for q in paper['questions'] if q.get('correct_answer'))
        if with_answers == paper['total_questions']:
            print(f"   ✅ All questions have answers")
        else:
            print(f"   ⚠️  Only {with_answers}/{paper['total_questions']} have answers")
        
        # Check if fallback questions were used
        fallback_count = sum(1 for q in paper['questions'] 
                            if 'key concepts' in q['question_text'].lower() or
                               'explain' in q['question_text'][:10].lower())
        if fallback_count == 0:
            print(f"   ✅ No obvious fallback questions detected")
        elif fallback_count < 3:
            print(f"   ⚠️  {fallback_count} possible fallback question(s)")
        else:
            print(f"   ⚠️  {fallback_count} likely fallback questions (API may have issues)")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the questions above")
        print(f"   2. Check server logs for any errors or warnings")
        print(f"   3. Access full paper at: {BASE_URL}/api/question-paper/{paper['id']}")
        print(f"   4. View API docs at: {BASE_URL}/api/docs")
        
        return paper['id']
        
    except requests.Timeout:
        print("\n❌ Request timed out (took > 3 minutes)")
        print("   The API might be slow or overloaded")
        print("   Try with fewer questions or check your internet connection")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main test function"""
    print("\n" + "🎓" * 30)
    print("  PDF SYLLABUS TEST - Data Structures")
    print("🎓" * 30 + "\n")
    
    # Step 1: Upload PDF
    syllabus_id = test_pdf_upload()
    
    if not syllabus_id:
        print("\n❌ Cannot proceed without valid syllabus")
        sys.exit(1)
    
    # Step 2: Generate questions
    paper_id = test_question_generation(syllabus_id)
    
    print("\n" + "🎉" * 30)
    print("  ALL DONE!")
    print("🎉" * 30 + "\n")


if __name__ == "__main__":
    main()
