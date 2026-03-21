"""
CampusGenie — RAG Pipeline
Orchestrates the full Retrieval-Augmented Generation workflow.

Indexing flow (when a PDF is uploaded):
  PDF file → PDFProcessor → pages
           → TextChunker  → chunks
           → EmbeddingEngine → vectors
           → VectorStore (ChromaDB) → stored

Query flow (when a student asks a question):
  Question → EmbeddingEngine → query vector
           → VectorStore.query() → top-k chunks
           → LLMClient.generate_answer() → answer + citations
"""

import logging
from datetime import datetime
from dataclasses import dataclass

from app.rag.pdf_processor import PDFProcessor
from app.rag.chunker import TextChunker
from app.rag.embeddings import get_embedding_engine
from app.rag.vector_store import VectorStore
from app.rag.llm_client import LLMClient
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class IndexResult:
    """Result of indexing a PDF document."""
    doc_id: str
    filename: str
    page_count: int
    chunk_count: int
    indexed_at: datetime


@dataclass
class Citation:
    """A single citation pointing to a source chunk."""
    document: str
    page: int
    snippet: str


@dataclass
class QueryResult:
    """Result of a RAG query."""
    answer: str
    citations: list[Citation]
    source_documents: list[str]
    found_in_docs: bool


class RAGPipeline:
    """
    High-level orchestrator for CampusGenie's RAG system.
    Used by API routes — routes don't touch individual components directly.
    """

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.embedder = get_embedding_engine()
        self.vector_store = VectorStore()
        self.llm = LLMClient()

    # ── Indexing ──────────────────────────────────────────────────────────────

    def index_document(self, filepath: str) -> IndexResult:
        """
        Full indexing pipeline for a PDF file.

        Steps:
          1. Extract text per page (PDFProcessor)
          2. Chunk pages into overlapping text chunks (TextChunker)
          3. Embed chunks into vectors (EmbeddingEngine)
          4. Store vectors + metadata in ChromaDB (VectorStore)

        Args:
            filepath: Absolute path to the uploaded PDF

        Returns:
            IndexResult with doc stats
        """
        logger.info(f"Indexing document: {filepath}")

        # Step 1: Extract text
        doc = self.pdf_processor.process(filepath)
        logger.info(f"Extracted {len(doc.pages)} pages from {doc.filename}")

        # Step 2: Chunk
        chunks = self.chunker.chunk_document(doc)
        logger.info(f"Created {len(chunks)} chunks")

        if not chunks:
            raise ValueError(f"No text could be extracted from {doc.filename}")

        # Step 3: Embed
        embeddings = self.embedder.embed_chunks(chunks)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Step 4: Store
        self.vector_store.add_chunks(chunks, embeddings)
        logger.info(f"Stored chunks in ChromaDB for doc_id={doc.doc_id}")

        return IndexResult(
            doc_id=doc.doc_id,
            filename=doc.filename,
            page_count=doc.page_count,
            chunk_count=len(chunks),
            indexed_at=datetime.utcnow(),
        )

    # ── Querying ──────────────────────────────────────────────────────────────

    def query(
        self,
        question: str,
        document_filter: list[str] | None = None,
        chat_history: list[dict] | None = None,
    ) -> QueryResult:
        """
        Full RAG query pipeline.

        Steps:
          1. Embed the user's question
          2. Retrieve top-k similar chunks from ChromaDB
          3. Pass chunks + question to LLM
          4. Build citations from retrieved chunks

        Args:
            question:        Natural language question
            document_filter: Optional list of doc_ids to restrict search
            chat_history:    Prior conversation for context

        Returns:
            QueryResult with answer + citations
        """
        logger.info(f"RAG query: '{question[:80]}' filter={document_filter}")

        # Step 1: Embed question
        query_vector = self.embedder.embed_query(question)

        # Step 2: Retrieve
        chunks = self.vector_store.query(
            query_embedding=query_vector,
            top_k=settings.retrieval_top_k,
            doc_filter=document_filter,
        )
        logger.info(f"Retrieved {len(chunks)} chunks")

        if not chunks:
            return QueryResult(
                answer="Not found in uploaded documents.",
                citations=[],
                source_documents=[],
                found_in_docs=False,
            )

        # Step 3: Generate answer
        answer = self.llm.generate_answer(
            question=question,
            context_chunks=chunks,
            chat_history=chat_history,
        )

        found = "not found in uploaded documents" not in answer.lower()

        # Step 4: Build citations
        citations = self._build_citations(chunks)
        source_docs = list({c.document for c in citations})

        return QueryResult(
            answer=answer,
            citations=citations,
            source_documents=source_docs,
            found_in_docs=found,
        )

    # ── Document management ───────────────────────────────────────────────────

    def delete_document(self, doc_id: str) -> int:
        return self.vector_store.delete_document(doc_id)

    def list_documents(self) -> list[dict]:
        return self.vector_store.list_documents()

    def document_exists(self, doc_id: str) -> bool:
        return self.vector_store.document_exists(doc_id)

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_citations(chunks: list[dict]) -> list[Citation]:
        """
        Build deduplicated citations from retrieved chunks.
        Groups by (filename, page_number) and takes the first snippet.
        """
        seen: set[tuple] = set()
        citations: list[Citation] = []

        for chunk in chunks:
            key = (chunk["filename"], chunk["page_number"])
            if key not in seen:
                seen.add(key)
                snippet = chunk["text"][:200].replace("\n", " ") + "..."
                citations.append(
                    Citation(
                        document=chunk["filename"],
                        page=chunk["page_number"],
                        snippet=snippet,
                    )
                )

        return citations


# Module-level singleton
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Return the shared RAGPipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
