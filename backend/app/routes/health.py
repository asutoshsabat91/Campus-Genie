"""
CampusGenie — Health Check Route
Returns status of all dependent services.
GET /api/health
"""

import logging
import httpx
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

SERVICE_TIMEOUT = 3.0


async def _ping_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=SERVICE_TIMEOUT) as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags")
            return "up" if r.status_code == 200 else "degraded"
    except Exception:
        return "down"


async def _ping_chromadb() -> str:
    try:
        async with httpx.AsyncClient(timeout=SERVICE_TIMEOUT) as client:
            # Try v1 API first for older ChromaDB versions
            r = await client.get(
                f"http://{settings.chroma_host}:{settings.chroma_port}/api/v1/heartbeat"
            )
            if r.status_code == 200:
                return "up"
            # Fallback to root endpoint
            r = await client.get(f"http://{settings.chroma_host}:{settings.chroma_port}/")
            return "up" if r.status_code == 200 else "degraded"
    except Exception:
        return "down"


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check availability of all backend services.
    Returns overall status and per-service breakdown.

    Status values: healthy | degraded | unreachable
    """
    services = {
        "backend":  "up",
        "ollama":   await _ping_ollama(),
        "chromadb": await _ping_chromadb(),
    }

    all_up = all(v == "up" for v in services.values())
    any_down = any(v == "down" for v in services.values())

    if all_up:
        overall = "healthy"
    elif any_down:
        overall = "degraded"
    else:
        overall = "degraded"

    logger.debug(f"Health check: {overall} — {services}")
    return HealthResponse(status=overall, services=services)
