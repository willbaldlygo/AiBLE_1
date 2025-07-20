from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int


class Document(BaseModel):
    id: str
    name: str
    file_type: str
    file_path: str
    summary: str
    chunks: List[DocumentChunk]
    created_at: datetime
    file_size: int


class ChatRequest(BaseModel):
    question: str
    document_ids: Optional[List[str]] = None


class SourceInfo(BaseModel):
    document_id: str
    document_name: str
    chunk_content: str
    relevance_score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    timestamp: datetime


class DocumentSummary(BaseModel):
    id: str
    name: str
    file_type: str
    summary: str
    created_at: datetime
    file_size: int


class HealthResponse(BaseModel):
    status: str
    vector_db_status: str
    documents_count: int
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime