"""
CampusGenie Backend — FastAPI Application Entry Point
ETT Course Project
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import documents, chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 CampusGenie backend starting up...")
    yield
    print("🛑 CampusGenie backend shutting down...")


app = FastAPI(
    title="CampusGenie API",
    description="RAG-based AI assistant for campus documents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "service": "CampusGenie API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
