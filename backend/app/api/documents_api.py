"""
Documents API Routes
Handle PDF upload, document management, summarization, and research notes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
import logging
import time
import os
import uuid

from backend.app.schemas.document import (
    UploadResponse,
    DocumentResponse,
    DocumentSummaryRequest,
    ResearchNotesRequest
)

from fastapi.responses import StreamingResponse
import json
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

# Temporary in-memory state tracking for documents
DOCUMENT_STATES = {}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Upload a PDF document for analysis
    """
    start_time = time.time()
    try:
        from backend.app.main import services
        
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        document_id = str(uuid.uuid4())
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
        file_location = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save file locally first
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
            
        logger.info(f"File saved locally: {file_location}")
        
        DOCUMENT_STATES[document_id] = "Processing"
        
        # Background task function
        def process_document(doc_id: str, file_path: str, filename: str, user_id: str):
            try:
                # 1. Parse PDF
                is_valid, err = services.parser.validate_pdf(file_path)
                if not is_valid:
                    DOCUMENT_STATES[doc_id] = f"Error: {err}"
                    return
                    
                full_text, pages = services.parser.extract_text_with_markers(file_path)
                cleaned_text = services.parser.clean_text(full_text)
                
                # 2. Chunk Text
                chunks = services.chunking.chunk_text(cleaned_text, filename, doc_id)
                
                # 3. Generate Embeddings
                chunk_texts = [c["text"] for c in chunks]
                embeddings = services.embeddings.embed_texts(chunk_texts)
                    
                # 4. Vector Storage
                for chunk in chunks:
                    chunk["metadata"]["user_id"] = user_id
                services.vector_store.add_chunks(chunks, embeddings)
                DOCUMENT_STATES[doc_id] = "Ready"
                logger.info(f"[OK] Document {doc_id} processed successfully in background")
            except Exception as e:
                logger.error(f"Background processing failed for {doc_id}: {e}")
                DOCUMENT_STATES[doc_id] = f"Error: {str(e)}"
        
        background_tasks.add_task(process_document, document_id, file_location, file.filename, current_user["id"])
        
        return {
            "status": "processing",
            "message": "Document uploaded and processing started",
            "document_id": document_id
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/status/{document_id}")
async def get_document_status(document_id: str, current_user: dict = Depends(get_current_user)):
    if document_id not in DOCUMENT_STATES:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "status": DOCUMENT_STATES[document_id]}


@router.post("/summary")
async def generate_summary(request: DocumentSummaryRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a summary of the uploaded document
    """
    start_time = time.time()
    try:
        from backend.app.main import services
        
        # Retrieve chunks for the whole document to summarize
        chunks = services.retrieval.retrieve_context(
            question="summarize the document",
            top_k=20, 
            document_id=request.document_id
        )
        
        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found or no content")
            
        # Setup generator for streaming
        async def response_generator():
            try:
                stream = services.generation.generate_streaming(
                    query=f"Summarize the following text, focusing on the most important points. Make it {request.length}.",
                    context=chunks
                )
                
                async for token in stream:
                    yield json.dumps({"type": "token", "data": token}) + "\n"
                
                yield json.dumps({"type": "done"}) + "\n"
                
                llm_latency = time.time() - start_time
                logger.info(f"Summary streamed in {llm_latency:.2f}s")
                
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
        
    except Exception as e:
        logger.error(f"Summary failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate summary")


@router.post("/research-notes")
async def generate_research_notes(request: ResearchNotesRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate detailed research notes for the document
    """
    start_time = time.time()
    try:
        from backend.app.main import services
        
        query = f"Provide detailed research notes about: {request.topic}" if request.topic else "Provide comprehensive research notes outlining the main arguments, methodologies, findings, and conclusions."
        
        retrieval_start = time.time()
        chunks = services.retrieval.retrieve_context(
            question=query,
            top_k=15,
            document_id=request.document_id
        )
        retrieval_latency = time.time() - retrieval_start
        logger.info(f"Retrieval latency for research notes: {retrieval_latency:.2f}s")
        
        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found or no content matches the topic")
            
        # Build context prompt
        context_prompt = "Context:\n"
        for chunk in chunks:
            context_prompt += f"[Source: {chunk['metadata'].get('source', 'Unknown')}, Page: {chunk['metadata'].get('page', 'Unknown')}]\n{chunk['text']}\n\n"
            
        context_prompt += f"Question: {query}"
        
        llm_start = time.time()
        answer, citations, confidence = services.generation.generate_grounded_answer(query, context_prompt, chunks)
        llm_latency = time.time() - llm_start
        logger.info(f"LLM latency for research notes: {llm_latency:.2f}s")
        
        return {
            "document_id": request.document_id,
            "topic": request.topic,
            "notes": answer,
            "citations": citations,
            "confidence": confidence
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Research notes generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate research notes: {str(e)}")


@router.get("/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """Get list of uploaded documents"""
    # ... placeholder or real implementation ...
    return {"documents": [], "total": 0}

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document"""
    try:
        from backend.app.main import services
        await services.vector_store.delete_by_metadata({"document_id": document_id, "user_id": current_user["id"]})
        return {"status": "success", "message": f"Document {document_id} deleted"}
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Delete failed")
