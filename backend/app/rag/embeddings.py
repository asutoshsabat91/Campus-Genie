"""
CampusGenie — Embeddings Engine
Converts text into dense vector representations for semantic search.

Model: sentence-transformers/all-MiniLM-L6-v2
  - 384-dimensional vectors
  - Fast, lightweight, runs on CPU
  - Excellent for semantic similarity tasks
  - No internet required after first download (model cached in Docker image)
"""

import logging
from functools import lru_cache
from typing import Union

logger = logging.getLogger(__name__)

# Model name — centralised so it's easy to swap
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class EmbeddingEngine:
    """
    Lazy-loaded sentence-transformer embedding engine.
    Model is loaded once and reused across requests.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Load the model on first use (lazy init)."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded ✓")
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of text strings.

        Args:
            texts: List of strings to embed

        Returns:
            List of embedding vectors (list of floats)
        """
        if not texts:
            return []

        model = self._load_model()
        embeddings = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,   # L2 normalize for cosine similarity
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """
        Embed a single query string.
        Convenience wrapper around embed_texts.
        """
        results = self.embed_texts([query])
        return results[0] if results else []

    def embed_chunks(self, chunks) -> list[list[float]]:
        """
        Embed a list of TextChunk objects.

        Args:
            chunks: List of TextChunk (from chunker.py)

        Returns:
            Parallel list of embedding vectors
        """
        texts = [chunk.text for chunk in chunks]
        return self.embed_texts(texts)


@lru_cache(maxsize=1)
def get_embedding_engine() -> EmbeddingEngine:
    """
    Singleton embedding engine.
    lru_cache ensures the model is loaded only once per process.
    """
    return EmbeddingEngine()
