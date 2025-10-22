"""
Syllabus router - handles syllabus upload and parsing
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
import logging
import os
import uuid
from datetime import datetime

from app.models import (
    Syllabus,
    SyllabusUploadRequest,
    ErrorResponse
)
from app.services.syllabus_parser import SyllabusParser
from app.config import settings
from app.utils.storage import get_storage

logger = logging.getLogger(__name__)
router = APIRouter()

# Storage instance
storage = get_storage()
SYLLABI_STORE = "syllabi"


@router.post("/upload/text", response_model=Syllabus, status_code=status.HTTP_201_CREATED)
async def upload_syllabus_text(request: SyllabusUploadRequest):
    """
    Upload syllabus as plain text
    """
    try:
        logger.info(f"Uploading syllabus for course: {request.course_name}")
        
        # Parse the syllabus
        parser = SyllabusParser()
        units = parser.parse_text(request.content)
        
        # Create syllabus object
        syllabus = Syllabus(
            id=f"syl_{uuid.uuid4().hex[:8]}",
            course_name=request.course_name,
            content=request.content,
            units=units
        )
        
        # Store persistently
        syllabus_dict = syllabus.model_dump()
        storage.set_item(SYLLABI_STORE, syllabus.id, syllabus_dict)
        
        logger.info(f"✓ Syllabus created with ID: {syllabus.id}, Units: {len(units)}")
        logger.info(f"✓ Syllabus saved to persistent storage")
        return syllabus
        
    except Exception as e:
        logger.error(f"Error uploading syllabus: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process syllabus: {str(e)}"
        )


@router.post("/upload/file", response_model=Syllabus, status_code=status.HTTP_201_CREATED)
async def upload_syllabus_file(
    file: UploadFile = File(...),
    course_name: str = Form(...)
):
    """
    Upload syllabus as a file (PDF or TXT)
    """
    try:
        logger.info(f"Uploading file: {file.filename} for course: {course_name}")
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # Save file temporarily
        file_id = uuid.uuid4().hex[:8]
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse based on file type
        parser = SyllabusParser()
        
        if file_ext == ".pdf":
            text_content = parser.extract_text_from_pdf(file_path)
        else:  # .txt
            text_content = content.decode('utf-8')
        
        units = parser.parse_text(text_content)
        
        # Create syllabus object
        syllabus = Syllabus(
            id=f"syl_{file_id}",
            course_name=course_name,
            content=text_content,
            units=units
        )
        
        # Store persistently
        syllabus_dict = syllabus.model_dump()
        storage.set_item(SYLLABI_STORE, syllabus.id, syllabus_dict)
        
        logger.info(f"✓ Syllabus created with ID: {syllabus.id}, Units: {len(units)}")
        logger.info(f"✓ Syllabus saved to persistent storage (file: {file.filename})")
        return syllabus
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


@router.get("/{syllabus_id}", response_model=Syllabus)
async def get_syllabus(syllabus_id: str):
    """
    Get a syllabus by ID
    """
    syllabus_dict = storage.get_item(SYLLABI_STORE, syllabus_id)
    if not syllabus_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus with ID {syllabus_id} not found"
        )
    
    return Syllabus(**syllabus_dict)


@router.get("/", response_model=list[Syllabus])
async def list_syllabi():
    """
    List all syllabi
    """
    syllabi_dict = storage.list_items(SYLLABI_STORE)
    logger.info(f"Listing syllabi - found {len(syllabi_dict)} syllabi in storage")
    return [Syllabus(**syl) for syl in syllabi_dict.values()]


@router.delete("/{syllabus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_syllabus(syllabus_id: str):
    """
    Delete a syllabus
    """
    syllabus_dict = storage.get_item(SYLLABI_STORE, syllabus_id)
    if not syllabus_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Syllabus with ID {syllabus_id} not found"
        )
    
    storage.delete_item(SYLLABI_STORE, syllabus_id)
    logger.info(f"✓ Deleted syllabus: {syllabus_id}")
    return None
