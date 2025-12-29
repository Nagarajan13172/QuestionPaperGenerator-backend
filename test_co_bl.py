"""
Test script to verify CO and BL columns are included in question paper generation
"""
import asyncio
from app.models.schemas import (
    Syllabus,
    Unit,
    GenerationRules,
    QuestionTypeConfig,
    QuestionType,
    Question,
    QuestionPaper
)
from app.services.pdf_generator import PDFGenerator
from datetime import datetime


def test_pdf_with_co_bl():
    """Test PDF generation with CO and BL columns"""
    
    # Create sample questions with CO and BL
    questions = [
        Question(
            id="q1",
            unit_id="unit1",
            unit_name="Cloud Computing Fundamentals",
            question_text="Describe the type of cloud computing.",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="easy",
            correct_answer="Types include IaaS, PaaS, SaaS",
            answer_explanation="Infrastructure as a Service, Platform as a Service, Software as a Service",
            course_outcome="CO1",
            blooms_level="K1"
        ),
        Question(
            id="q2",
            unit_id="unit1",
            unit_name="Cloud Computing Fundamentals",
            question_text="Difference between cloud computing and distributed computing.",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="medium",
            correct_answer="Cloud computing uses internet-based resources, distributed computing uses multiple computers",
            answer_explanation="Key differences in architecture and resource management",
            course_outcome="CO1",
            blooms_level="K2"
        ),
        Question(
            id="q3",
            unit_id="unit2",
            unit_name="Virtualization",
            question_text="Mention the role of hypervisor to manage virtual machines in a cloud environment.",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="medium",
            correct_answer="Hypervisor manages VM creation, resource allocation, and isolation",
            answer_explanation="Acts as a layer between hardware and VMs",
            course_outcome="CO2",
            blooms_level="K2"
        ),
        Question(
            id="q4",
            unit_id="unit2",
            unit_name="Virtualization",
            question_text="What is meant by hardware virtualization?",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="easy",
            correct_answer="Process of creating virtual versions of hardware resources",
            answer_explanation="Enables multiple OS to run on single physical hardware",
            course_outcome="CO2",
            blooms_level="K1"
        ),
        Question(
            id="q5",
            unit_id="unit3",
            unit_name="Cloud Architecture",
            question_text="List out the implementation methods of desktop virtualization.",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="medium",
            correct_answer="VDI, Session-based, Application virtualization",
            answer_explanation="Various methods to deliver desktop environments",
            course_outcome="CO3",
            blooms_level="K2"
        ),
        Question(
            id="q6",
            unit_id="unit3",
            unit_name="Cloud Architecture",
            question_text="What are virtual clusters in cloud computing, and how is resource management performed?",
            marks=2,
            type=QuestionType.DESCRIPTIVE,
            difficulty="hard",
            correct_answer="Virtual clusters are groups of VMs working together. Resource management involves scheduling, load balancing, and monitoring.",
            answer_explanation="Complex coordination of distributed resources",
            course_outcome="CO3",
            blooms_level="K2"
        ),
        Question(
            id="q7",
            unit_id="unit4",
            unit_name="Cloud Services",
            question_text="How does an open cloud ecosystem support cloud computing?",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="medium",
            correct_answer="Provides interoperability, flexibility, and vendor independence",
            answer_explanation="Enables seamless integration across platforms",
            course_outcome="CO4",
            blooms_level="K2"
        ),
        Question(
            id="q8",
            unit_id="unit4",
            unit_name="Cloud Services",
            question_text="How can AWS services be applied to deploy a web application?",
            marks=2,
            type=QuestionType.DESCRIPTIVE,
            difficulty="hard",
            correct_answer="Use EC2 for compute, S3 for storage, RDS for database, CloudFront for CDN",
            answer_explanation="Complete deployment architecture on AWS",
            course_outcome="CO4",
            blooms_level="K3"
        ),
        Question(
            id="q9",
            unit_id="unit5",
            unit_name="Cloud Security",
            question_text="In what situation might a hyper jacking attack occur in a cloud environment?",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="hard",
            correct_answer="When attacker gains control of hypervisor to compromise VMs",
            answer_explanation="Critical security vulnerability in virtualized environments",
            course_outcome="CO5",
            blooms_level="K3"
        ),
        Question(
            id="q10",
            unit_id="unit5",
            unit_name="Cloud Security",
            question_text="What is IAM in cloud computing and what are its challenges?",
            marks=2,
            type=QuestionType.SHORT_ANSWER,
            difficulty="medium",
            correct_answer="Identity and Access Management. Challenges: complexity, integration, compliance",
            answer_explanation="Critical for security but complex to implement",
            course_outcome="CO5",
            blooms_level="K1"
        ),
    ]
    
    # Create question paper
    question_paper = QuestionPaper(
        id="qp_test_001",
        syllabus_id="syl_001",
        course_name="CCS335 - CLOUD COMPUTING",
        generated_at=datetime.now(),
        total_marks=20,
        total_questions=10,
        questions=questions,
        generation_rules=GenerationRules(
            question_types=[
                QuestionTypeConfig(marks=2, count=10, type=QuestionType.SHORT_ANSWER)
            ],
            include_answer_key=True
        ),
        units_coverage={"unit1": 2, "unit2": 2, "unit3": 2, "unit4": 2, "unit5": 2}
    )
    
    # Generate PDF
    pdf_generator = PDFGenerator()
    pdf_buffer = pdf_generator.generate_pdf(question_paper, include_answers=True)
    
    # Save to file
    output_file = "generated/test_question_paper_with_co_bl.pdf"
    with open(output_file, "wb") as f:
        f.write(pdf_buffer.read())
    
    print(f"✓ Test PDF generated successfully: {output_file}")
    print(f"✓ Generated {len(questions)} questions")
    print(f"✓ Each question includes CO and BL columns")
    print("\nSample question structure:")
    print(f"  - Question 1: CO={questions[0].course_outcome}, BL={questions[0].blooms_level}")
    print(f"  - Question 5: CO={questions[4].course_outcome}, BL={questions[4].blooms_level}")
    print(f"  - Question 10: CO={questions[9].course_outcome}, BL={questions[9].blooms_level}")


if __name__ == "__main__":
    print("Testing CO and BL columns in question paper...")
    print("=" * 60)
    test_pdf_with_co_bl()
    print("=" * 60)
    print("Test completed successfully!")
