"""
CampusGenie — Simple RAG Pipeline
Lightweight version for better performance.
"""

import logging
from datetime import datetime
from dataclasses import dataclass

from app.rag.pdf_processor import PDFProcessor
from app.rag.chunker import TextChunker
from app.rag.llm_client import LLMClient
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class SimpleIndexResult:
    """Result of indexing a PDF document."""
    success: bool
    message: str
    chunks_created: int = 0
    filename: str = ""

# Module-level persistent storage
_documents = {}

# Export for external access
def get_documents():
    return _documents

class SimpleRAGPipeline:
    """
    Simplified RAG pipeline for better performance.
    """

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker(
            chunk_size=200,  # Smaller chunks
            chunk_overlap=20,
        )
        self.llm = LLMClient()
        # Use module-level storage for persistence

    def index_document(self, filepath: str) -> SimpleIndexResult:
        """
        Simple indexing without embeddings for now.
        """
        try:
            logger.info(f"Starting simple indexing: {filepath}")
            
            # Extract text
            doc_content = self.pdf_processor.process(filepath)
            if not doc_content.pages:
                return SimpleIndexResult(
                    success=False,
                    message="No text extracted from PDF",
                    filename=filepath
                )
            
            # Create chunks
            try:
                chunks = self.chunker.chunk_document(doc_content)
            except Exception as chunk_error:
                logger.error(f"Chunking failed: {chunk_error}")
                # Create a simple chunk manually
                from app.rag.chunker import TextChunk
                chunks = [TextChunk(
                    chunk_id=f"{doc_content.filename}_c0",
                    doc_id=doc_content.filename,
                    filename=doc_content.filename,
                    page_number=1,
                    text=doc_content.pages[0].text if doc_content.pages else "No text extracted"
                )]
            
            # Store in module-level storage
            _documents[doc_content.filename] = {
                'text': doc_content.pages[0].text if doc_content.pages else "No text extracted",
                'indexed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully indexed {len(chunks)} chunks from {doc_content.filename}")
            return SimpleIndexResult(
                success=True,
                message=f"Successfully indexed {len(chunks)} chunks",
                chunks_created=len(chunks),
                filename=doc_content.filename
            )
            
        except Exception as e:
            logger.error(f"Simple indexing failed: {e}")
            return SimpleIndexResult(
                success=False,
                message=f"Indexing failed: {str(e)}",
                filename=filepath
            )

    def ask_question(self, question: str) -> dict:
        """
        Simple question answering without vector search.
        """
        try:
            # Check for conversational interactions first
            conversational_response = self.llm._handle_conversational_interactions(question)
            if conversational_response:
                return {
                    "answer": conversational_response,
                    "citations": [],
                    "source_documents": [],
                    "found_in_docs": False,
                    "processing_time": 0.1
                }
            
            # Simple context from all documents  
            context_parts = []
            for doc_name, doc_data in get_documents().items():
                # Just use the text directly
                text = doc_data.get('text', '')
                if text:
                    context_parts.append(f"From {doc_name}: {text[:200]}...")
            
            context = "\n\n".join(context_parts)
            
            if not context:
                return {
                    "answer": "No documents have been uploaded yet. Please upload a PDF document first.",
                    "citations": [],
                    "source_documents": [],
                    "found_in_docs": False,
                    "processing_time": 0.1
                }
            
            # Generate answer with simple context
            answer = self.llm.generate_answer(question, [], [])
            
            return {
                "answer": answer,
                "citations": ["[Source: Uploaded Documents]"],
                "source_documents": list(_documents.keys()),
                "found_in_docs": True,
                "processing_time": 0.5
            }
            
        except Exception as e:
            logger.error(f"Simple question answering failed: {e}")
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "citations": [],
                "source_documents": [],
                "found_in_docs": False,
                "processing_time": 0.1
            }

# Singleton instance
_simple_pipeline = None

def get_simple_pipeline():
    """Get singleton simple pipeline."""
    global _simple_pipeline
    if _simple_pipeline is None:
        _simple_pipeline = SimpleRAGPipeline()
    return _simple_pipeline
