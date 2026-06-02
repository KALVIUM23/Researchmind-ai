# ResearchMind AI

AI-powered research tool that extracts insights from PDF documents using semantic search and LLM reasoning.

## Features

- **PDF Analysis**: Upload research papers and documents
- **Semantic Search**: Find relevant sections using AI-powered vector search
- **AI Reasoning**: Get intelligent answers grounded in document content
- **Stream Responses**: Real-time answer generation with Gemini AI

## Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Configure API keys in backend/.env
GEMINI_API_KEY=your_key_here
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key

# Run server
python -m uvicorn backend.app.main:app --reload
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/upload` | POST | Upload PDF document |
| `/api/v1/ask` | POST | Ask question about documents |
| `/api/v1/health` | GET | Health check |

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── api/             # Route handlers
│   ├── rag/             # RAG services
│   ├── core/            # Config & logging
│   └── vectorstore/     # Qdrant integration
├── tests/               # Test suite
├── .env                 # Configuration (secrets)
└── requirements.txt     # Dependencies
```

## Architecture

```
Request → FastAPI Routes → RAG Services → Vector DB + LLM → Response
           ↓
    API Layer (upload, ask, health)
           ↓
    RAG Layer (ingestion, chunking, embedding, retrieval, generation)
           ↓
    Storage Layer (Qdrant vectors)
```

## Environment Setup

See `backend/.env` for all configuration options.

