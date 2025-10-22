# PDF Syllabus Handling - Current Status & Solutions

## 🔍 Analysis of Your PDF

Your "Data Structures Syllabus.pdf" has a specific format that's challenging to parse:

### PDF Structure:
- **All content in one continuous text block** (no clear line breaks between units)
- **Units embedded inline**: "UNIT I LISTS 9", "UNIT II STACKS...", etc.
- **No clear boundaries** between units
- Contains course objectives, outcomes, textbook references all mixed together

### Current Parsing Result:
❌ Parsed as 1 giant unit with all content as a single topic  
❌ No proper unit separation  
❌ Results in identical fallback questions  

## 💡 Solutions

###  **Solution 1: Manual Text Extraction (RECOMMENDED)**

The most reliable approach for your PDF format:

1. **Extract the syllabus manually into proper format:**

Create a file `data_structures_clean.txt`:

```
Unit 1: Lists
- Abstract Data Types (ADTs)
- List ADT
- Array-based implementation
- Linked list implementation (Singly, Circular, Doubly)
- Applications of lists
- Polynomial ADT
- Radix Sort
- Multilists

Unit 2: Stacks and Queues
- Stack ADT and Operations
- Applications - Balancing Symbols
- Evaluating arithmetic expressions
- Infix to Postfix conversion
- Function Calls
- Queue ADT and Operations
- Circular Queue
- DeQueue
- Applications of Queues

Unit 3: Trees
- Tree ADT
- Tree Traversals
- Binary Tree ADT
- Expression trees
- Binary Search Tree ADT
- AVL Trees
- Priority Queue (Heaps)
- Binary Heap

Unit 4: Multiway Search Trees and Graphs
- B-Tree
- B+ Tree
- Graph Definition
- Representation of Graphs
- Types of Graph
- Breadth-first traversal
- Depth-first traversal
- Bi-connectivity
- Euler circuits
- Topological Sort
- Dijkstra's algorithm
- Minimum Spanning Tree
- Prim's algorithm
- Kruskal's algorithm

Unit 5: Searching, Sorting and Hashing
- Linear Search
- Binary Search
- Bubble sort
- Selection sort
- Insertion sort
- Shell sort
- Merge Sort
- Hashing
- Hash Functions
- Separate Chaining
- Open Addressing
- Rehashing
- Extendible Hashing
```

2. **Upload using text endpoint:**

```python
import requests

with open('data_structures_clean.txt', 'r') as f:
    content = f.read()

response = requests.post(
    "http://localhost:8000/api/syllabus/upload/text",
    json={
        "course_name": "Data Structures",
        "content": content
    }
)

print(response.json())
```

OR use curl:

```bash
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d "{\"course_name\": \"Data Structures\", \"content\": \"$(cat data_structures_clean.txt)\"}"
```

### Solution 2: Pre-process PDF Before Upload

If you need to handle many similar PDFs:

1. **Extract text from PDF manually**:
   ```bash
   pdftotext "Data Structures Syllabus.pdf" syllabus_text.txt
   ```

2. **Clean it up** (remove headers, footers, page numbers, references)

3. **Format it properly** with clear unit markers

4. **Upload the cleaned text**

### Solution 3: Use OCR/Advanced PDF Tools

For automated processing of many PDFs:

```python
import PyPDF2
import re

def clean_pdf_syllabus(pdf_path):
    """Extract and clean syllabus from PDF"""
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Extract units using regex
    units = []
    pattern = r'UNIT ([IVX]+)\s+([A-Z\s]+?)\s+\d+\s+(.*?)(?=UNIT [IVX]+|COURSE OUTCOMES|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    formatted = ""
    for num, title, content in matches:
        formatted += f"Unit {num}: {title.strip()}\n"
        # Split content into topics
        topics = re.split(r'\s*[–—]\s*', content)
        for topic in topics[:10]:  # Limit topics
            if len(topic.strip()) > 10:
                formatted += f"- {topic.strip()}\n"
        formatted += "\n"
    
    return formatted

# Use it
clean_content = clean_pdf_syllabus("Data Structures Syllabus.pdf")
print(clean_content)
```

