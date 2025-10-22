"""
Configuration management for Question Paper Generator
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Question Paper Generator API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # API Keys
    GEMINI_API_KEY: str
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".txt"]
    UPLOAD_DIR: str = "uploads"
    GENERATED_DIR: str = "generated"
    
    # Gemini Settings
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: Optional[int] = None
    
    # Generation Limits
    MAX_QUESTIONS_PER_REQUEST: int = 100
    GENERATION_TIMEOUT: int = 60  # seconds
    
    # Database (Optional - for future use)
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env.example"
        case_sensitive = True


# Global settings instance
settings = Settings()
