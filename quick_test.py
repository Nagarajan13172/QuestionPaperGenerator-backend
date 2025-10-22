#!/usr/bin/env python3
"""
Quick API test - Upload syllabus and generate questions
Usage: python quick_test.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# Your syllabus content here
SYLLABUS_CONTENT = """Unit 1: Arrays and Linked Lists
- Array operations (insert, delete, search)
- Singly linked lists
- Doubly linked lists  
- Circular linked lists
- Time complexity analysis

Unit 2: Stacks and Queues
- Stack implementation using arrays
- Stack implementation using linked lists
- Queue implementation
- Circular queues
- Priority queues
- Applications of stacks and queues

Unit 3: Trees
- Binary tree concepts
- Binary search trees (BST)
- Tree traversals (inorder, preorder, postorder)
- AVL trees and balancing
- Heap data structure
- B-trees and B+ trees

Unit 4: Graphs
- Graph representation (adjacency matrix, list)
- Breadth-first search (BFS)
- Depth-first search (DFS)
- Shortest path algorithms
- Minimum spanning tree
- Topological sorting"""

def main():
    print("🚀 Quick API Test")
    print("=" * 60)
    
    # Step 1: Upload syllabus
    print("\n📤 Step 1: Uploading syllabus...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/syllabus/upload/text",
            json={
                "course_name": "Data Structures",
                "content": SYLLABUS_CONTENT
            },
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"❌ Upload failed: {response.text}")
            sys.exit(1)
        
        syllabus = response.json()
        syllabus_id = syllabus['id']
        
        print(f"✅ Syllabus uploaded: {syllabus_id}")
        print(f"   Units found: {len(syllabus['units'])}")
        
        for unit in syllabus['units']:
            print(f"   - {unit['title']}: {len(unit['topics'])} topics")
        
    except requests.ConnectionError:
        print("❌ Cannot connect to server.")
        print("   Make sure server is running: uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Step 2: Generate questions
    print("\n📝 Step 2: Generating questions...")
    print("   Requesting: 10 MCQ (1 mark) + 5 descriptive (5 marks) + 3 essay (8 marks)")
    print("   This may take 30-60 seconds, please wait...")
    
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
                    "include_answer_key": True
                }
            },
            timeout=120  # 2 minutes
        )
        
        if response.status_code != 201:
            print(f"❌ Generation failed: {response.text}")
            sys.exit(1)
        
        paper = response.json()
        
        print(f"\n✅ Question paper generated!")
        print(f"   Paper ID: {paper['id']}")
        print(f"   Total questions: {paper['total_questions']}")
        print(f"   Total marks: {paper['total_marks']}")
        
        print(f"\n📊 Unit coverage:")
        for unit_id, count in paper['units_coverage'].items():
            unit_name = next(u['title'] for u in syllabus['units'] if u['id'] == unit_id)
            print(f"   {unit_name}: {count} questions")
        
        # Show sample questions
        print(f"\n📋 Sample questions:")
        
        # Show first MCQ
        mcq = next((q for q in paper['questions'] if q['type'] == 'multiple_choice'), None)
        if mcq:
            print(f"\n   MCQ Example (1 mark):")
            print(f"   Q: {mcq['question_text'][:80]}...")
            if mcq.get('options'):
                for opt in mcq['options'][:2]:
                    print(f"      {opt}")
                print(f"      ...")
            print(f"   Answer: {mcq.get('correct_answer', 'N/A')}")
        
        # Show first descriptive
        desc = next((q for q in paper['questions'] if q['type'] == 'descriptive'), None)
        if desc:
            print(f"\n   Descriptive Example (5 marks):")
            print(f"   Q: {desc['question_text'][:80]}...")
        
        # Show first essay
        essay = next((q for q in paper['questions'] if q['type'] == 'essay'), None)
        if essay:
            print(f"\n   Essay Example (8 marks):")
            print(f"   Q: {essay['question_text'][:80]}...")
        
        print(f"\n{'='*60}")
        print("✅ Test completed successfully!")
        print(f"{'='*60}")
        
        # Check for diversity
        print("\n🔍 Quality Check:")
        unique_questions = len(set(q['question_text'] for q in paper['questions']))
        if unique_questions == paper['total_questions']:
            print(f"   ✅ All {unique_questions} questions are unique")
        else:
            print(f"   ⚠️  Only {unique_questions}/{paper['total_questions']} unique questions")
        
        # Check options
        mcq_count = sum(1 for q in paper['questions'] if q['type'] == 'multiple_choice')
        mcq_with_options = sum(1 for q in paper['questions'] 
                               if q['type'] == 'multiple_choice' and q.get('options'))
        if mcq_with_options == mcq_count:
            print(f"   ✅ All MCQs have options")
        else:
            print(f"   ⚠️  Only {mcq_with_options}/{mcq_count} MCQs have options")
        
        # Check answers
        questions_with_answers = sum(1 for q in paper['questions'] if q.get('correct_answer'))
        if questions_with_answers == paper['total_questions']:
            print(f"   ✅ All questions have answers")
        else:
            print(f"   ⚠️  Only {questions_with_answers}/{paper['total_questions']} have answers")
        
    except requests.Timeout:
        print("❌ Request timed out (took > 2 minutes)")
        print("   Try with fewer questions or check your internet")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
