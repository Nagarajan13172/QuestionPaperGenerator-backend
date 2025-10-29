#!/usr/bin/env python3
"""
Test script for PDF download endpoint
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_pdf_download():
    """Test PDF download endpoint"""
    
    # First, get list of question papers
    print("📋 Fetching available question papers...")
    response = requests.get(f"{BASE_URL}/question-paper/")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch question papers: {response.status_code}")
        print(response.text)
        return False
    
    papers = response.json()
    
    if not papers:
        print("❌ No question papers found. Generate one first.")
        return False
    
    # Get first paper ID
    paper_id = papers[0]["id"]
    course_name = papers[0]["course_name"]
    print(f"✓ Found question paper: {paper_id} ({course_name})")
    
    # Test PDF download without answers
    print(f"\n📄 Testing PDF download (without answers)...")
    response = requests.get(f"{BASE_URL}/question-paper/{paper_id}/pdf")
    
    if response.status_code != 200:
        print(f"❌ Failed to download PDF: {response.status_code}")
        print(response.text)
        return False
    
    # Check content type
    content_type = response.headers.get('Content-Type')
    if content_type != 'application/pdf':
        print(f"❌ Wrong content type: {content_type}")
        return False
    
    # Save PDF
    filename = f"test_{paper_id}_no_answers.pdf"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print(f"✓ PDF downloaded successfully: {filename}")
    print(f"  Size: {len(response.content)} bytes")
    
    # Test PDF download with answers
    print(f"\n📄 Testing PDF download (with answers)...")
    response = requests.get(f"{BASE_URL}/question-paper/{paper_id}/pdf?include_answers=true")
    
    if response.status_code != 200:
        print(f"❌ Failed to download PDF with answers: {response.status_code}")
        print(response.text)
        return False
    
    # Save PDF
    filename = f"test_{paper_id}_with_answers.pdf"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print(f"✓ PDF with answers downloaded successfully: {filename}")
    print(f"  Size: {len(response.content)} bytes")
    
    # Test non-existent paper
    print(f"\n📄 Testing non-existent paper...")
    response = requests.get(f"{BASE_URL}/question-paper/qp_nonexistent/pdf")
    
    if response.status_code != 404:
        print(f"⚠️  Expected 404, got: {response.status_code}")
    else:
        print(f"✓ Correctly returns 404 for non-existent paper")
    
    print("\n✅ All tests passed!")
    print(f"\n🔗 You can download PDFs using:")
    print(f"   {BASE_URL}/question-paper/{paper_id}/pdf")
    print(f"   {BASE_URL}/question-paper/{paper_id}/pdf?include_answers=true")
    print(f"   {BASE_URL}/question-paper/{paper_id}/pdf?include_answers=false")
    
    return True


if __name__ == "__main__":
    try:
        success = test_pdf_download()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on http://localhost:8000?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
