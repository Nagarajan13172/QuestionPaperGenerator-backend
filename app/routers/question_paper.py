"""
Question Paper router - handles question paper generation
"""
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
import logging
import uuid
from datetime import datetime

from app.models import (
    QuestionPaper,
    GenerateQuestionPaperRequest,
    ErrorResponse,
    Syllabus,
    AnswerKey,
    AnswerKeyItem
)
from app.services.question_generator import QuestionGenerator
from app.services.pdf_generator import PDFGenerator
from app.utils.storage import get_storage
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Storage instance
storage = get_storage()
SYLLABI_STORE = "syllabi"
QUESTION_PAPERS_STORE = "question_papers"


@router.post("/generate", response_model=QuestionPaper, status_code=status.HTTP_201_CREATED)
async def generate_question_paper(request: GenerateQuestionPaperRequest):
    """
    Generate a question paper based on syllabus and rules
    """
    try:
        logger.info(f"Generating question paper for syllabus: {request.syllabus_id}")
        
        # Validate syllabus exists
        syllabus_dict = storage.get_item(SYLLABI_STORE, request.syllabus_id)
        if not syllabus_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Syllabus with ID {request.syllabus_id} not found"
            )
        
        syllabus = Syllabus(**syllabus_dict)
        
        # Validate units exist
        if not syllabus.units:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Syllabus has no parsed units. Please upload a valid syllabus."
            )
        
        # Calculate total questions
        total_questions = sum(qt.count for qt in request.generation_rules.question_types)
        if total_questions > settings.MAX_QUESTIONS_PER_REQUEST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many questions requested. Max: {settings.MAX_QUESTIONS_PER_REQUEST}"
            )
        
        # Generate questions
        generator = QuestionGenerator()
        questions = await generator.generate_questions(
            syllabus=syllabus,
            rules=request.generation_rules
        )
        
        # Calculate metrics
        total_marks = sum(q.marks for q in questions)
        units_coverage = {}
        for question in questions:
            units_coverage[question.unit_id] = units_coverage.get(question.unit_id, 0) + 1
        
        # Create question paper
        question_paper = QuestionPaper(
            id=f"qp_{uuid.uuid4().hex[:8]}",
            syllabus_id=request.syllabus_id,
            course_name=syllabus.course_name,
            total_marks=total_marks,
            total_questions=len(questions),
            questions=questions,
            generation_rules=request.generation_rules,
            units_coverage=units_coverage
        )
        
        # Store persistently
        question_paper_dict = question_paper.model_dump()
        storage.set_item(QUESTION_PAPERS_STORE, question_paper.id, question_paper_dict)
        
        logger.info(f"✓ Question paper generated with ID: {question_paper.id}")
        logger.info(f"✓ Question paper saved to persistent storage")
        return question_paper
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating question paper: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate question paper: {str(e)}"
        )


@router.get("/{paper_id}", response_model=QuestionPaper)
async def get_question_paper(paper_id: str):
    """
    Get a question paper by ID
    """
    paper_dict = storage.get_item(QUESTION_PAPERS_STORE, paper_id)
    if not paper_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question paper with ID {paper_id} not found"
        )
    
    return QuestionPaper(**paper_dict)


@router.get("/", response_model=list[QuestionPaper])
async def list_question_papers():
    """
    List all question papers
    """
    papers_dict = storage.list_items(QUESTION_PAPERS_STORE)
    logger.info(f"Listing question papers - found {len(papers_dict)} papers in storage")
    return [QuestionPaper(**paper) for paper in papers_dict.values()]


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_paper(paper_id: str):
    """
    Delete a question paper
    """
    paper_dict = storage.get_item(QUESTION_PAPERS_STORE, paper_id)
    if not paper_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question paper with ID {paper_id} not found"
        )
    
    storage.delete_item(QUESTION_PAPERS_STORE, paper_id)
    logger.info(f"✓ Deleted question paper: {paper_id}")
    return None


@router.get("/{paper_id}/pdf")
async def download_question_paper_pdf(
    paper_id: str,
    include_answers: bool = Query(None, description="Include answers in PDF (overrides generation rules)")
):
    """
    Download question paper as PDF
    
    Args:
        paper_id: ID of the question paper
        include_answers: Optional override to include/exclude answers
        
    Returns:
        PDF file as streaming response
    """
    try:
        # Get question paper
        paper_dict = storage.get_item(QUESTION_PAPERS_STORE, paper_id)
        if not paper_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question paper with ID {paper_id} not found"
            )
        
        question_paper = QuestionPaper(**paper_dict)
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_buffer = pdf_generator.generate_pdf(question_paper, include_answers)
        
        # Create filename
        safe_course_name = "".join(c for c in question_paper.course_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_course_name = safe_course_name.replace(' ', '_')
        filename = f"{safe_course_name}_{paper_id}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for question paper {paper_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/{paper_id}/answer-key", response_model=AnswerKey)
async def get_answer_key(paper_id: str):
    """
    Get the answer key for a question paper
    """
    try:
        # Get question paper
        paper_dict = storage.get_item(QUESTION_PAPERS_STORE, paper_id)
        if not paper_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question paper with ID {paper_id} not found"
            )
        
        question_paper = QuestionPaper(**paper_dict)
        
        # Transform questions into answer key items
        answers = []
        for i, question in enumerate(question_paper.questions, 1):
            answers.append(AnswerKeyItem(
                question_id=question.id,
                question_number=i,
                question_text=question.question_text,
                type=question.type,
                marks=question.marks,
                correct_answer=question.correct_answer or "Not available",
                explanation=question.answer_explanation
            ))
            
        # Create answer key
        answer_key = AnswerKey(
            paper_id=question_paper.id,
            course_name=question_paper.course_name,
            total_marks=question_paper.total_marks,
            generated_at=question_paper.generated_at,
            answers=answers
        )
        
        logger.info(f"Answer key retrieved for paper: {paper_id}")
        return answer_key
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving answer key for {paper_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve answer key: {str(e)}"
        )
