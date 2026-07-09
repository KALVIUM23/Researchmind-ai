"""
ResearchMind AI - Production Backend
Main FastAPI application with proper service lifecycle management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from backend.app.core.config import get_settings
from backend.app.core.logging_config import setup_logging
from backend.app.middleware.cors import setup_cors

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# Global service container
class Services:
    """Holds all initialized services"""
    pass

services = Services()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle: startup and shutdown"""
    
    # ===== STARTUP =====
    logger.info("🚀 ResearchMind AI Starting...")
    try:
        settings = get_settings()
        logger.info(f"Environment: {settings.environment}")
        
        # Import services here to avoid circular imports at startup
        from backend.app.services.parser_service import ParserService
        from backend.app.ingestion.chunking import ChunkingService
        from backend.app.retrieval.embeddings import EmbeddingsService
        from backend.app.retrieval.retrieval import RetrievalService
        from backend.app.services.generation_service import GenerationService
        from backend.app.services.citation_service import CitationService
        from backend.app.services.health_service import HealthService
        from backend.app.vectorstore.qdrant_store import VectorStoreService
        from backend.app.core.database import connect_to_mongo, close_mongo_connection
        
        # Initialize MongoDB
        await connect_to_mongo()
        
        # Initialize services in order
        logger.info("Initializing services pipeline...")
        services.health = HealthService()
        services.parser = ParserService()
        services.chunking = ChunkingService(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        services.embeddings = EmbeddingsService(
            model_name=settings.embedding_model,
            api_key=settings.gemini_api_key
        )
        services.vector_store = VectorStoreService(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection_name,
            embedding_dim=settings.embedding_dimension
        )
        services.retrieval = RetrievalService(
            vector_store=services.vector_store,
            embeddings_service=services.embeddings
        )
        services.generation = GenerationService(
            model_name=settings.gemini_model,
            api_key=settings.gemini_api_key
        )
        services.citation = CitationService()
        
        logger.info("[OK] All services initialized")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info("🛑 ResearchMind AI Shutting down...")
    from backend.app.core.database import close_mongo_connection
    await close_mongo_connection()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    app = FastAPI(
        title="ResearchMind AI",
        description="AI-powered research with semantic search and LLM reasoning",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # ===== CORS Configuration =====
    setup_cors(app)
    
    # ===== Health Check =====
    @app.get("/health")
    async def health_check():
        """API health check endpoint"""
        return services.health.get_health_status()
    
    # ===== Root Endpoint =====
    @app.get("/")
    async def root():
        """API information endpoint"""
        return {
            "name": "ResearchMind AI",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "upload": "/api/v1/documents/upload",
                "ask": "/api/v1/questions/ask",
                "documents": "/api/v1/documents",
            }
        }
    
    # ===== API Routes (v1) =====
    from backend.app.api import documents_api, questions_api, auth_api
    
    app.include_router(auth_api.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(documents_api.router, prefix="/api/v1", tags=["documents"])
    app.include_router(questions_api.router, prefix="/api/v1", tags=["questions"])
    
    # ===== Global Error Handler =====
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc) if settings.debug else "Unknown error"}
        )
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

@app.get("/api/v1/test_models")
async def test_models():
    import google.generativeai as genai
    from backend.app.core.config import settings
    genai.configure(api_key=settings.gemini_api_key)
    try:
        models = [m.name for m in genai.list_models()]
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}
