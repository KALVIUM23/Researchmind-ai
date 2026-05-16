"""Chunk ID and Metadata Management System"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChunkIdentifier:
    """Generates and manages unique chunk IDs"""
    
    @staticmethod
    def generate_chunk_id() -> str:
        """
        Generate unique chunk ID
        
        Returns:
            UUID string for the chunk
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_chunk_hash(text: str, document_id: str, chunk_index: int) -> str:
        """
        Generate consistent hash for chunk (deterministic)
        Useful for deduplication
        
        Args:
            text: Chunk text content
            document_id: Document identifier
            chunk_index: Index of chunk
            
        Returns:
            Hash string
        """
        import hashlib
        
        content = f"{document_id}:{chunk_index}:{text[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class EnhancedChunkMetadata:
    """Enhanced metadata container for chunks with full tracking"""
    
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        source: str,
        page: int,
        chunk_index: int,
        text: str,
        char_start: int = 0,
        char_end: int = 0,
        text_preview: Optional[str] = None
    ):
        """
        Initialize enhanced chunk metadata
        
        Args:
            chunk_id: Unique chunk identifier
            document_id: Parent document ID
            source: Source filename
            page: Page number in document
            chunk_index: Index of chunk in document
            text: Full chunk text content
            char_start: Character position start in full text
            char_end: Character position end in full text
            text_preview: Preview text for UI display
        """
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.source = source
        self.page = page
        self.chunk_index = chunk_index
        self.text = text
        self.char_start = char_start
        self.char_end = char_end
        self.text_preview = text_preview or self._generate_preview(text)
        self.created_at = datetime.now().isoformat()
        self.hash = ChunkIdentifier.generate_chunk_hash(text, document_id, chunk_index)
    
    @staticmethod
    def _generate_preview(text: str, max_length: int = 150) -> str:
        """Generate preview text for UI display"""
        if len(text) <= max_length:
            return text.strip()
        
        # Try to break at word boundary
        preview = text[:max_length]
        last_space = preview.rfind(' ')
        if last_space > max_length - 50:
            preview = text[:last_space]
        
        return preview.strip() + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source": self.source,
            "page": self.page,
            "chunk_index": self.chunk_index,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "text_preview": self.text_preview,
            "created_at": self.created_at,
            "hash": self.hash,
        }
    
    def to_vector_store_payload(self) -> Dict[str, Any]:
        """Convert to format suitable for vector store"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "source": self.source,
            "page": self.page,
            "chunk_index": self.chunk_index,
        }


class ChunkPositionTracker:
    """Track character positions of chunks in original text"""
    
    def __init__(self, text: str):
        """
        Initialize position tracker
        
        Args:
            text: Full document text
        """
        self.text = text
        self.current_position = 0
    
    def record_chunk(self, chunk: str) -> tuple:
        """
        Record chunk and return its start/end positions
        
        Args:
            chunk: Chunk text
            
        Returns:
            Tuple of (start_pos, end_pos)
        """
        # Find chunk in text starting from current position
        start = self.text.find(chunk, self.current_position)
        
        if start == -1:
            # Fallback if exact match not found (due to modifications)
            start = self.current_position
        
        end = start + len(chunk)
        self.current_position = end
        
        return start, end
    
    def get_text_around_chunk(self, start: int, end: int, context_chars: int = 50) -> Dict[str, str]:
        """
        Get text context around chunk
        
        Args:
            start: Chunk start position
            end: Chunk end position
            context_chars: Characters to show before and after
            
        Returns:
            Dictionary with before, chunk, after text
        """
        context_start = max(0, start - context_chars)
        context_end = min(len(self.text), end + context_chars)
        
        before = self.text[context_start:start]
        after = self.text[end:context_end]
        chunk_text = self.text[start:end]
        
        return {
            "before": before,
            "chunk": chunk_text,
            "after": after,
        }


class ChunkQualityAnalyzer:
    """Analyze chunk quality for retrieval optimization"""
    
    @staticmethod
    def analyze_chunk(chunk: str) -> Dict[str, Any]:
        """
        Analyze chunk quality metrics
        
        Args:
            chunk: Chunk text
            
        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "length": len(chunk),
            "word_count": len(chunk.split()),
            "sentence_count": chunk.count('.') + chunk.count('!') + chunk.count('?'),
            "has_headers": any(
                chunk.strip().startswith(f"{'#' * i}") 
                for i in range(1, 7)
            ),
            "has_code": '```' in chunk or '    ' in chunk,  # Indented text or code blocks
            "has_lists": chunk.count('\n-') > 0 or chunk.count('\n*') > 0,
            "readability_score": ChunkQualityAnalyzer._calculate_readability(chunk),
        }
        
        return metrics
    
    @staticmethod
    def _calculate_readability(text: str) -> float:
        """
        Simple readability score (0-100)
        Based on word length and sentence structure
        
        Args:
            text: Text to analyze
            
        Returns:
            Score 0-100
        """
        if not text:
            return 0
        
        words = text.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        # Flesch-Kincaid style scoring (simplified)
        # Lower score = more readable
        score = min(100, max(0, 100 - (avg_word_length * 10)))
        
        return round(score, 1)


class ChunkDeduplicationManager:
    """Detect and manage duplicate or near-duplicate chunks"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        """
        Initialize deduplication manager
        
        Args:
            similarity_threshold: Threshold for considering chunks duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.chunk_hashes: Dict[str, str] = {}  # hash -> chunk_id mapping
    
    def register_chunk(self, chunk_id: str, chunk_hash: str) -> bool:
        """
        Register chunk and check for duplicates
        
        Args:
            chunk_id: Chunk ID
            chunk_hash: Chunk hash
            
        Returns:
            True if unique, False if duplicate
        """
        if chunk_hash in self.chunk_hashes:
            logger.warning(
                f"Duplicate detected: {chunk_id} matches {self.chunk_hashes[chunk_hash]}"
            )
            return False
        
        self.chunk_hashes[chunk_hash] = chunk_id
        return True
    
    def get_duplicate_id(self, chunk_hash: str) -> Optional[str]:
        """Get ID of duplicate chunk if exists"""
        return self.chunk_hashes.get(chunk_hash)
    
    def clear(self):
        """Clear deduplication state"""
        self.chunk_hashes.clear()
