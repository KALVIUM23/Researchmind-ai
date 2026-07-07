"""Document Schemas"""

from pydantic import BaseModel
from typing import Optional

class DocumentResponse(BaseModel):
    """Document metadata response"""
    id: str
    filename: str
    status: str
    pages: Optional[int] = None
    chunks: Optional[int] = None

class UploadResponse(BaseModel):
    """Upload response"""
    status: str
    message: str
    document_id: Optional[str] = None

class DocumentSummaryRequest(BaseModel):
    """Request summary for document"""
    document_id: str
    length: Optional[str] = "medium" # short, medium, long
    
class ResearchNotesRequest(BaseModel):
    """Request research notes for document"""
    document_id: str
    topic: Optional[str] = None
