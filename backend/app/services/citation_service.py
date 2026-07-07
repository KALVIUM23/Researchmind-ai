"""Citation Service"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CitationService:
    """Map retrieved chunks to answers and handle citation generation"""

    @staticmethod
    def extract_citations(
        answer: str, 
        chunks: List[Dict[str, Any]],
        dedup_by_page: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract source citations from retrieved chunks.
        Maps the answer to the provided chunks.
        """
        citations = []
        seen = set()
        
        for chunk in chunks:
            source = chunk["metadata"]["source"]
            page = chunk["metadata"]["page"]
            
            # Deduplication
            if dedup_by_page:
                key = (source, page)
            else:
                key = chunk["id"]
            
            if key not in seen:
                citations.append({
                    "source": source,
                    "page": page,
                    "document_id": chunk["metadata"].get("document_id"),
                    "chunk_id": chunk["metadata"].get("chunk_id"),
                    "similarity_score": chunk.get("similarity_score", 0.0),
                    "text_preview": chunk.get("text", "")[:100]
                })
                seen.add(key)
        
        logger.info(f"[OK] Extracted {len(citations)} unique citations")
        return citations
