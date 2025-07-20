import uuid
import fitz
import os
from typing import List, Tuple
from datetime import datetime
from models import Document, DocumentChunk
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, sources_path: str):
        self.sources_path = sources_path
        os.makedirs(sources_path, exist_ok=True)
    
    def process_pdf(self, file_path: str, original_filename: str) -> Document:
        """
        Process a PDF file and return a Document with chunks.
        """
        try:
            doc_id = str(uuid.uuid4())
            
            # Extract text from PDF
            text_content = self._extract_text_from_pdf(file_path)
            
            if not text_content.strip():
                raise ValueError("PDF contains no extractable text")
            
            # Create chunks
            chunks = self._create_chunks(text_content, doc_id)
            
            # Generate summary from first few chunks
            summary = self._generate_summary(chunks[:3])
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            document = Document(
                id=doc_id,
                name=original_filename,
                file_type="pdf",
                file_path=file_path,
                summary=summary,
                chunks=chunks,
                created_at=datetime.now(),
                file_size=file_size
            )
            
            logger.info(f"Successfully processed PDF: {original_filename} -> {len(chunks)} chunks")
            return document
            
        except Exception as e:
            logger.error(f"Error processing PDF {original_filename}: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from PDF using PyMuPDF.
        """
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_content += page.get_text()
                text_content += "\n\n"
            
            doc.close()
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _create_chunks(self, text: str, doc_id: str) -> List[DocumentChunk]:
        """
        Create intelligent chunks from text content.
        Target 500-800 words per chunk with overlap.
        """
        chunks = []
        words = text.split()
        
        if not words:
            return chunks
        
        chunk_size = 600  # Target words per chunk
        overlap_size = 100  # Overlap words between chunks
        
        start_idx = 0
        chunk_index = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + chunk_size, len(words))
            
            chunk_words = words[start_idx:end_idx]
            chunk_content = " ".join(chunk_words)
            
            # Calculate character positions
            start_char = len(" ".join(words[:start_idx]))
            if start_idx > 0:
                start_char += 1  # Account for space
            end_char = start_char + len(chunk_content)
            
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                content=chunk_content,
                chunk_index=chunk_index,
                start_char=start_char,
                end_char=end_char
            )
            
            chunks.append(chunk)
            
            # Move start position with overlap
            if end_idx >= len(words):
                break
            
            start_idx = end_idx - overlap_size
            chunk_index += 1
        
        return chunks
    
    def _generate_summary(self, chunks: List[DocumentChunk]) -> str:
        """
        Generate a simple summary from the first few chunks.
        """
        if not chunks:
            return "No content available"
        
        # Combine first few chunks for summary
        combined_text = " ".join([chunk.content for chunk in chunks])
        
        # Simple extraction of first few sentences
        sentences = combined_text.split('. ')
        summary_sentences = sentences[:3]  # First 3 sentences
        
        summary = '. '.join(summary_sentences)
        if not summary.endswith('.'):
            summary += '.'
        
        # Limit summary length
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary or "Document content extracted successfully"
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to sources directory.
        """
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        safe_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(self.sources_path, safe_filename)
        
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Saved file: {filename} -> {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the sources directory.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate that the file is a readable PDF.
        """
        try:
            doc = fitz.open(file_path)
            is_valid = doc.page_count > 0
            doc.close()
            return is_valid
            
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            return False