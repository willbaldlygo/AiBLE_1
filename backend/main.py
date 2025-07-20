from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

from models import (
    ChatRequest, ChatResponse, DocumentSummary, HealthResponse, 
    ErrorResponse, Document
)
from document_processor import PDFProcessor
from vector_store import VectorStore
from llm_client import ClaudeClient
from document_manager import DocumentManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Able2 PDF Research Assistant",
    description="A PDF-focused research assistant with vector search and Claude AI",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for components
pdf_processor = None
vector_store = None
claude_client = None
document_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global pdf_processor, vector_store, claude_client, document_manager
    
    try:
        # Get configuration from environment
        vector_db_path = os.getenv("VECTOR_DB_PATH", "./data/vectordb")
        sources_path = os.getenv("SOURCES_PATH", "./sources")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        # Initialize components
        pdf_processor = PDFProcessor(sources_path)
        vector_store = VectorStore(vector_db_path)
        claude_client = ClaudeClient(anthropic_api_key)
        
        # Initialize document manager (this will load existing documents)
        document_manager = DocumentManager(sources_path, vector_store, pdf_processor)
        
        # Test Claude connection
        if not claude_client.test_connection():
            logger.warning("Claude API connection test failed")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Able2 PDF Research Assistant API", "status": "running"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check."""
    try:
        vector_health = vector_store.health_check()
        document_count = document_manager.get_document_count()
        
        return HealthResponse(
            status="healthy" if vector_health["status"] == "healthy" else "degraded",
            vector_db_status=vector_health["status"],
            documents_count=document_count,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            vector_db_status="error",
            documents_count=0,
            timestamp=datetime.now()
        )


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 50MB limit"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Save file to sources directory
        file_path = pdf_processor.save_uploaded_file(file_content, file.filename)
        
        try:
            # Validate PDF
            if not pdf_processor.validate_pdf(file_path):
                pdf_processor.delete_file(file_path)
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or corrupted PDF file"
                )
            
            # Process PDF
            document = pdf_processor.process_pdf(file_path, file.filename)
            
            # Add to vector store
            if not vector_store.add_document(document):
                pdf_processor.delete_file(file_path)
                raise HTTPException(
                    status_code=500,
                    detail="Failed to add document to vector store"
                )
            
            # Store document metadata persistently
            if not document_manager.add_document(document):
                pdf_processor.delete_file(file_path)
                vector_store.delete_document(document.id)
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save document metadata"
                )
            
            # Return document summary
            return DocumentSummary(
                id=document.id,
                name=document.name,
                file_type=document.file_type,
                summary=document.summary,
                created_at=document.created_at,
                file_size=document.file_size
            )
            
        except Exception as e:
            # Cleanup on failure
            pdf_processor.delete_file(file_path)
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with uploaded documents."""
    try:
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        # Search for relevant sources
        sources = vector_store.search(
            query=request.question,
            n_results=5,
            document_ids=request.document_ids
        )
        
        if not sources:
            return ChatResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question. Please make sure you have uploaded relevant PDF documents.",
                sources=[],
                timestamp=datetime.now()
            )
        
        # Generate response using Claude
        response = await claude_client.generate_response(request.question, sources)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@app.get("/documents", response_model=List[DocumentSummary])
async def get_documents():
    """Get list of all uploaded documents."""
    try:
        return document_manager.get_all_documents()
        
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and all its data."""
    try:
        # Check if document exists
        document = document_manager.get_document(doc_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        # Delete using document manager (handles all cleanup)
        if document_manager.delete_document(doc_id):
            return {"message": "Document deleted successfully", "document_id": doc_id}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.now()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)