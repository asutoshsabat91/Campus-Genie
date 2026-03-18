"""
CampusGenie — Pydantic Schemas
Request / Response models for the API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Document schemas ─────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteDocumentResponse(BaseModel):
    success: bool
    message: str


# ── Chat schemas ──────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    document_filter: Optional[list[str]] = None  # filter by specific doc filenames
    chat_history: Optional[list[ChatMessage]] = []


class Citation(BaseModel):
    document: str
    page: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    source_documents: list[str]
    found_in_docs: bool


# ── Health schemas ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]
