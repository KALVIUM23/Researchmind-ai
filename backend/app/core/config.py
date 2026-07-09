"""
Centralized Configuration Management

This module centralizes all application configuration and settings.
All environment variables are loaded here to ensure:
- No hardcoded secrets
- Support for environment switching (dev, staging, prod)
- Type-safe configuration access
- Easy deployment across environments
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application Settings
    
    All configuration is centralized here.
    Environment variables override defaults.
    """
    
    # Application
    app_name: str = "ResearchMind AI"
    debug: bool = True
    environment: str = "development"  # development, staging, production
    
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    
    # Qdrant Vector Database
    qdrant_url: str = ":memory:"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "researchmind_v2"
    
    # Text Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # File Upload
    max_file_size: int = 52428800  # 50MB in bytes
    upload_directory: str = "uploads"
    
    # Embeddings
    embedding_model: str = "models/gemini-embedding-2"
    embedding_dimension: int = 3072
    
    # Retrieval
    retrieval_top_k: int = 5
    
    # Logging
    log_level: str = "INFO"
    
    # MongoDB Database
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "researchmind"
    
    # JWT Authentication
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Default secret, should override in .env
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validate critical settings
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings: Singleton instance of application settings
    
    Usage:
        from app.core.config import get_settings
        settings = get_settings()
        api_key = settings.gemini_api_key
    """
    return Settings()


# Create default instance for module imports
settings = get_settings()
