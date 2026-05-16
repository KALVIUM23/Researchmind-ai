"""Embedding Cache and Batch Processing System"""

import hashlib
import pickle
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmbeddingCache(ABC):
    """Abstract base class for embedding caches"""
    
    @abstractmethod
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        pass
    
    @abstractmethod
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache embedding for text"""
        pass
    
    @abstractmethod
    def exists(self, text: str) -> bool:
        """Check if embedding exists in cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached embeddings"""
        pass
    
    @staticmethod
    def _hash_text(text: str) -> str:
        """Generate hash key for text"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]


class MemoryEmbeddingCache(EmbeddingCache):
    """In-memory embedding cache - fast but not persistent"""
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize memory cache
        
        Args:
            max_size: Maximum number of cached embeddings
        """
        self.cache: Dict[str, List[float]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding"""
        key = self._hash_text(text)
        if key in self.cache:
            self.hits += 1
            logger.debug(f"Cache hit for text (total hits: {self.hits})")
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache embedding"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple LRU approximation)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted oldest entry, size: {len(self.cache)}")
        
        key = self._hash_text(text)
        self.cache[key] = embedding
    
    def exists(self, text: str) -> bool:
        """Check if embedding exists"""
        return self._hash_text(text) in self.cache
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "cache_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
        }


class DiskEmbeddingCache(EmbeddingCache):
    """Persistent disk-based embedding cache"""
    
    def __init__(self, cache_dir: str = ".embedding_cache", ttl_hours: int = 24):
        """
        Initialize disk cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live for cached entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Disk cache initialized at {self.cache_dir}")
    
    def _get_cache_path(self, text: str) -> Path:
        """Get file path for cached embedding"""
        key = self._hash_text(text)
        return self.cache_dir / f"{key}.pkl"
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding from disk"""
        cache_path = self._get_cache_path(text)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if file_age > self.ttl:
                cache_path.unlink()
                logger.debug("Cache entry expired, deleted")
                return None
            
            with open(cache_path, 'rb') as f:
                embedding = pickle.load(f)
            logger.debug(f"Loaded embedding from disk cache")
            return embedding
        
        except Exception as e:
            logger.error(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache embedding to disk"""
        cache_path = self._get_cache_path(text)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embedding, f)
            logger.debug(f"Cached embedding to disk")
        except Exception as e:
            logger.error(f"Error writing cache: {str(e)}")
    
    def exists(self, text: str) -> bool:
        """Check if embedding exists in disk cache"""
        cache_path = self._get_cache_path(text)
        
        if not cache_path.exists():
            return False
        
        # Check if expired
        try:
            file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if file_age > self.ttl:
                cache_path.unlink()
                return False
            return True
        except:
            return False
    
    def clear(self) -> None:
        """Clear all cached embeddings"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        logger.info("Disk cache cleared")


class BatchEmbeddingProcessor:
    """Process embeddings in batches with optimization"""
    
    def __init__(
        self,
        embedding_service,
        cache: Optional[EmbeddingCache] = None,
        batch_size: int = 32
    ):
        """
        Initialize batch processor
        
        Args:
            embedding_service: EmbeddingsService instance
            cache: EmbeddingCache instance (optional)
            batch_size: Batch size for processing
        """
        self.embedding_service = embedding_service
        self.cache = cache or MemoryEmbeddingCache()
        self.batch_size = batch_size
        self.processed_count = 0
        self.cached_count = 0
    
    def process_chunks(
        self,
        chunks: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Process chunks and generate embeddings with caching
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            
        Returns:
            List of chunks with added 'embedding' field
        """
        logger.info(f"Processing {len(chunks)} chunks with batch embedding")
        
        # Separate chunks that need embedding from cached ones
        texts_to_embed = []
        text_to_chunk_index = {}  # Map text to chunk indices
        cached_embeddings = {}  # Store cached embeddings
        
        for idx, chunk in enumerate(chunks):
            text = chunk.get('text', '')
            
            # Check cache
            if self.cache.exists(text):
                embedding = self.cache.get(text)
                cached_embeddings[idx] = embedding
                self.cached_count += 1
            else:
                if text not in text_to_chunk_index:
                    text_to_chunk_index[text] = []
                    texts_to_embed.append(text)
                text_to_chunk_index[text].append(idx)
        
        logger.info(
            f"Cache hit: {self.cached_count}, need embedding: {len(texts_to_embed)}"
        )
        
        # Generate embeddings for uncached texts in batches
        new_embeddings = {}
        if texts_to_embed:
            embeddings = self._embed_in_batches(texts_to_embed)
            
            for text, embedding in zip(texts_to_embed, embeddings):
                # Cache the embedding
                self.cache.set(text, embedding)
                
                # Map to all chunk indices with this text
                for chunk_idx in text_to_chunk_index[text]:
                    new_embeddings[chunk_idx] = embedding
                
                self.processed_count += 1
        
        # Add embeddings to chunks
        for idx, chunk in enumerate(chunks):
            if idx in cached_embeddings:
                chunk['embedding'] = cached_embeddings[idx]
            elif idx in new_embeddings:
                chunk['embedding'] = new_embeddings[idx]
            else:
                logger.warning(f"No embedding for chunk {idx}")
                chunk['embedding'] = None
        
        return chunks
    
    def _embed_in_batches(self, texts: List[str]) -> List[List[float]]:
        """
        Embed texts in batches
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            logger.debug(f"Processing batch {i//self.batch_size + 1}: {len(batch)} texts")
            
            try:
                batch_embeddings = self.embedding_service.embed_texts(batch)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error embedding batch: {str(e)}")
                # Add None for failed embeddings
                embeddings.extend([None] * len(batch))
        
        return embeddings
    
    def get_stats(self) -> Dict[str, any]:
        """Get processing statistics"""
        stats = {
            "total_processed": self.processed_count,
            "total_cached": self.cached_count,
        }
        
        if hasattr(self.cache, 'get_stats'):
            stats.update(self.cache.get_stats())
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear cache and reset stats"""
        self.cache.clear()
        self.processed_count = 0
        self.cached_count = 0
        logger.info("Batch processor cache cleared and stats reset")