## 📝 Quick Fix Script

I'll create a helper script for you:

```python
# clean_pdf_syllabus.py
import sys

# Paste your PDF content here (or read from file)
pdf_content = """
UNIT I LISTS 9
Abstract Data Types (ADTs) – List ADT – Array-based implementation – Linked list implementation – Singly linked lists – Circularly linked lists – Doubly-linked lists – Applications of lists – Polynomial ADT – Radix Sort – Multilists.

UNIT II STACKS AND QUEUES 9
Stack ADT – Operations – Applications – Balancing Symbols – Evaluating arithmetic expressions- Infix to Postfix conversion – Function Calls – Queue ADT – Operations – Circular Queue – DeQueue – Applications of Queues.

UNIT III TREES 9
Tree ADT – Tree Traversals - Binary Tree ADT – Expression trees – Binary Search Tree ADT – AVL Trees – Priority Queue (Heaps) – Binary Heap.

UNIT IV MULTIWAY SEARCH TREES AND GRAPHS 9
B-Tree – B+ Tree – Graph Definition – Representation of Graphs – Types of Graph - Breadth-first traversal – Depth-first traversal –– Bi-connectivity – Euler circuits – Topological Sort – Dijkstra's algorithm – Minimum Spanning Tree – Prim's algorithm – Kruskal's algorithm

UNIT V SEARCHING, SORTING AND HASHING TECHNIQUES 9
Searching – Linear Search – Binary Search. Sorting – Bubble sort – Selection sort – Insertion sort – Shell sort –. Merge Sort – Hashing – Hash Functions – Separate Chaining – Open Addressing – Rehashing – Extendible Hashing.
"""

import re

def extract_units(content):
    pattern = r'UNIT ([IVX]+)\s+([A-Z\s]+?)\s+\d+\s+(.*?)(?=UNIT [IVX]+|$)'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    
    formatted = ""
    roman_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5'}
    
    for num, title, topics_text in matches:
        unit_num = roman_map.get(num, num)
        formatted += f"Unit {unit_num}: {title.strip()}\n"
        
        # Split by dash and clean
        topics = re.split(r'\s*[–—-]\s*', topics_text)
        for topic in topics:
            topic = topic.strip()
            if len(topic) > 5 and not topic.startswith('UNIT'):
                formatted += f"- {topic}\n"
        formatted += "\n"
    
    return formatted

if __name__ == "__main__":
    result = extract_units(pdf_content)
    print(result)
    
    # Save to file
    with open('cleaned_syllabus.txt', 'w') as f:
        f.write(result)
    print("\n✅ Saved to cleaned_syllabus.txt")
```

## 🎯 Recommended Workflow

1. **For this specific PDF**:
   - Manually copy units from PDF
   - Format as shown in Solution 1
   - Upload as text (not PDF)

2. **For future PDFs**:
   - Check if they have clear unit separators
   - If yes: upload PDF directly
   - If no: extract and format first

3. **For many PDFs**:
   - Create preprocessing script
   - Automate cleaning
   - Upload formatted text

## ✅ Working Example

```bash
# Create properly formatted syllabus
cat > syllabus_clean.txt << 'EOF'
Unit 1: Lists
- Abstract Data Types
- List ADT operations
- Array implementation
- Linked list implementation

Unit 2: Stacks and Queues
- Stack ADT
- Queue ADT
- Applications
EOF

# Upload
curl -X POST "http://localhost:8000/api/syllabus/upload/text" \
  -H "Content-Type: application/json" \
  -d @- << EOF
{
  "course_name": "Data Structures",
  "content": "$(cat syllabus_clean.txt)"
}
EOF
```

## 🚀 Next Steps

1. Extract units from your PDF (copy-paste into text file)
2. Format with "Unit X:" headers and "-" bullet points
3. Upload as text using the API
4. Generate questions - should work perfectly!

**The API works great with properly formatted input - the issue is purely PDF parsing!**
