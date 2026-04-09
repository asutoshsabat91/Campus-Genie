"""
CampusGenie Backend - Minimal Vercel Deployment
FastAPI application optimized for serverless deployment
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    logger.info("CampusGenie backend starting up")
    yield
    logger.info("CampusGenie backend shutting down")

app = FastAPI(
    title="CampusGenie API",
    description="RAG-based AI assistant for campus documents",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "CampusGenie API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CampusGenie API",
        "version": "1.0.0"
    }

@app.post("/api/chat/ask")
async def ask_question(request: dict):
    """Simple chat endpoint for deployment testing."""
    question = request.get("question", "")
    
    # Simple response for testing
    return {
        "answer": f"CampusGenie received your question: {question}. Full RAG functionality requires external ChromaDB and Ollama services.",
        "citations": [],
        "source_documents": [],
        "found_in_docs": False
    }

@app.get("/api/documents")
async def list_documents():
    """List documents endpoint."""
    return {
        "documents": [],
        "message": "Document upload requires ChromaDB service"
    }

@app.post("/api/documents/upload")
async def upload_document():
    """Upload document endpoint."""
    return {
        "message": "Document upload requires ChromaDB service"
    }
