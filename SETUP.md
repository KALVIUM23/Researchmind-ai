# ResearchMind AI - Production-Ready Backend

## Architecture Overview

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌──────────────────────────┐
│    FastAPI Backend       │
├──────────────────────────┤
│  /health               │ ← Health check
│  /api/v1/documents    │ ← Upload & list PDFs
│  /api/v1/questions    │ ← Streaming Q&A
└──────┬───────────────────┘
       │
   ┌───┴────┬─────────┐
   │        │         │
   ▼        ▼         ▼
 ┌──────┐ ┌─────────┐ ┌──────────────┐
 │ PDF  │ │Embeddings│ │Gemini LLM   │
 │Parse │ │(384-dim) │ │(Generation) │
 └──┬───┘ └────┬────┘ └──────────────┘
    │         │
    └─────┬───┘
          │
          ▼
    ┌──────────────┐
    │Qdrant Cloud  │
    │(Vector DB)   │
    └──────────────┘
```

## Key Features

✅ **Production-Ready**
- Async/await throughout
- Streaming responses (like Perplexity)
- Proper error handling
- CORS configured for UI
- Health checks built-in

✅ **Scalable**
- Docker containerized
- Environment-based configuration
- Cloud-agnostic
- Horizontal scaling ready

✅ **Easy to Deploy**
- 1 command local: `python -m uvicorn app.main:app --reload`
- 1 command Docker: `docker-compose up`
- Works on Render, Railway, AWS, GCP, Azure

✅ **UI-Ready**
- Streaming API for real-time answers
- Simple REST endpoints
- Proper CORS headers
- JSON responses

## File Structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI app (start here)
│   ├── api/
│   │   ├── documents_api.py ← Upload, list, delete
│   │   └── questions_api.py ← Streaming Q&A
│   ├── rag/
│   │   ├── ingestion.py     ← PDF loading
│   │   ├── chunking.py      ← Text splitting
│   │   ├── embeddings.py    ← Vector generation
│   │   ├── retrieval.py     ← Vector search
│   │   └── answer_generation.py ← LLM calls
│   ├── vectorstore/
│   │   └── qdrant_store.py  ← Vector DB
│   └── core/
│       ├── config.py        ← Settings from .env
│       └── logging_config.py
├── .env                     ← Your secrets (DO NOT COMMIT)
├── .env.example            ← Template (commit this)
└── requirements.txt        ← Dependencies
```

## Setup Steps

### Step 1: Clone & Navigate
```bash
git clone https://github.com/KALVIUM23/researchmind-ai.git
cd researchmind-ai
```

### Step 2: Configure Secrets
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add:
```
GEMINI_API_KEY=sk-...
QDRANT_URL=https://...qdrant.io
QDRANT_API_KEY=...
```

### Step 3: Install & Run

**Option A: Local Development**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Option B: Docker**
```bash
docker-compose up
```

### Step 4: Verify
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "ResearchMind AI"}
```

## API Usage

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@research.pdf"
```

### Ask Question (Streaming - like Perplexity)
```bash
curl -N -X POST http://localhost:8000/api/v1/questions/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are key findings?", "top_k": 5}'
```

### Ask Question (Simple)
```bash
curl -X POST http://localhost:8000/api/v1/questions/ask/simple \
  -H "Content-Type: application/json" \
  -d '{"query": "What are key findings?", "top_k": 5}'
```

## Frontend Integration

### React Example
```javascript
// Upload
const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch('http://localhost:8000/api/v1/documents/upload', {
    method: 'POST',
    body: formData
  });
  return await res.json();
};

// Stream answer
const askQuestion = async (query) => {
  const response = await fetch('http://localhost:8000/api/v1/questions/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: 5 })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    
    const text = decoder.decode(value);
    const events = text.split('\n').filter(e => e);
    
    for (const event of events) {
      const data = JSON.parse(event);
      if (data.type === 'token') {
        // Display token as it arrives
        setAnswer(prev => prev + data.data);
      }
    }
  }
};
```

## Deployment

### Render.com (Recommended for Fast Setup)
1. Push to GitHub
2. Go to render.com → New → Web Service
3. Connect GitHub repo
4. Set Environment Variables:
   - `GEMINI_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
5. Deploy!

### Docker (Any Cloud)
```bash
docker build -t myapp .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=xxx \
  -e QDRANT_URL=xxx \
  -e QDRANT_API_KEY=xxx \
  myapp
```

## Performance

- First boot: ~20-30s (downloads embedding model)
- Subsequent requests: <1s warmup
- Document upload: ~2-5s (depends on size)
- Question answering: ~3-10s (depends on LLM)
- Streaming shows tokens in real-time

## Troubleshooting

**"GEMINI_API_KEY is required"**
→ Copy backend/.env.example to backend/.env and add your key

**"Cannot connect to Qdrant"**
→ Verify QDRANT_URL and QDRANT_API_KEY are correct

**Port 8000 already in use**
```bash
# Change port:
python -m uvicorn app.main:app --port 8001 --reload
```

**Module import errors**
```bash
# Reinstall dependencies:
pip install -r requirements.txt --force-reinstall
```

## What's Next

1. ✅ Backend setup and running
2. → Build Frontend (React/Vue/Svelte)
3. → Connect frontend to these APIs
4. → Deploy to production
5. → Add more RAG features (filters, analytics, etc.)

## Support

Check logs:
```bash
docker-compose logs -f backend
```

View API docs:
```
http://localhost:8000/docs
```
