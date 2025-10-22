#!/usr/bin/env python3
"""
Helper script to extract and format syllabus from your PDF format
Run: python3 extract_from_pdf.py "Data Structures Syllabus.pdf"
"""

import sys
import re
import fitz  # PyMuPDF

def roman_to_int(roman):
    """Convert Roman numeral to integer"""
    mapping = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 
               'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
    return mapping.get(roman, roman)

def extract_units_from_pdf(pdf_path):
    """Extract units from PDF and format properly"""
    
    # Read PDF
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    
    print(f"📄 Extracted {len(text)} characters from PDF\n")
    
    # Pattern to match: UNIT I LISTS 9
    # Captures: roman numeral, title, credit hours, and content until next UNIT
    pattern = r'UNIT\s+([IVX]+)\s+([A-Z\s&,]+?)\s+(\d+)\s+(.*?)(?=UNIT\s+[IVX]+\s+|COURSE\s+OUTCOMES|TOTAL|TEXT\s*BOOKS|REFERENCES|$)'
    
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        print("❌ No units found with pattern matching!")
        print("Trying alternative extraction...\n")
        
        # Fallback: Look for simpler pattern
        lines = text.split('\n')
        for i, line in enumerate(lines[:50]):  # Check first 50 lines
            if 'UNIT' in line.upper():
                print(f"Found line {i}: {line}")
        return None
    
    print(f"✅ Found {len(matches)} units\n")
    
    formatted = ""
    all_topics = []
    
    for roman, title, credits, content in matches:
        unit_num = roman_to_int(roman)
        title = title.strip()
        
        print(f"Unit {unit_num}: {title} ({credits} credits)")
        formatted += f"Unit {unit_num}: {title}\n"
        
        # Clean content
        content = content.strip()
        
        # Split by common separators: – (en dash), — (em dash), - (hyphen)
        topics = re.split(r'\s*[–—-]\s+', content)
        
        unit_topics = []
        for topic in topics:
            topic = topic.strip()
            # Filter out noise
            if (len(topic) > 10 and 
                not topic.upper().startswith('UNIT') and
                not topic.upper().startswith('COURSE') and
                not topic.upper().startswith('TEXT') and
                not any(x in topic.lower() for x in ['page', 'edition', 'published', 'isbn'])):
                
                # Clean up the topic
                topic = re.sub(r'\s+', ' ', topic)  # Normalize whitespace
                topic = re.sub(r'\d{4}', '', topic)  # Remove years
                
                if len(topic) > 15:  # Reasonable topic length
                    formatted += f"- {topic}\n"
                    unit_topics.append(topic)
                    print(f"  - {topic[:80]}{'...' if len(topic) > 80 else ''}")
        
        all_topics.append(unit_topics)
        formatted += "\n"
        print()
    
    return formatted, matches, all_topics

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_from_pdf.py <pdf_file>")
        print("\nExample: python3 extract_from_pdf.py 'Data Structures Syllabus.pdf'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print("="*70)
    print("PDF Syllabus Extractor")
    print("="*70)
    print(f"Processing: {pdf_path}\n")
    
    result = extract_units_from_pdf(pdf_path)
    
    if result:
        formatted, matches, all_topics = result
        
        # Save to file
        output_file = "cleaned_syllabus.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        print("="*70)
        print(f"✅ Successfully extracted {len(matches)} units!")
        print(f"📝 Saved formatted syllabus to: {output_file}")
        print("="*70)
        print("\n📋 Summary:")
        for i, topics in enumerate(all_topics, 1):
            print(f"  Unit {i}: {len(topics)} topics")
        
        print("\n🚀 Next steps:")
        print("1. Review the generated file: cleaned_syllabus.txt")
        print("2. Upload it using:")
        print(f'   curl -X POST "http://localhost:8000/api/syllabus/upload/text" \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d @- << EOF')
        print(f'{{')
        print(f'  "course_name": "Data Structures",')
        print(f'  "content": "$(cat cleaned_syllabus.txt)"')
        print(f'}}')
        print(f'EOF')
        
        return 0
    else:
        print("❌ Failed to extract units. Check the PDF format.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
