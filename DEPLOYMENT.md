# ResearchMind AI - Deployment Guide

## Quick Start (Local Development)

### 1. Setup Environment
```bash
# Navigate to project
cd researchmind-ai

# Copy and configure .env
cp backend/.env.example backend/.env

# Edit .env with your API keys:
# - GEMINI_API_KEY (get from https://ai.google.dev)
# - QDRANT_URL & QDRANT_API_KEY (get from https://cloud.qdrant.io)
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Locally
```bash
python -m uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

## Docker Deployment

### Build & Run
```bash
docker-compose up -d
```

Server runs at: `http://localhost:8000`

View logs:
```bash
docker-compose logs -f backend
```

## Production Deployment (Cloud)

### Option 1: Render.com
1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy

### Option 2: Railway
1. Connect GitHub repo
2. Set env variables
3. Deploy

### Option 3: AWS/GCP/Azure
Build and push Docker image:
```bash
docker build -t researchmind-ai .
docker tag researchmind-ai:latest your-registry/researchmind-ai:latest
docker push your-registry/researchmind-ai:latest
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@document.pdf"
```

### Ask Question (Streaming)
```bash
curl -X POST http://localhost:8000/api/v1/questions/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is X?", "top_k": 5}'
```

### Ask Question (Simple)
```bash
curl -X POST http://localhost:8000/api/v1/questions/ask/simple \
  -H "Content-Type: application/json" \
  -d '{"query": "What is X?", "top_k": 5}'
```

## Frontend Integration

### Setup CORS
Backend allows `localhost:3000` and `localhost:5173` by default.

For custom origins, edit `backend/app/main.py`:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### Example Frontend Call (React)
```javascript
// Upload document
const formData = new FormData();
formData.append('file', pdfFile);

const uploadRes = await fetch('http://localhost:8000/api/v1/documents/upload', {
  method: 'POST',
  body: formData
});

// Ask question (streaming)
const response = await fetch('http://localhost:8000/api/v1/questions/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Your question here', top_k: 5 })
});

const reader = response.body.getReader();
while(true) {
  const {done, value} = await reader.read();
  if (done) break;
  
  const text = new TextDecoder().decode(value);
  const events = text.split('\n').filter(e => e);
  
  for (const event of events) {
    const data = JSON.parse(event);
    if (data.type === 'token') {
      console.log(data.data); // Add to UI
    }
  }
}
```

## Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### API Not Responding
```bash
# Check health
curl http://localhost:8000/health

# Check logs
docker-compose logs backend
```

### Vector DB Connection Failed
- Verify QDRANT_URL and QDRANT_API_KEY in .env
- Check Qdrant Cloud dashboard for API key validity

## Performance Notes

- First embedding request downloads model (~200MB) - takes ~30 seconds
- Subsequent requests use cached model
- Streaming responses show tokens in real-time (like Perplexity/ChatGPT)
- Max file size: 50MB by default (configurable)

## Next Steps

1. ✅ Backend running locally
2. → Setup frontend (React/Vue/Svelte)
3. → Connect frontend to backend APIs
4. → Deploy to production
