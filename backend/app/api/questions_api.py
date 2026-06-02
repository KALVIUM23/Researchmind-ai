"""
Questions API Routes
Handle document Q&A with streaming support (like Perplexity)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json

router = APIRouter(prefix="/questions", tags=["questions"])
logger = logging.getLogger(__name__)


class QuestionRequest(BaseModel):
    """User question about documents"""
    query: str
    document_id: str = None  # Optional: filter to specific document
    top_k: int = 5


class QuestionResponse(BaseModel):
    """Response with streaming support"""
    query: str
    answer: str
    sources: list = []
    status: str


@router.post("/ask", response_class=StreamingResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded documents with streaming response
    
    Mimics Perplexity/Google Studio streaming pattern:
    1. Retrieve relevant chunks from vector DB
    2. Stream answer generation in real-time
    
    Args:
        request: Question query and filters
        
    Returns:
        Server-Sent Events stream of answer chunks
    """
    try:
        from backend.app.main import services
        
        logger.info(f"Processing question: {request.query[:50]}...")
        
        # Retrieve relevant chunks
        chunks = await services.retrieval.retrieve(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id
        )
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Generate streaming response
        async def response_generator():
            """Stream answer tokens as they're generated"""
            try:
                # Get streaming response from LLM
                stream = services.answer_generation.generate_streaming(
                    query=request.query,
                    context=chunks
                )
                
                answer_text = ""
                async for chunk in stream:
                    answer_text += chunk
                    # Yield as JSON events
                    yield json.dumps({"type": "token", "data": chunk}) + "\n"
                
                # Yield sources
                sources = [{"id": c.metadata.get("document_id"), "text": c.page_content[:100]} for c in chunks]
                yield json.dumps({"type": "sources", "data": sources}) + "\n"
                yield json.dumps({"type": "done"}) + "\n"
                
                logger.info(f"✅ Answer generated ({len(answer_text)} chars)")
                
            except Exception as e:
                logger.error(f"Stream error: {str(e)}", exc_info=True)
                yield json.dumps({"type": "error", "data": str(e)}) + "\n"
        
        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")


@router.post("/ask/simple")
async def ask_question_simple(request: QuestionRequest):
    """
    Simple (non-streaming) version of ask endpoint
    Returns complete answer at once
    """
    try:
        from backend.app.main import services
        
        logger.info(f"Processing question (simple): {request.query[:50]}...")
        
        # Retrieve
        chunks = await services.retrieval.retrieve(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id
        )
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Generate answer
        answer = await services.answer_generation.generate(
            query=request.query,
            context=chunks
        )
        
        sources = [{"document_id": c.metadata.get("document_id"), "excerpt": c.page_content[:200]} for c in chunks]
        
        return {
            "query": request.query,
            "answer": answer,
            "sources": sources,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
