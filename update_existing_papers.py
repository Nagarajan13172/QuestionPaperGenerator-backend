"""
Script to update existing question papers with CO and BL values
"""
import json
from pathlib import Path


def determine_co_bl(marks, unit_id=None):
    """Determine CO and BL based on marks and unit"""
    if marks == 1:
        return "CO1", "K1"
    elif marks <= 2:
        return "CO1", "K2"
    elif marks <= 3:
        return "CO2", "K2"
    elif marks <= 5:
        return "CO3", "K3"
    elif marks <= 8:
        return "CO4", "K3"
    else:
        return "CO5", "K4"


def update_question_papers():
    """Update all existing question papers with CO and BL values"""
    storage_file = Path("storage/question_papers.json")
    
    if not storage_file.exists():
        print("No question papers found in storage")
        return
    
    # Load existing data
    with open(storage_file, 'r') as f:
        data = json.load(f)
    
    updated_count = 0
    question_count = 0
    
    # Update each question paper
    for qp_id, qp_data in data.items():
        if 'questions' in qp_data:
            for question in qp_data['questions']:
                # Check if CO and BL already exist
                if 'course_outcome' not in question or 'blooms_level' not in question:
                    # Determine appropriate CO and BL
                    marks = question.get('marks', 1)
                    unit_id = question.get('unit_id', 'unit_1')
                    
                    co, bl = determine_co_bl(marks, unit_id)
                    
                    # Add CO and BL
                    question['course_outcome'] = co
                    question['blooms_level'] = bl
                    
                    question_count += 1
            
            updated_count += 1
            print(f"✓ Updated question paper: {qp_id} ({len(qp_data['questions'])} questions)")
    
    # Save updated data
    with open(storage_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  - Updated {updated_count} question papers")
    print(f"  - Modified {question_count} questions")
    print(f"  - File: {storage_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    print("Updating existing question papers with CO and BL values...")
    print("="*60)
    update_question_papers()
    print("\nDone! Refresh your frontend to see the changes.")
