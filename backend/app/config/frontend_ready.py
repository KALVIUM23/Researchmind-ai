"""Phase 9: Frontend Ready Configuration and CORS Setup"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GzipMiddleware
import logging

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI, settings):
    """Configure CORS for frontend integration"""
    
    origins = []
    
    if settings.is_development:
        # Development: Allow localhost variations
        origins = [
            "http://localhost:3000",    # React dev server
            "http://localhost:8000",    # FastAPI docs
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
    else:
        # Production: Configure based on environment
        origins = [
            settings.frontend_url if hasattr(settings, 'frontend_url') else "https://yourdomain.com",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key",
        ],
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,
    )
    
    logger.info(f"✅ CORS configured for origins: {origins}")


def setup_compression(app: FastAPI):
    """Setup GZIP compression for responses"""
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    logger.info("✅ GZIP compression enabled")


def setup_error_handlers(app: FastAPI):
    """Setup custom error handlers"""
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return {
            "error": "Invalid input",
            "detail": str(exc)
        }
    
    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request, exc):
        return {
            "error": "Server error",
            "detail": "An unexpected error occurred"
        }
    
    logger.info("✅ Custom error handlers configured")


def setup_api_documentation(app: FastAPI, settings):
    """Configure automatic API documentation"""
    
    # OpenAPI/Swagger configuration
    app.openapi_tags = [
        {
            "name": "documents",
            "description": "Document upload and management endpoints",
        },
        {
            "name": "queries",
            "description": "Question answering endpoints",
        },
        {
            "name": "health",
            "description": "System health and diagnostics",
        },
    ]
    
    logger.info("✅ API documentation configured")
    logger.info(f"   📚 Swagger UI: http://localhost:{settings.port}/docs")
    logger.info(f"   📚 ReDoc: http://localhost:{settings.port}/redoc")


class FrontendConfig:
    """Configuration constants for frontend integration"""
    
    # API versions
    API_VERSION = "v1"
    BASE_URL = "/api/v1"
    
    # Document upload
    MAX_FILE_SIZE_MB = 50
    ALLOWED_FORMATS = [".pdf", ".txt", ".docx"]
    UPLOAD_TIMEOUT_SECONDS = 300
    
    # Query endpoints
    QUERY_TIMEOUT_SECONDS = 60
    MAX_CONCURRENT_QUERIES = 10
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Polling intervals
    UPLOAD_PROGRESS_POLL_MS = 500
    QUERY_RESULT_POLL_MS = 1000
    
    # Error messages
    ERROR_MESSAGES = {
        "invalid_file": "File format not supported. Allowed: PDF, TXT, DOCX",
        "file_too_large": "File size exceeds maximum limit",
        "upload_failed": "Upload failed. Please try again.",
        "query_failed": "Query processing failed. Please try again.",
        "not_found": "Resource not found",
        "server_error": "Server error occurred. Please contact support.",
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        "file_uploaded": "File uploaded successfully",
        "processing": "Processing your request...",
        "complete": "Operation completed successfully",
    }
    
    @classmethod
    def get_client_config(cls) -> dict:
        """Get configuration object for frontend"""
        return {
            "apiVersion": cls.API_VERSION,
            "baseUrl": cls.BASE_URL,
            "maxFileSize": cls.MAX_FILE_SIZE_MB,
            "allowedFormats": cls.ALLOWED_FORMATS,
            "uploadTimeout": cls.UPLOAD_TIMEOUT_SECONDS,
            "queryTimeout": cls.QUERY_TIMEOUT_SECONDS,
            "errorMessages": cls.ERROR_MESSAGES,
            "successMessages": cls.SUCCESS_MESSAGES,
        }


class DeploymentGuide:
    """Deployment guide and environment setup"""
    
    DOCKER_COMPOSE_DEVELOPMENT = """
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      QDRANT_API_KEY: your_api_key

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: development
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      QDRANT_URL: http://qdrant:6333
    depends_on:
      - qdrant

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
"""
    
    ENVIRONMENT_VARIABLES = {
        "development": {
            "ENVIRONMENT": "development",
            "DEBUG": "True",
            "HOST": "0.0.0.0",
            "PORT": 8000,
            "GEMINI_API_KEY": "${GEMINI_API_KEY}",
            "QDRANT_URL": "http://localhost:6333",
        },
        "production": {
            "ENVIRONMENT": "production",
            "DEBUG": "False",
            "HOST": "0.0.0.0",
            "PORT": 8000,
            "GEMINI_API_KEY": "${GEMINI_API_KEY}",
            "QDRANT_URL": "${QDRANT_CLOUD_URL}",
            "QDRANT_API_KEY": "${QDRANT_API_KEY}",
        }
    }
    
    DEPLOYMENT_STEPS = """
    1. Prerequisites:
       - Docker and Docker Compose
       - Python 3.10+
       - Node.js 18+

    2. Environment Setup:
       - Copy .env.example to .env
       - Fill in GEMINI_API_KEY and Qdrant credentials

    3. Development:
       docker-compose up -d
       python -m uvicorn app.main:app --reload

    4. Production:
       - Set ENVIRONMENT=production in .env
       - Use production-grade database (Qdrant Cloud)
       - Deploy with Gunicorn/Nginx
       - Enable HTTPS with SSL certificate
       - Setup monitoring (e.g., Sentry, New Relic)
    """
