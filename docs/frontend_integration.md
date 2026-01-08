# Frontend Integration Guide: Answer Key & Evaluation

This guide outlines how to integrate the new Answer Key API into your frontend application.

## 1. API Details

**Endpoint:** `GET /api/question-paper/{paper_id}/answer-key`

**Method:** `GET`

**Response Format:** JSON

## 2. TypeScript Interfaces

Use these interfaces to type the response data in your frontend application.

```typescript
// Type definitions for the Answer Key response

export type QuestionType = 
  | "multiple_choice"
  | "short_answer"
  | "descriptive"
  | "essay"
  | "true_false"
  | "fill_blank";

export interface AnswerKeyItem {
  question_id: string;
  question_number: number;
  question_text: string;
  type: QuestionType;
  marks: number;
  correct_answer: string;
  explanation?: string; // Optional explanation/marking scheme
}

export interface AnswerKey {
  paper_id: string;
  course_name: string;
  total_marks: number;
  generated_at: string; // ISO date string
  answers: AnswerKeyItem[];
}
```

## 3. Implementation Suggestions

### A. Dedicated "Answer Key" Link/Modal
Best for students reviewing their own paper or simple checks.
1.  Add a "View Answer Key" button on the Question Paper page.
2.  On click, fetch the answer key from `/api/question-paper/{current_paper_id}/answer-key`.
3.  Display the answers in a modal or a side drawer, indexed by question number.

### B. Evaluation/Grading Mode
Best for teachers/examiners.
1.  Create a "Evaluation Mode" toggle.
2.  When enabled, fetch the answer key.
3.  Render the `correct_answer` and `explanation` distinctively right below each question.
4.  Example UI structure:

```tsx
const QuestionCard = ({ question, answerKey }) => {
  const answer = answerKey?.find(a => a.question_id === question.id);

  return (
    <div className="card">
      <h3>Q{question.question_number}. {question.question_text} <span className="marks">({question.marks} Marks)</span></h3>
      
      {/* Student View / Question Content */}
      <div className="question-content">
        {/* ... options or input fields ... */}
      </div>

      {/* Evaluator View */}
      {answer && (
        <div className="evaluator-panel bg-green-50 p-4 mt-4 border-l-4 border-green-500">
          <h4 className="font-bold text-green-700">Correct Answer:</h4>
          <p className="text-gray-800">{answer.correct_answer}</p>
          
          {answer.explanation && (
            <div className="mt-2">
              <span className="font-semibold text-green-700">Explanation/Key Points:</span>
              <p className="text-sm text-gray-600">{answer.explanation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

## 4. Key Considerations
- **Security**: Typically, answer keys should only be accessible to authorized users (faculty/admins). Ensure your frontend authenticates these requests if you have an auth system.
- **Printing**: If you implement a "Print" feature, consider adding a checkbox to "Include Answer Key" which simply appends the answer list at the end of the printable view.
