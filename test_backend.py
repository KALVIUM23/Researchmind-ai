#!/usr/bin/env python
"""Test all backend services"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("🧪 BACKEND SERVICE TEST")
print("=" * 60)

# Test imports
print("\n📦 Testing service imports...")
try:
    from backend.app.rag.ingestion import PDFIngestionService
    print("  ✅ PDFIngestionService")
    
    from backend.app.rag.chunking import ChunkingService
    print("  ✅ ChunkingService")
    
    from backend.app.rag.embeddings import EmbeddingsService
    print("  ✅ EmbeddingsService")
    
    from backend.app.vectorstore.qdrant_store import VectorStoreService
    print("  ✅ VectorStoreService")
    
    from backend.app.rag.retrieval import RetrievalService
    print("  ✅ RetrievalService")
    
    from backend.app.rag.answer_generation import AnswerGenerationService
    print("  ✅ AnswerGenerationService")
    
    print("\n✅ All imports successful!")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)

# Test config
print("\n⚙️  Testing configuration...")
try:
    from backend.app.core.config import get_settings
    settings = get_settings()
    print(f"  ✅ Config loaded")
    print(f"     - App: {settings.app_name}")
    print(f"     - Debug: {settings.debug}")
    print(f"     - Environment: {settings.environment}")
    print(f"     - Host: {settings.host}:{settings.port}")
except Exception as e:
    print(f"  ❌ Config error: {e}")
    sys.exit(1)

# Test logging
print("\n📝 Testing logging...")
try:
    from backend.app.core.logging_config import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("✅ Logging configured")
    print("  ✅ Logging setup complete")
except Exception as e:
    print(f"  ❌ Logging error: {e}")
    sys.exit(1)

# Test API routes
print("\n🛣️  Testing API routes...")
try:
    from backend.app.api import documents_api, questions_api
    print("  ✅ documents_api")
    print("  ✅ questions_api")
except Exception as e:
    print(f"  ❌ API route error: {e}")
    sys.exit(1)

# Test FastAPI app creation
print("\n🚀 Testing FastAPI app creation...")
try:
    from backend.app.main import app
    print(f"  ✅ FastAPI app created")
    print(f"     - Title: {app.title}")
    print(f"     - Version: {app.version}")
    print(f"     - Routes: {len(app.routes)}")
except Exception as e:
    print(f"  ❌ App creation error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL BACKEND TESTS PASSED")
print("=" * 60)
print("\nNext: python -m uvicorn backend.app.main:app --reload")
