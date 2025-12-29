# CO and BL Columns Feature

## Overview
Updated the question paper generator to include **Course Outcome (CO)** and **Bloom's Level (BL)** columns in the generated question papers, matching the format shown in the reference image from Gnanamani College of Technology.

## Changes Made

### 1. Schema Updates (`app/models/schemas.py`)
- Added two new optional fields to the `Question` model:
  - `course_outcome`: Course Outcome (e.g., CO1, CO2, CO3)
  - `blooms_level`: Bloom's Taxonomy Level (e.g., K1, K2, K3)

### 2. Question Generation (`app/services/question_generator.py`)
- Updated all question generation prompts to instruct Gemini AI to include CO and BL values
- Modified the `_create_prompt` method to include CO and BL in JSON response format
- Updated the Question object creation to extract and store CO and BL values
- Enhanced fallback question generation with appropriate CO and BL based on marks:
  - 1 mark → CO1, K1 (Remember)
  - 2-3 marks → CO2, K2 (Understand)
  - 4-5 marks → CO3, K3 (Apply)
  - 6+ marks → CO4, K4 (Analyze)

### 3. PDF Generation (`app/services/pdf_generator.py`)
- Redesigned question layout to use table format with four columns:
  - **Q. No.**: Question number
  - **Questions**: Question text with options
  - **CO**: Course Outcome
  - **BL**: Bloom's Level
- Added table headers for each question section
- Styled tables with borders and proper alignment

## Question Format

The generated question papers now display questions in the following format:

```
Part A – (10 X 2 = 20 Marks)

┌────────┬──────────────────────────────────────────────┬──────┬──────┐
│ Q. No. │ Questions                                    │  CO  │  BL  │
├────────┼──────────────────────────────────────────────┼──────┼──────┤
│   1.   │ Describe the type of cloud computing.        │ CO1  │  K1  │
├────────┼──────────────────────────────────────────────┼──────┼──────┤
│   2.   │ Difference between cloud computing and       │ CO1  │  K2  │
│        │ distributed computing.                       │      │      │
└────────┴──────────────────────────────────────────────┴──────┴──────┘
```

## Bloom's Taxonomy Levels

The system uses the following Bloom's Taxonomy levels:
- **K1**: Remember (recall facts and basic concepts)
- **K2**: Understand (explain ideas or concepts)
- **K3**: Apply (use information in new situations)
- **K4**: Analyze (draw connections among ideas)
- **K5**: Evaluate (justify a decision or course of action)
- **K6**: Create (produce new or original work)

## Course Outcomes

Course outcomes are mapped based on the unit and complexity:
- **CO1**: Basic knowledge and comprehension
- **CO2**: Application of concepts
- **CO3**: Analysis and problem-solving
- **CO4**: Synthesis and design
- **CO5**: Evaluation and critical thinking

## Testing

Run the test script to verify the feature:

```bash
source venv/bin/activate
python3 test_co_bl.py
```

This generates a sample PDF: `generated/test_question_paper_with_co_bl.pdf`

## API Response

The API now returns questions with CO and BL fields:

```json
{
  "id": "q1",
  "unit_id": "unit_1",
  "unit_name": "Cloud Computing Fundamentals",
  "question_text": "What is cloud computing?",
  "marks": 2,
  "type": "short_answer",
  "difficulty": "easy",
  "course_outcome": "CO1",
  "blooms_level": "K1"
}
```

## Benefits

1. **Academic Standards**: Aligns with standard academic question paper formats
2. **Learning Objectives**: Clearly maps questions to course outcomes
3. **Cognitive Levels**: Shows the thinking skills being assessed
4. **Curriculum Mapping**: Helps ensure comprehensive coverage of learning objectives
5. **Assessment Planning**: Enables balanced distribution across cognitive levels
