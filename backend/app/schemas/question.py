"""Question Schemas"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QuestionRequest(BaseModel):
    """User question about documents"""
    query: str
    document_id: Optional[str] = None  # Optional: filter to specific document
    top_k: int = 5

class QuestionResponse(BaseModel):
    """Response with streaming support"""
    query: str
    answer: str
    sources: List[Dict[str, Any]] = []
    status: str
