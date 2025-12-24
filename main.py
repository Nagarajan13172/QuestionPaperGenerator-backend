"""
Main FastAPI application for Question Paper Generator
Entry point - Run with: python main.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.models import HealthResponse
from app.routers import syllabus, question_paper
from app.utils.storage import get_storage
import logging
import os
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered question paper generator using Google Gemini",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Note: Vercel has read-only file system, so we skip directory creation
    # All file operations are done in-memory
    logger.info("Running on serverless platform - using in-memory storage")
    
    # Initialize storage
    storage = get_storage()
    syllabi_count = len(storage.list_items("syllabi"))
    papers_count = len(storage.list_items("question_papers"))
    logger.info(f"📚 Loaded {syllabi_count} syllabi and {papers_count} question papers from persistent storage")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down application")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    storage = get_storage()
    syllabi_count = len(storage.list_items("syllabi"))
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with syllabi count"""
    storage = get_storage()
    syllabi_count = len(storage.list_items("syllabi"))
    papers_count = len(storage.list_items("question_papers"))
    
    logger.info(f"Health check: {syllabi_count} syllabi, {papers_count} question papers")
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


# Include routers
app.include_router(
    syllabus.router,
    prefix="/api/syllabus",
    tags=["Syllabus"]
)

app.include_router(
    question_paper.router,
    prefix="/api/question-paper",
    tags=["Question Paper"]
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted at /static")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )