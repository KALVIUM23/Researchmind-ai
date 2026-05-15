"""Enhanced Parser Service - Advanced metadata extraction and text processing"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class ParserService:
    """Handle advanced PDF parsing with metadata extraction"""
    
    @staticmethod
    def extract_text_with_markers(file_path: str) -> Tuple[str, int]:
        """
        Extract text from PDF with page markers for tracking
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (full_text_with_markers, page_count)
        """
        try:
            reader = PdfReader(file_path)
            pages_count = len(reader.pages)
            
            full_text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    # Add page marker for tracking in citations
                    full_text += f"\n[PAGE {page_num + 1}]\n{text}\n"
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1}: {str(e)}")
                    full_text += f"\n[PAGE {page_num + 1}]\n[FAILED TO EXTRACT]\n"
            
            logger.info(f"Extracted text from {pages_count} pages")
            return full_text, pages_count
            
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text with normalized whitespace
        """
        try:
            # Split into lines and clean each one
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Strip leading/trailing whitespace
                cleaned_line = line.strip()
                # Skip empty lines but keep page markers
                if cleaned_line or cleaned_line.startswith('[PAGE'):
                    cleaned_lines.append(cleaned_line)
            
            # Join back together
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Remove multiple consecutive newlines
            while '\n\n\n' in cleaned_text:
                cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
            
            logger.info("Text cleaning completed")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            raise
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata (creation date, pages, title, etc.)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with metadata
        """
        try:
            reader = PdfReader(file_path)
            
            # Get document info
            doc_info = reader.metadata or {}
            
            # Get page count
            page_count = len(reader.pages)
            
            # Get file info
            file_stats = Path(file_path).stat()
            file_size = file_stats.st_size
            created_time = datetime.fromtimestamp(file_stats.st_ctime).isoformat()
            
            metadata = {
                "pages": page_count,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "created_time": created_time,
                "title": doc_info.get('/Title', 'Unknown'),
                "author": doc_info.get('/Author', 'Unknown'),
                "subject": doc_info.get('/Subject', 'Unknown'),
                "creator": doc_info.get('/Creator', 'Unknown'),
                "producer": doc_info.get('/Producer', 'Unknown'),
            }
            
            logger.info(f"Extracted metadata: {page_count} pages, {metadata['file_size_mb']}MB")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            # Return basic metadata even if extraction fails
            try:
                file_stats = Path(file_path).stat()
                return {
                    "pages": 0,
                    "file_size": file_stats.st_size,
                    "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                    "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "title": "Unknown",
                    "author": "Unknown",
                    "subject": "Unknown",
                    "creator": "Unknown",
                    "producer": "Unknown",
                }
            except Exception as e2:
                logger.error(f"Failed to extract basic metadata: {str(e2)}")
                raise
    
    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate PDF file integrity
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file exists
            if not Path(file_path).exists():
                return False, "File does not exist"
            
            # Check file is readable
            if not Path(file_path).is_file():
                return False, "Path is not a file"
            
            # Try to read PDF
            reader = PdfReader(file_path)
            
            # Check if encrypted
            if reader.is_encrypted:
                logger.warning("PDF is encrypted - may have limited extraction")
            
            # Check if has pages
            if len(reader.pages) == 0:
                return False, "PDF has no pages"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"
    
    @staticmethod
    def extract_page_boundaries(text: str) -> Dict[int, Tuple[int, int]]:
        """
        Extract page boundaries from text with page markers
        
        Args:
            text: Text with [PAGE N] markers
            
        Returns:
            Dictionary mapping page number to (start_pos, end_pos) in text
        """
        import re
        
        page_boundaries = {}
        
        # Find all [PAGE N] markers
        for match in re.finditer(r'\[PAGE (\d+)\]', text):
            page_num = int(match.group(1))
            start_pos = match.start()
            page_boundaries[page_num] = start_pos
        
        # Convert to ranges
        page_ranges = {}
        page_nums = sorted(page_boundaries.keys())
        
        for i, page_num in enumerate(page_nums):
            start = page_boundaries[page_num]
            # End is start of next page marker, or end of text
            end = page_boundaries[page_nums[i + 1]] if i + 1 < len(page_nums) else len(text)
            page_ranges[page_num] = (start, end)
        
        logger.info(f"Extracted boundaries for {len(page_ranges)} pages")
        return page_ranges
