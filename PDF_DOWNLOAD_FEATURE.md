# PDF Download Feature

## Overview
The Question Paper Generator API now supports downloading question papers as professionally formatted PDF files.

## Endpoint

### Download Question Paper as PDF

**URL:** `GET /api/question-paper/{paper_id}/pdf`

**Parameters:**
- `paper_id` (path, required): The ID of the question paper (e.g., `qp_768a3e89`)
- `include_answers` (query, optional): Boolean to include/exclude answers
  - `true`: Force include answers
  - `false`: Force exclude answers
  - Not provided: Uses the `include_answer_key` setting from generation rules

**Response:**
- **Content-Type:** `application/pdf`
- **Status Codes:**
  - `200 OK`: PDF successfully generated and returned
  - `404 Not Found`: Question paper with the given ID doesn't exist
  - `500 Internal Server Error`: PDF generation failed

**Headers:**
- `Content-Disposition`: `attachment; filename=<Course_Name>_<paper_id>.pdf`

## Usage Examples

### Example 1: Download with default answer settings
```bash
curl -O -J http://localhost:8000/api/question-paper/qp_768a3e89/pdf
```

### Example 2: Download without answers
```bash
curl -O -J "http://localhost:8000/api/question-paper/qp_768a3e89/pdf?include_answers=false"
```

### Example 3: Download with answers
```bash
curl -O -J "http://localhost:8000/api/question-paper/qp_768a3e89/pdf?include_answers=true"
```

### Example 4: Using Python requests
```python
import requests

# Download PDF
response = requests.get("http://localhost:8000/api/question-paper/qp_768a3e89/pdf")

if response.status_code == 200:
    with open("question_paper.pdf", "wb") as f:
        f.write(response.content)
    print("PDF downloaded successfully!")
```

### Example 5: Using JavaScript/Fetch
```javascript
// Download PDF in browser
async function downloadQuestionPaper(paperId, includeAnswers = null) {
    const url = `/api/question-paper/${paperId}/pdf${
        includeAnswers !== null ? `?include_answers=${includeAnswers}` : ''
    }`;
    
    const response = await fetch(url);
    
    if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `question_paper_${paperId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
    } else {
        console.error('Failed to download PDF:', response.statusText);
    }
}

// Usage
downloadQuestionPaper('qp_768a3e89');
downloadQuestionPaper('qp_768a3e89', true);  // with answers
downloadQuestionPaper('qp_768a3e89', false); // without answers
```

## PDF Format

The generated PDF includes:

### 1. Header Section
- **Course Name**: Prominently displayed as title
- **Question Paper ID**: Unique identifier
- **Total Marks**: Sum of all question marks
- **Total Questions**: Number of questions
- **Generated On**: Timestamp of generation

### 2. Instructions
- Standard exam instructions
- Customizable based on question paper type

### 3. Questions Section
Questions are organized by type with subsections:
- Multiple Choice Questions
- Short Answer Questions
- Descriptive Questions
- Essay Questions
- True/False Questions
- Fill in the Blanks

Each question displays:
- Question number
- Question text
- Marks allocation
- Unit/topic reference
- Options (for MCQ/True-False)
- Correct answer (if enabled)
- Answer explanation (if enabled)

## Styling

The PDF uses professional formatting:
- **Page Size**: A4
- **Margins**: 0.75 inches on all sides
- **Fonts**: Helvetica family
- **Colors**: Professional color scheme with good contrast
- **Layout**: Clean, readable structure with proper spacing

## Testing

Run the test script to verify PDF generation:

```bash
python3 test_pdf_download.py
```

This will:
1. Fetch available question papers
2. Download PDF without answers
3. Download PDF with answers
4. Verify error handling
5. Save test PDFs to disk

## Server Restart Required

After adding this feature, restart the FastAPI server:

```bash
# Stop existing server
pkill -f uvicorn

# Start server
cd /home/allyhari/questionpaper-generator/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Error Handling

The endpoint handles various error scenarios:

1. **Question Paper Not Found** (404)
   ```json
   {
     "detail": "Question paper with ID qp_invalid not found"
   }
   ```

2. **PDF Generation Error** (500)
   ```json
   {
     "detail": "Failed to generate PDF: <error details>"
   }
   ```

## Implementation Details

### New Files
- `app/services/pdf_generator.py`: PDF generation service using ReportLab

### Modified Files
- `app/routers/question_paper.py`: Added PDF download endpoint

### Dependencies
- **ReportLab** (already in requirements.txt): Professional PDF generation library

## Future Enhancements

Potential improvements:
1. Custom PDF templates
2. Institutional branding (logos, headers, footers)
3. QR codes for answer verification
4. Watermarks for security
5. Multiple page layouts
6. Export to DOCX format
7. Batch PDF generation for multiple papers
8. Custom styling options via API parameters
