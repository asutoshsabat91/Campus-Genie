"""
CampusGenie — Application Settings
Loaded from environment variables / .env file
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama LLM
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "gemma:2b"

    # ChromaDB
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "campus_docs"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8080
    max_upload_size_mb: int = 50

    # RAG pipeline
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 5

    # Upload directory (inside container)
    upload_dir: str = "/app/uploads"

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
