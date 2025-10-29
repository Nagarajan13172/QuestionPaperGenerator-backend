"""
PDF Generator service for question papers
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
from typing import List
import logging

from app.models.schemas import QuestionPaper, Question, QuestionType

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF for question papers"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Question style
        self.styles.add(ParagraphStyle(
            name='Question',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Option style
        self.styles.add(ParagraphStyle(
            name='Option',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            leftIndent=20,
            spaceAfter=3,
            fontName='Helvetica'
        ))
        
        # Answer style
        self.styles.add(ParagraphStyle(
            name='Answer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#27ae60'),
            leftIndent=20,
            spaceAfter=6,
            fontName='Helvetica-Oblique'
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='Info',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica'
        ))
    
    def generate_pdf(self, question_paper: QuestionPaper, include_answers: bool = None) -> BytesIO:
        """
        Generate PDF for a question paper
        
        Args:
            question_paper: QuestionPaper object
            include_answers: Override for including answers (uses generation_rules if None)
            
        Returns:
            BytesIO object containing PDF data
        """
        logger.info(f"Generating PDF for question paper: {question_paper.id}")
        
        # Determine if answers should be included
        show_answers = include_answers if include_answers is not None else question_paper.generation_rules.include_answer_key
        
        # Create buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Header
        story.extend(self._build_header(question_paper))
        
        # Instructions
        story.extend(self._build_instructions(question_paper))
        
        # Questions
        story.extend(self._build_questions(question_paper, show_answers))
        
        # Build PDF
        doc.build(story)
        
        # Reset buffer position
        buffer.seek(0)
        
        logger.info(f"✓ PDF generated successfully for {question_paper.id}")
        return buffer
    
    def _build_header(self, question_paper: QuestionPaper) -> List:
        """Build PDF header section"""
        story = []
        
        # Title
        title = Paragraph(question_paper.course_name, self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.1*inch))
        
        # Info table
        info_data = [
            ['Question Paper ID:', question_paper.id],
            ['Total Marks:', str(question_paper.total_marks)],
            ['Total Questions:', str(question_paper.total_questions)],
            ['Generated On:', question_paper.generated_at.strftime('%B %d, %Y at %I:%M %p')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _build_instructions(self, question_paper: QuestionPaper) -> List:
        """Build instructions section"""
        story = []
        
        # Instructions heading
        instructions_title = Paragraph("Instructions:", self.styles['CustomHeading'])
        story.append(instructions_title)
        
        # Instructions list
        instructions = [
            f"This question paper contains {question_paper.total_questions} questions worth {question_paper.total_marks} marks.",
            "Answer all questions in the space provided.",
            "Write clearly and legibly.",
            "Use of calculators/mobile phones is not permitted unless specified."
        ]
        
        for instruction in instructions:
            p = Paragraph(f"• {instruction}", self.styles['Normal'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _build_questions(self, question_paper: QuestionPaper, show_answers: bool) -> List:
        """Build questions section"""
        story = []
        
        # Group questions by type
        questions_by_type = {}
        for question in question_paper.questions:
            q_type = question.type.value
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(question)
        
        # Render each group
        question_number = 1
        for q_type, questions in questions_by_type.items():
            # Section heading
            section_title = self._get_section_title(q_type, len(questions), questions[0].marks)
            heading = Paragraph(section_title, self.styles['CustomHeading'])
            story.append(heading)
            story.append(Spacer(1, 0.1*inch))
            
            # Render questions
            for question in questions:
                story.extend(self._render_question(question, question_number, show_answers))
                question_number += 1
                story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _get_section_title(self, question_type: str, count: int, marks: int) -> str:
        """Get formatted section title"""
        type_names = {
            'multiple_choice': 'Multiple Choice Questions',
            'short_answer': 'Short Answer Questions',
            'descriptive': 'Descriptive Questions',
            'essay': 'Essay Questions',
            'true_false': 'True/False Questions',
            'fill_blank': 'Fill in the Blanks'
        }
        
        type_name = type_names.get(question_type, question_type.replace('_', ' ').title())
        return f"{type_name} ({count} × {marks} marks)"
    
    def _render_question(self, question: Question, number: int, show_answers: bool) -> List:
        """Render a single question"""
        story = []
        
        # Question text with number
        q_text = f"<b>Q{number}.</b> {self._escape_html(question.question_text)} "
        q_text += f"<i>[{question.marks} mark{'s' if question.marks > 1 else ''}]</i>"
        
        # Add unit reference
        q_text += f" <font color='#7f8c8d'>(Unit: {question.unit_name})</font>"
        
        question_para = Paragraph(q_text, self.styles['Question'])
        story.append(question_para)
        
        # Options for MCQ/True-False
        if question.options:
            for option in question.options:
                option_para = Paragraph(self._escape_html(option), self.styles['Option'])
                story.append(option_para)
        
        # Answer (if enabled)
        if show_answers and question.correct_answer:
            answer_text = f"<b>Answer:</b> {self._escape_html(question.correct_answer)}"
            if question.answer_explanation:
                answer_text += f" - {self._escape_html(question.answer_explanation)}"
            
            answer_para = Paragraph(answer_text, self.styles['Answer'])
            story.append(Spacer(1, 0.05*inch))
            story.append(answer_para)
        
        return story
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        
        text = str(text)
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
