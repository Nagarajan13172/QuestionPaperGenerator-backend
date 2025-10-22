"""
Migration script to convert existing uploaded syllabi to persistent storage
This script reads existing uploaded PDFs and migrates them to the new JSON storage system
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.syllabus_parser import SyllabusParser
from app.utils.storage import get_storage
from app.models import Syllabus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_uploaded_files():
    """Migrate existing uploaded PDF files to persistent storage"""
    
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        logger.info("No uploads directory found, nothing to migrate")
        return
    
    storage = get_storage()
    parser = SyllabusParser()
    
    # Get existing syllabi to avoid duplicates
    existing_syllabi = storage.list_items("syllabi")
    existing_ids = set(existing_syllabi.keys())
    
    pdf_files = list(uploads_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in uploads directory")
    
    migrated = 0
    for pdf_file in pdf_files:
        file_id = pdf_file.stem  # Get filename without extension
        syllabus_id = f"syl_{file_id}"
        
        # Skip if already in storage
        if syllabus_id in existing_ids:
            logger.info(f"  ✓ Skipping {pdf_file.name} (already in storage)")
            continue
        
        try:
            logger.info(f"  Processing {pdf_file.name}...")
            
            # Extract text from PDF
            text_content = parser.extract_text_from_pdf(str(pdf_file))
            
            # Parse units
            units = parser.parse_text(text_content)
            
            if not units:
                logger.warning(f"    ⚠ No units found in {pdf_file.name}, skipping")
                continue
            
            # Create syllabus object
            syllabus = Syllabus(
                id=syllabus_id,
                course_name=f"Migrated - {pdf_file.name}",
                content=text_content,
                units=units
            )
            
            # Save to persistent storage
            syllabus_dict = syllabus.model_dump()
            storage.set_item("syllabi", syllabus.id, syllabus_dict)
            
            logger.info(f"    ✓ Migrated {pdf_file.name} with {len(units)} units")
            migrated += 1
            
        except Exception as e:
            logger.error(f"    ✗ Error processing {pdf_file.name}: {e}")
    
    logger.info(f"\n✓ Migration complete! Migrated {migrated} new syllabi")
    
    # Show final count
    final_count = len(storage.list_items("syllabi"))
    logger.info(f"Total syllabi in storage: {final_count}")


def list_stored_syllabi():
    """List all syllabi in persistent storage"""
    storage = get_storage()
    syllabi_dict = storage.list_items("syllabi")
    
    print(f"\n{'='*70}")
    print(f"📚 STORED SYLLABI ({len(syllabi_dict)} total)")
    print(f"{'='*70}\n")
    
    for syl_id, syl_data in syllabi_dict.items():
        print(f"ID: {syl_id}")
        print(f"Course: {syl_data.get('course_name', 'N/A')}")
        print(f"Units: {len(syl_data.get('units', []))}")
        print(f"Created: {syl_data.get('created_at', 'N/A')}")
        print(f"{'-'*70}")


if __name__ == "__main__":
    print("="*70)
    print("🔄 SYLLABUS MIGRATION TOOL")
    print("="*70)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_stored_syllabi()
    else:
        migrate_uploaded_files()
        print()
        list_stored_syllabi()
