#!/usr/bin/env python3
"""
Create a simple test PDF for CampusGenie testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def create_test_pdf():
    """Create a simple test PDF document"""
    c = canvas.Canvas("test_document.pdf", pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "CampusGenie Test Document")
    
    # Content
    c.setFont("Helvetica", 12)
    text = """
CampusGenie is an educational AI assistant designed to help students with their studies.

Key Features:
1. RAG-powered responses with proper citations
2. Document upload and processing capabilities  
3. Educational chat interface
4. Vector search for relevant information
5. Integration with Ollama language models

How to Use CampusGenie:
- Upload PDF documents about course materials
- Ask questions about the content
- Receive detailed answers with source citations
- Get educational explanations and examples

Technical Architecture:
- Backend: FastAPI with Python
- Frontend: Streamlit interface
- Vector Database: ChromaDB
- Language Model: Ollama with Gemma 2B
- Embeddings: Sentence Transformers

This test document should be successfully indexed and processed by the CampusGenie system.
Students can then ask questions about this content and receive accurate, educational responses.
"""
    
    # Draw text
    lines = text.split('\n')
    y = 700
    for line in lines:
        if line.strip():
            c.drawString(72, y, line.strip())
            y -= 15
    
    c.save()
    print("Test PDF created: test_document.pdf")

if __name__ == "__main__":
    create_test_pdf()
