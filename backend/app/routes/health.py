"""Health check route."""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
import httpx
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    services = {}

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            services["ollama"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        services["ollama"] = "down"

    # Check ChromaDB
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(
                f"http://{settings.chroma_host}:{settings.chroma_port}/api/v1/heartbeat"
            )
            services["chromadb"] = "up" if r.status_code == 200 else "degraded"
    except Exception:
        services["chromadb"] = "down"

    services["backend"] = "up"

    overall = "healthy" if all(v == "up" for v in services.values()) else "degraded"
    return HealthResponse(status=overall, services=services)
