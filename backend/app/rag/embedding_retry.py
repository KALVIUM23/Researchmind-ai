"""Embedding Error Handling and Retry Logic"""

import time
from typing import List, Optional, Callable, Any
from functools import wraps
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy options"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class EmbeddingError(Exception):
    """Base exception for embedding errors"""
    pass


class RetryableEmbeddingError(EmbeddingError):
    """Error that can be retried"""
    pass


class NonRetryableEmbeddingError(EmbeddingError):
    """Error that should not be retried"""
    pass


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries
            strategy: Retry strategy (exponential, linear, fixed)
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Add random jitter to delays
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_multiplier ** attempt)
        
        else:
            delay = self.base_delay
        
        # Cap at max_delay
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled
        if self.jitter:
            import random
            # Add up to 20% jitter
            jitter_amount = delay * 0.2 * random.random()
            delay += jitter_amount
        
        return delay


class RetryableEmbeddingService:
    """Wrapper around EmbeddingsService with retry logic"""
    
    def __init__(
        self,
        embedding_service,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize retryable embedding service
        
        Args:
            embedding_service: Base EmbeddingsService instance
            retry_config: Retry configuration
        """
        self.embedding_service = embedding_service
        self.retry_config = retry_config or RetryConfig()
        self.stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "retried": 0,
        }
    
    def embed_text_with_retry(self, text: str) -> Optional[List[float]]:
        """
        Embed single text with retry logic
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if all retries failed
        """
        return self._retry_with_backoff(
            lambda: self.embedding_service.embed_text(text),
            f"embed_text('{text[:50]}...')"
        )
    
    def embed_texts_with_retry(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        Embed multiple texts with retry logic
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings or None for failed items
        """
        result = self._retry_with_backoff(
            lambda: self.embedding_service.embed_texts(texts, batch_size),
            f"embed_texts({len(texts)} texts)"
        )
        
        if result is None:
            # If all retries fail, return None list
            return [None] * len(texts)
        
        return result
    
    def _retry_with_backoff(
        self,
        operation: Callable,
        operation_name: str,
    ) -> Optional[Any]:
        """
        Execute operation with retry logic
        
        Args:
            operation: Callable to retry
            operation_name: Name for logging
            
        Returns:
            Result or None if all retries fail
        """
        self.stats["total_attempts"] += 1
        
        for attempt in range(self.retry_config.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.retry_config.max_retries}: {operation_name}")
                
                result = operation()
                
                self.stats["successful"] += 1
                
                if attempt > 0:
                    self.stats["retried"] += 1
                    logger.info(f"Success after {attempt} retries: {operation_name}")
                
                return result
            
            except NonRetryableEmbeddingError as e:
                logger.error(f"Non-retryable error: {str(e)}")
                self.stats["failed"] += 1
                return None
            
            except (RetryableEmbeddingError, Exception) as e:
                logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                
                # Check if we should retry
                if attempt < self.retry_config.max_retries - 1:
                    delay = self.retry_config.calculate_delay(attempt)
                    logger.info(f"Retrying after {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All retries failed for {operation_name}")
                    self.stats["failed"] += 1
                    return None
        
        return None
    
    def get_stats(self) -> dict:
        """Get retry statistics"""
        successful_rate = (
            self.stats["successful"] / self.stats["total_attempts"] * 100
            if self.stats["total_attempts"] > 0
            else 0
        )
        
        return {
            **self.stats,
            "success_rate_percent": round(successful_rate, 2),
        }
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self.stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "retried": 0,
        }


class BatchEmbeddingWithRetry:
    """Batch embedding processing with retry logic"""
    
    def __init__(
        self,
        embedding_service,
        retry_config: Optional[RetryConfig] = None,
        batch_size: int = 32,
    ):
        """
        Initialize batch embedding with retry
        
        Args:
            embedding_service: Base EmbeddingsService
            retry_config: Retry configuration
            batch_size: Batch size for processing
        """
        self.retryable_service = RetryableEmbeddingService(
            embedding_service,
            retry_config
        )
        self.batch_size = batch_size
        self.stats = {
            "batches_processed": 0,
            "chunks_processed": 0,
            "chunks_failed": 0,
        }
    
    def process_chunks_with_retry(
        self,
        chunks: List[dict]
    ) -> List[dict]:
        """
        Process chunks with retry logic per batch
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of chunks with embeddings
        """
        logger.info(f"Processing {len(chunks)} chunks with retry logic")
        
        # Extract texts
        texts = [chunk.get('text', '') for chunk in chunks]
        
        # Process in batches
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            self.stats["batches_processed"] += 1
            
            logger.debug(f"Batch {self.stats['batches_processed']}: {len(batch)} texts")
            
            batch_embeddings = self.retryable_service.embed_texts_with_retry(batch)
            embeddings.extend(batch_embeddings)
        
        # Add embeddings to chunks
        for idx, chunk in enumerate(chunks):
            if embeddings[idx] is not None:
                chunk['embedding'] = embeddings[idx]
                self.stats["chunks_processed"] += 1
            else:
                chunk['embedding'] = None
                self.stats["chunks_failed"] += 1
        
        logger.info(
            f"Processed {self.stats['chunks_processed']} chunks "
            f"({self.stats['chunks_failed']} failed)"
        )
        
        return chunks
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        return {
            **self.stats,
            "retry_stats": self.retryable_service.get_stats(),
        }
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self.stats = {
            "batches_processed": 0,
            "chunks_processed": 0,
            "chunks_failed": 0,
        }
        self.retryable_service.reset_stats()
