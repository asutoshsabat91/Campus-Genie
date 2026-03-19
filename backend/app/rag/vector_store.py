"""
CampusGenie — ChromaDB Vector Store
Manages storage and retrieval of document embeddings.

ChromaDB is the persistent vector database that powers semantic search.
Each chunk is stored as a vector + metadata for citation-aware retrieval.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional
import logging

from app.rag.chunker import TextChunk
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Wraps ChromaDB for:
      - Storing embedded document chunks
      - Semantic similarity search
      - Document-level filtering
      - Deletion by doc_id
    """

    def __init__(self):
        self._client: Optional[chromadb.HttpClient] = None
        self._collection = None

    def _get_client(self) -> chromadb.HttpClient:
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            logger.info(
                f"Connected to ChromaDB at {settings.chroma_host}:{settings.chroma_port}"
            )
        return self._client

    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Using ChromaDB collection: {settings.chroma_collection}")
        return self._collection

    # ── Write operations ──────────────────────────────────────────────────────

    def add_chunks(self, chunks: list[TextChunk], embeddings: list[list[float]]) -> None:
        """
        Store text chunks with their embeddings in ChromaDB.

        Args:
            chunks:     TextChunk objects with metadata
            embeddings: Pre-computed embedding vectors (one per chunk)
        """
        if not chunks:
            return

        collection = self._get_collection()

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "doc_id": c.doc_id,
                "filename": c.filename,
                "page_number": c.page_number,
            }
            for c in chunks
        ]

        # ChromaDB upsert — safe to re-index the same doc
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(f"Stored {len(chunks)} chunks in ChromaDB")

    def delete_document(self, doc_id: str) -> int:
        """
        Delete all chunks belonging to a document.

        Returns:
            Number of chunks deleted
        """
        collection = self._get_collection()
        results = collection.get(where={"doc_id": doc_id})
        ids_to_delete = results["ids"]

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for doc_id={doc_id}")

        return len(ids_to_delete)

    # ── Read operations ───────────────────────────────────────────────────────

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        doc_filter: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Retrieve the top-k most semantically similar chunks.

        Args:
            query_embedding: Embedding of the user's question
            top_k:           Number of chunks to retrieve
            doc_filter:      Optional list of doc_ids to restrict search

        Returns:
            List of dicts with keys: text, doc_id, filename, page_number, distance
        """
        collection = self._get_collection()

        where_clause = None
        if doc_filter:
            if len(doc_filter) == 1:
                where_clause = {"doc_id": {"$eq": doc_filter[0]}}
            else:
                where_clause = {"doc_id": {"$in": doc_filter}}

        kwargs = dict(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._count()),
            include=["documents", "metadatas", "distances"],
        )
        if where_clause:
            kwargs["where"] = where_clause

        results = collection.query(**kwargs)

        chunks = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": results["documents"][0][i],
                        "doc_id": results["metadatas"][0][i]["doc_id"],
                        "filename": results["metadatas"][0][i]["filename"],
                        "page_number": results["metadatas"][0][i]["page_number"],
                        "distance": results["distances"][0][i],
                    }
                )

        return chunks

    def list_documents(self) -> list[dict]:
        """
        Return unique documents indexed in the vector store.
        """
        collection = self._get_collection()
        results = collection.get(include=["metadatas"])

        seen: dict[str, dict] = {}
        for meta in results["metadatas"]:
            doc_id = meta["doc_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta["filename"],
                    "chunk_count": 0,
                }
            seen[doc_id]["chunk_count"] += 1

        return list(seen.values())

    def document_exists(self, doc_id: str) -> bool:
        """Check if a document is already indexed."""
        collection = self._get_collection()
        results = collection.get(where={"doc_id": doc_id}, limit=1)
        return len(results["ids"]) > 0

    def _count(self) -> int:
        """Total number of chunks in the collection."""
        try:
            return self._get_collection().count()
        except Exception:
            return 0
