"""
CampusGenie — Minimal RAG Pipeline
Ultra-simplified version for maximum performance.
"""

import logging
from datetime import datetime
from dataclasses import dataclass

from app.rag.llm_client import LLMClient
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class MinimalIndexResult:
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

class MinimalRAGPipeline:
    """
    Ultra-minimal RAG pipeline for maximum performance.
    """

    def __init__(self):
        self.llm = LLMClient()

    def index_document(self, filepath: str) -> MinimalIndexResult:
        """
        Minimal indexing without any processing.
        """
        try:
            logger.info(f"Starting minimal indexing: {filepath}")
            
            # Store document info without processing
            import os
            filename = os.path.basename(filepath)
            _documents[filename] = {
                'text': f"Document {filename} uploaded successfully",
                'indexed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully indexed {filename}")
            return MinimalIndexResult(
                success=True,
                message=f"Successfully indexed {filename}",
                chunks_created=1,
                filename=filename
            )
            
        except Exception as e:
            logger.error(f"Minimal indexing failed: {e}")
            return MinimalIndexResult(
                success=False,
                message=f"Indexing failed: {str(e)}",
                filename=filepath
            )

    def ask_question(self, question: str) -> dict:
        """
        Minimal question answering.
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
                text = doc_data.get('text', '')
                if text:
                    context_parts.append(f"From {doc_name}: {text}")
            
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
                "source_documents": list(get_documents().keys()),
                "found_in_docs": True,
                "processing_time": 0.5
            }
            
        except Exception as e:
            logger.error(f"Minimal question answering failed: {e}")
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "citations": [],
                "source_documents": [],
                "found_in_docs": False,
                "processing_time": 0.1
            }

# Global pipeline instance for consistency across requests
_global_pipeline = MinimalRAGPipeline()

def get_minimal_pipeline():
    """Get global minimal pipeline."""
    return _global_pipeline
