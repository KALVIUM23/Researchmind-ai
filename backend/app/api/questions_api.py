"""
Questions API Routes
Handle document Q&A with streaming support
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from backend.app.core.security import get_current_user
import logging
import json
import time

from backend.app.schemas.question import QuestionRequest, QuestionResponse

router = APIRouter(prefix="/questions", tags=["questions"])
logger = logging.getLogger(__name__)

@router.post("/ask", response_class=StreamingResponse)
async def ask_question(request: QuestionRequest, current_user: dict = Depends(get_current_user)):
    """
    Ask a question about uploaded documents with streaming response
    """
    start_time = time.time()
    try:
        from backend.app.main import services
        
        logger.info(f"Processing question: {request.query[:50]}...")
        
        # 1. Retrieve relevant chunks
        retrieval_start = time.time()
        chunks = services.retrieval.retrieve_context(
            question=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            filters={"user_id": current_user["id"]}
        )
        retrieval_latency = time.time() - retrieval_start
        logger.info(f"Retrieval latency: {retrieval_latency:.2f}s")
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # 2. Generate streaming response
        async def response_generator():
            llm_start = time.time()
            try:
                stream = services.generation.generate_streaming(
                    query=request.query,
                    context=chunks
                )
                
                answer_text = ""
                async for chunk in stream:
                    answer_text += chunk
                    yield json.dumps({"type": "token", "data": chunk}) + "\n"
                
                llm_latency = time.time() - llm_start
                logger.info(f"LLM latency: {llm_latency:.2f}s")
                
                # Yield sources
                sources = []
                for c in chunks:
                    sources.append({
                        "id": c["metadata"].get("document_id"), 
                        "text": c["text"][:100],
                        "source": c["metadata"].get("source"),
                        "page": c["metadata"].get("page")
                    })
                yield json.dumps({"type": "sources", "data": sources}) + "\n"
                yield json.dumps({"type": "done"}) + "\n"
                
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


@router.post("/ask/simple", response_model=QuestionResponse)
async def ask_question_simple(request: QuestionRequest, current_user: dict = Depends(get_current_user)):
    """
    Simple (non-streaming) version of ask endpoint
    """
    start_time = time.time()
    try:
        from backend.app.main import services
        
        logger.info(f"Processing question (simple): {request.query[:50]}...")
        
        retrieval_start = time.time()
        chunks = services.retrieval.retrieve_context(
            question=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            filters={"user_id": current_user["id"]}
        )
        retrieval_latency = time.time() - retrieval_start
        logger.info(f"Retrieval latency: {retrieval_latency:.2f}s")
        
        if not chunks:
            raise HTTPException(status_code=404, detail="No relevant documents found")
            
        context_prompt = "Context:\n"
        for chunk in chunks:
            context_prompt += f"[Source: {chunk.metadata.get('source', 'Unknown')}, Page: {chunk.metadata.get('page', 'Unknown')}]\n{chunk.page_content}\n\n"
        
        llm_start = time.time()
        answer, citations, confidence = services.generation.generate_grounded_answer(request.query, context_prompt, chunks)
        llm_latency = time.time() - llm_start
        logger.info(f"LLM latency: {llm_latency:.2f}s")
        
        return {
            "query": request.query,
            "answer": answer,
            "sources": citations,
            "status": "success"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
