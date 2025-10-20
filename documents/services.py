"""
Document processing services for PDF text extraction and chunking.
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple
from django.conf import settings
from .models import Document, Chunk
import logging

logger = logging.getLogger(__name__)


class PDFProcessingService:
    """Service for processing PDF documents."""
    
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    def process_document(self, document: Document) -> bool:
        """
        Process a PDF document: extract text, create chunks.
        
        Args:
            document: Document model instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update status
            document.processing_status = 'processing'
            document.save()
            
            # Extract text from PDF
            text_by_page = self.extract_text_from_pdf(document.file_path)
            
            if not text_by_page:
                document.processing_status = 'failed'
                document.processing_error = 'No text extracted from PDF'
                document.save()
                return False
            
            # Update page count
            document.page_count = len(text_by_page)
            document.save()
            
            # Create chunks
            chunks_created = self.create_chunks(document, text_by_page)
            
            if chunks_created == 0:
                document.processing_status = 'failed'
                document.processing_error = 'No chunks created'
                document.save()
                return False
            
            # Update status to completed
            document.processing_status = 'completed'
            document.save()
            
            logger.info(f"Document {document.id} processed successfully. Created {chunks_created} chunks.")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.save()
            return False
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[int, str]:
        """
        Extract text from PDF file page by page.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary mapping page number to text content
        """
        text_by_page = {}
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(file_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()
                
                # Only store pages with actual text
                if text.strip():
                    text_by_page[page_num + 1] = text.strip()
            
            pdf_document.close()
            
            logger.info(f"Extracted text from {len(text_by_page)} pages in {file_path}")
            return text_by_page
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise
    
    def create_chunks(self, document: Document, text_by_page: Dict[int, str]) -> int:
        """
        Create text chunks from extracted text.
        
        Args:
            document: Document model instance
            text_by_page: Dictionary mapping page number to text
            
        Returns:
            Number of chunks created
        """
        chunks_created = 0
        chunk_global_index = 0  # Global index across all pages
        
        try:
            # Process each page
            for page_num, page_text in text_by_page.items():
                # Split page text into chunks
                page_chunks = self._split_text_into_chunks(page_text)
                
                # Create Chunk records
                for chunk_text in page_chunks:
                    Chunk.objects.create(
                        document=document,
                        chunk_text=chunk_text,
                        page_number=page_num,
                        chunk_index=chunk_global_index,
                        chunk_token_count=len(chunk_text.split()),  # Approximate token count
                        start_char_index=0,  # Can be enhanced later
                        end_char_index=len(chunk_text)
                    )
                    chunks_created += 1
                    chunk_global_index += 1
            
            logger.info(f"Created {chunks_created} chunks for document {document.id}")
            return chunks_created
            
        except Exception as e:
            logger.error(f"Error creating chunks for document {document.id}: {str(e)}")
            raise
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence/word boundary
            if end < text_length:
                # Look for sentence ending (., !, ?) within the last 100 chars
                chunk_end_section = text[max(start, end - 100):end]
                sentence_end = max(
                    chunk_end_section.rfind('. '),
                    chunk_end_section.rfind('! '),
                    chunk_end_section.rfind('? ')
                )
                
                if sentence_end != -1:
                    # Adjust end to sentence boundary
                    end = max(start, end - 100) + sentence_end + 2
                else:
                    # Fall back to word boundary
                    chunk_end_section = text[max(start, end - 50):end]
                    word_end = chunk_end_section.rfind(' ')
                    if word_end != -1:
                        end = max(start, end - 50) + word_end
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Avoid infinite loop
            if start <= 0 or start >= text_length:
                break
        
        return chunks


# Singleton instance
pdf_service = PDFProcessingService()

