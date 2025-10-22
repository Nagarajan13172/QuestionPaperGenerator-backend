"""
Test script for Question Paper Generator API
Run this after starting the server to test the functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Sample syllabus with proper formatting
SAMPLE_SYLLABUS = """Unit 1: Introduction to Data Structures
- Arrays and their operations
- Linked Lists (Single, Double, Circular)
- Stack and Queue operations
- Time and Space Complexity

Unit 2: Trees and Graphs
- Binary Trees and Binary Search Trees
- Tree Traversal Algorithms (Inorder, Preorder, Postorder)
- AVL Trees and Balancing
- Graph Representation and Traversal (BFS, DFS)

Unit 3: Sorting and Searching
- Bubble Sort, Selection Sort, Insertion Sort
- Quick Sort and Merge Sort
- Binary Search and Linear Search
- Hashing and Hash Tables

Unit 4: Advanced Data Structures
- Heaps and Priority Queues
- B-Trees and B+ Trees
- Tries and Suffix Trees
- Disjoint Set Data Structures"""


def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_upload_syllabus():
    """Test syllabus upload"""
    print("\n" + "="*60)
    print("TEST 2: Upload Syllabus")
    print("="*60)
    
    data = {
        "course_name": "Data Structures and Algorithms",
        "content": SAMPLE_SYLLABUS
    }
    
    response = requests.post(
        f"{BASE_URL}/api/syllabus/upload/text",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"Syllabus ID: {result['id']}")
        print(f"Course Name: {result['course_name']}")
        print(f"Units Found: {len(result['units'])}")
        
        for unit in result['units']:
            print(f"\n  Unit {unit['order']}: {unit['title']}")
            print(f"    Topics ({len(unit['topics'])}): {', '.join(unit['topics'][:3])}...")
        
        return result['id']
    else:
        print(f"Error: {response.text}")
        return None


def test_generate_question_paper(syllabus_id):
    """Test question paper generation"""
    print("\n" + "="*60)
    print("TEST 3: Generate Question Paper")
    print("="*60)
    
    if not syllabus_id:
        print("Skipping: No syllabus ID available")
        return None
    
    data = {
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
    }
    
    print(f"Generating paper for syllabus: {syllabus_id}")
    print("Requesting: 10 MCQ (1 mark) + 5 Descriptive (5 marks) + 3 Essay (8 marks)")
    print("This may take 30-60 seconds...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/question-paper/generate",
            json=data,
            timeout=120  # 2 minute timeout
        )
        
        elapsed = time.time() - start_time
        print(f"\nGeneration completed in {elapsed:.1f} seconds")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"\n✓ Question Paper Generated Successfully!")
            print(f"Paper ID: {result['id']}")
            print(f"Total Questions: {result['total_questions']}")
            print(f"Total Marks: {result['total_marks']}")
            print(f"\nUnit Coverage:")
            for unit_id, count in result['units_coverage'].items():
                print(f"  {unit_id}: {count} questions")
            
            print(f"\n--- Sample Questions ---")
            for i, q in enumerate(result['questions'][:3], 1):
                print(f"\n{i}. [{q['type']} - {q['marks']} marks]")
                print(f"   {q['question_text'][:100]}...")
                if q.get('options'):
                    print(f"   Options: {len(q['options'])} provided")
                if q.get('correct_answer'):
                    print(f"   Answer: {q['correct_answer'][:50]}...")
            
            if len(result['questions']) > 3:
                print(f"\n... and {len(result['questions']) - 3} more questions")
            
            return result['id']
        else:
            print(f"Error: {response.text}")
            return None
            
    except requests.Timeout:
        print("Request timed out after 2 minutes")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_get_question_paper(paper_id):
    """Test retrieving a question paper"""
    print("\n" + "="*60)
    print("TEST 4: Retrieve Question Paper")
    print("="*60)
    
    if not paper_id:
        print("Skipping: No paper ID available")
        return
    
    response = requests.get(f"{BASE_URL}/api/question-paper/{paper_id}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Retrieved paper: {result['id']}")
        print(f"  Questions: {result['total_questions']}")
        print(f"  Total Marks: {result['total_marks']}")


def test_list_all():
    """Test listing all syllabi and papers"""
    print("\n" + "="*60)
    print("TEST 5: List All Resources")
    print("="*60)
    
    # List syllabi
    response = requests.get(f"{BASE_URL}/api/syllabus/")
    print(f"Syllabi found: {len(response.json())}")
    
    # List papers
    response = requests.get(f"{BASE_URL}/api/question-paper/")
    print(f"Papers found: {len(response.json())}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("QUESTION PAPER GENERATOR - API TEST SUITE")
    print("="*60)
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        # Test 1: Health check
        if not test_health_check():
            print("\n❌ Server not responding. Make sure it's running!")
            return
        
        # Test 2: Upload syllabus
        syllabus_id = test_upload_syllabus()
        if not syllabus_id:
            print("\n❌ Syllabus upload failed")
            return
        
        # Test 3: Generate question paper
        paper_id = test_generate_question_paper(syllabus_id)
        
        # Test 4: Retrieve paper
        test_get_question_paper(paper_id)
        
        # Test 5: List all
        test_list_all()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.ConnectionError:
        print("\n❌ Cannot connect to server at http://localhost:8000")
        print("Please start the server first:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
