#!/usr/bin/env python3
"""
Test with cleaned syllabus from PDF extraction
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_cleaned_syllabus():
    print("="*70)
    print("Testing with Cleaned Syllabus")
    print("="*70)
    
    # Read cleaned syllabus
    with open('cleaned_syllabus.txt', 'r') as f:
        content = f.read()
    
    print(f"\n📝 Syllabus content ({len(content)} chars):")
    print(content[:300] + "...\n")
    
    # Upload as text
    print("1️⃣ Uploading cleaned syllabus as text...")
    response = requests.post(
        f"{BASE_URL}/syllabus/upload/text",
        json={
            "course_name": "Data Structures (Cleaned)",
            "content": content
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return
    
    syllabus_data = response.json()
    syllabus_id = syllabus_data['id']
    print(f"✅ Syllabus uploaded: {syllabus_id}")
    print(f"   Course: {syllabus_data['course_name']}")
    print(f"   Units found: {len(syllabus_data['units'])}\n")
    
    for unit in syllabus_data['units']:
        print(f"   📚 {unit['title']}")
        print(f"      Topics: {len(unit['topics'])}")
        for topic in unit['topics'][:3]:  # Show first 3
            print(f"        - {topic}")
        if len(unit['topics']) > 3:
            print(f"        ... and {len(unit['topics']) - 3} more")
        print()
    
    # Generate questions
    print("\n2️⃣ Generating questions...")
    print("   Requested: 10 MCQs (1 mark), 5 Descriptive (5 marks), 3 Essay (8 marks)")
    
    response = requests.post(
        f"{BASE_URL}/question-paper/generate",
        json={
            "syllabus_id": syllabus_id,
            "total_marks": 73,  # 10 + 25 + 24
            "question_types": [
                {"type": "mcq", "marks": 1, "count": 10},
                {"type": "descriptive", "marks": 5, "count": 5},
                {"type": "essay", "marks": 8, "count": 3}
            ]
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.status_code}")
        print(response.text)
        return
    
    paper = response.json()
    questions = paper['questions']
    
    print(f"✅ Generated {len(questions)} questions\n")
    
    # Analyze questions
    unique_questions = set(q['question_text'] for q in questions)
    fallback_count = sum(1 for q in questions if 'explain the key concepts' in q['question_text'].lower() or 'general topics' in q['question_text'].lower())
    
    print("="*70)
    print("📊 QUESTION ANALYSIS")
    print("="*70)
    print(f"Total questions: {len(questions)}")
    print(f"Unique questions: {len(unique_questions)}/{len(questions)}")
    print(f"Duplicate questions: {len(questions) - len(unique_questions)}")
    print(f"Likely fallback questions: {fallback_count}")
    print()
    
    # Group by type
    by_type = {}
    for q in questions:
        qtype = q['type']
        if qtype not in by_type:
            by_type[qtype] = []
        by_type[qtype].append(q)
    
    print("By Type:")
    for qtype, qs in by_type.items():
        marks_list = [q['marks'] for q in qs]
        print(f"  {qtype}: {len(qs)} questions (marks: {marks_list})")
    print()
    
    # Show sample questions from each type
    print("="*70)
    print("📝 SAMPLE QUESTIONS")
    print("="*70)
    
    for qtype in ['mcq', 'descriptive', 'essay']:
        if qtype in by_type:
            print(f"\n{qtype.upper()} Questions ({by_type[qtype][0]['marks']} marks each):")
            print("-" * 70)
            for i, q in enumerate(by_type[qtype][:3], 1):  # Show first 3
                print(f"\nQ{i}. {q['question_text']}")
                if q.get('options'):
                    for opt in q['options']:
                        print(f"   {opt}")
                print(f"   [Difficulty: {q['difficulty']}]")
            if len(by_type[qtype]) > 3:
                print(f"\n   ... and {len(by_type[qtype]) - 3} more {qtype} questions")
    
    print("\n" + "="*70)
    
    if len(unique_questions) == len(questions) and fallback_count == 0:
        print("✅ SUCCESS! All questions are unique and AI-generated!")
    elif fallback_count > 0:
        print(f"⚠️  WARNING: {fallback_count} fallback questions detected (API issues)")
    else:
        print(f"⚠️  WARNING: {len(questions) - len(unique_questions)} duplicate questions")
    
    print("="*70)
    
    # Save full output
    with open('test_cleaned_result.json', 'w') as f:
        json.dump(paper, f, indent=2)
    print(f"\n💾 Full results saved to: test_cleaned_result.json")

if __name__ == "__main__":
    try:
        test_cleaned_syllabus()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
