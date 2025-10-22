"""
Example test script for Question Paper Generator API
Run after starting the server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_upload_syllabus():
    """Test syllabus upload"""
    print("Testing syllabus upload...")
    
    syllabus_data = {
        "course_name": "Data Structures and Algorithms",
        "content": """
Unit 1: Introduction to Data Structures
- Arrays and their operations
- Linked Lists (Single, Double, Circular)
- Stacks and Queues
- Applications of stacks and queues

Unit 2: Trees
- Binary Trees
- Binary Search Trees
- Tree Traversals (Inorder, Preorder, Postorder)
- AVL Trees
- B-Trees

Unit 3: Graphs
- Graph representation (Adjacency Matrix, Adjacency List)
- Graph Traversals (BFS, DFS)
- Shortest Path Algorithms (Dijkstra, Bellman-Ford)
- Minimum Spanning Tree (Prim's, Kruskal's)

Unit 4: Sorting Algorithms
- Bubble Sort, Selection Sort, Insertion Sort
- Quick Sort and Merge Sort
- Heap Sort
- Time complexity analysis

Unit 5: Searching and Hashing
- Linear and Binary Search
- Hash Tables
- Collision Resolution Techniques
- Applications of Hashing
        """
    }
    
    response = requests.post(
        f"{BASE_URL}/api/syllabus/upload/text",
        json=syllabus_data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Syllabus ID: {data['id']}")
        print(f"Units found: {len(data['units'])}")
        for unit in data['units']:
            print(f"  - {unit['title']} ({len(unit['topics'])} topics)")
        print()
        return data['id']
    else:
        print(f"Error: {response.text}\n")
        return None

def test_generate_questions(syllabus_id):
    """Test question paper generation"""
    if not syllabus_id:
        print("Skipping question generation (no syllabus ID)\n")
        return
    
    print("Testing question paper generation...")
    
    generation_rules = {
        "syllabus_id": syllabus_id,
        "generation_rules": {
            "question_types": [
                {
                    "marks": 1,
                    "count": 10,
                    "type": "multiple_choice",
                    "difficulty": "easy"
                },
                {
                    "marks": 2,
                    "count": 5,
                    "type": "short_answer",
                    "difficulty": "medium"
                },
                {
                    "marks": 5,
                    "count": 2,
                    "type": "descriptive",
                    "difficulty": "hard"
                }
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
    
    response = requests.post(
        f"{BASE_URL}/api/question-paper/generate",
        json=generation_rules
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Question Paper ID: {data['id']}")
        print(f"Total Questions: {data['total_questions']}")
        print(f"Total Marks: {data['total_marks']}")
        print(f"Units Coverage: {data['units_coverage']}")
        print("\nSample Questions:")
        for i, question in enumerate(data['questions'][:3], 1):
            print(f"\n{i}. [{question['marks']} marks] {question['question_text']}")
            if question.get('options'):
                for option in question['options']:
                    print(f"   {option}")
            if question.get('correct_answer'):
                print(f"   Answer: {question['correct_answer']}")
        print()
        return data['id']
    else:
        print(f"Error: {response.text}\n")
        return None

def test_list_syllabi():
    """Test listing syllabi"""
    print("Testing list syllabi...")
    response = requests.get(f"{BASE_URL}/api/syllabus/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total syllabi: {len(data)}\n")

def test_list_papers():
    """Test listing question papers"""
    print("Testing list question papers...")
    response = requests.get(f"{BASE_URL}/api/question-paper/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total question papers: {len(data)}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Question Paper Generator API - Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Run tests
        test_health()
        syllabus_id = test_upload_syllabus()
        test_generate_questions(syllabus_id)
        test_list_syllabi()
        test_list_papers()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
