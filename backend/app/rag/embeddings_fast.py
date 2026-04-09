"""
CampusGenie — Fast Embeddings Engine
Lightweight embeddings for better performance.
"""

import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class FastEmbeddingEngine:
    """
    Fast, lightweight embedding engine using pre-computed embeddings.
    """

    def __init__(self):
        self.model_loaded = False
        self.cache = {}

    def _load_model(self):
        """Load model on first use."""
        if not self.model_loaded:
            logger.info("Loading fast embedding model...")
            # Use a much smaller, faster model
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model_loaded = True
                logger.info("Fast embedding model loaded ✓")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                # Fallback to simple embeddings
                self.model = None
                self.model_loaded = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed texts with caching."""
        if not texts:
            return []

        self._load_model()
        
        # Check cache first
        cached_results = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            if text in self.cache:
                cached_results.append((i, self.cache[text]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        if not uncached_texts:
            return [result[1] for result in cached_results]
        
        # Process uncached texts in smaller batches
        batch_size = 4  # Very small batch size
        all_embeddings = []
        
        for i in range(0, len(uncached_texts), batch_size):
            batch = uncached_texts[i:i + batch_size]
            try:
                if self.model:
                    embeddings = self.model.encode(
                        batch,
                        batch_size=2,  # Even smaller
                        show_progress_bar=False,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                    )
                    all_embeddings.extend(embeddings.tolist())
                else:
                    # Fallback: simple hash-based embeddings
                    all_embeddings.extend([self._simple_embedding(text) for text in batch])
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                all_embeddings.extend([[0.0] * 384 for _ in batch])
        
        # Cache results and combine with cached
        final_results = [None] * len(texts)
        
        # Fill cached results
        for idx, embedding in cached_results:
            final_results[idx] = embedding
        
        # Fill new results
        for i, idx in enumerate(uncached_indices):
            embedding = all_embeddings[i]
            final_results[idx] = embedding
            self.cache[texts[idx]] = embedding
        
        return final_results

    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding."""
        # Create a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to 384-dimensional vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if i + 1 < len(hash_hex):
                val = int(hash_hex[i:i+2], 16) / 255.0
                embedding.append(val)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        return embedding[:384]

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        results = self.embed_texts([query])
        return results[0] if results else []

# Singleton instance
_embedding_engine = None

def get_fast_embedding_engine():
    """Get singleton fast embedding engine."""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = FastEmbeddingEngine()
    return _embedding_engine
