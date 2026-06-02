"""
Documents API Routes
Handle PDF upload and document management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


class DocumentResponse(BaseModel):
    """Document metadata response"""
    id: str
    filename: str
    status: str
    pages: int = None
    chunks: int = None


class UploadResponse(BaseModel):
    """Upload response"""
    status: str
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document for analysis
    
    Args:
        file: PDF file to upload
        
    Returns:
        Document ID and processing status
    """
    try:
        from backend.app.main import services
        
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Process PDF
        document_id = await services.pdf_ingestion.process_file(file)
        logger.info(f"✅ Document uploaded: {document_id}")
        
        return {
            "status": "success",
            "message": f"Document {document_id} uploaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/")
async def list_documents():
    """Get list of uploaded documents"""
    try:
        from backend.app.main import services
        
        documents = await services.pdf_ingestion.list_documents()
        return {"documents": documents, "total": len(documents)}
    
    except Exception as e:
        logger.error(f"List failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        from backend.app.main import services
        
        await services.vector_store.delete_by_metadata({"document_id": document_id})
        return {"status": "success", "message": f"Document {document_id} deleted"}
    
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Delete failed")
