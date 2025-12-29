"""
Quick test to verify API returns CO and BL values
"""
import requests
import json

# Test the API endpoint
API_BASE = "http://localhost:5173"

def test_question_paper_api():
    """Test if question papers have CO and BL values"""
    try:
        # Get all question papers
        response = requests.get(f"{API_BASE}/api/question-papers")
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return
        
        papers = response.json()
        print(f"✓ Found {len(papers)} question papers\n")
        
        # Check first paper
        if papers:
            first_paper_id = list(papers.keys())[0] if isinstance(papers, dict) else papers[0]['id']
            
            # Get detailed paper
            detail_response = requests.get(f"{API_BASE}/api/question-papers/{first_paper_id}")
            
            if detail_response.status_code == 200:
                paper = detail_response.json()
                
                print(f"Question Paper: {paper.get('course_name', 'N/A')}")
                print(f"ID: {paper.get('id', 'N/A')}")
                print(f"Total Questions: {paper.get('total_questions', 0)}\n")
                
                # Check first few questions
                questions = paper.get('questions', [])
                print("Sample Questions:")
                print("-" * 80)
                
                for i, q in enumerate(questions[:3], 1):
                    co = q.get('course_outcome', 'MISSING')
                    bl = q.get('blooms_level', 'MISSING')
                    
                    status = "✓" if co != 'MISSING' and bl != 'MISSING' else "❌"
                    
                    print(f"{status} Q{i}: CO={co}, BL={bl}")
                    print(f"   {q.get('question_text', '')[:70]}...")
                    print()
                
                # Summary
                has_co_bl = sum(1 for q in questions if q.get('course_outcome') and q.get('blooms_level'))
                print("-" * 80)
                print(f"Summary: {has_co_bl}/{len(questions)} questions have CO and BL values")
                
                if has_co_bl == len(questions):
                    print("✓ All questions have CO and BL values!")
                else:
                    print("❌ Some questions are missing CO/BL values")
            else:
                print(f"❌ Could not get paper details: {detail_response.status_code}")
        else:
            print("❌ No question papers found")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running on port 5173?")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Testing Question Paper API for CO and BL values...")
    print("=" * 80)
    test_question_paper_api()
    print("=" * 80)
