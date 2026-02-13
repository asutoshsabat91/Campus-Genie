# Problem Statement
Students waste time searching through campus PDFs (syllabus, notes, rules, timetable, question papers) for information. Manual keyword search is inefficient and leads to missed details.

# Objectives
- Build an AI assistant that answers questions only from uploaded campus documents
- Ensure answers are citation-based (page number, document name)
- Prevent hallucination (no info outside uploaded docs)
- Support document filtering and role-based access
- Provide chat history for continuity

# Methodology
- Admin uploads PDFs
- Backend extracts, chunks, embeds, and stores in ChromaDB
- User asks questions via frontend
- Backend retrieves relevant chunks, sends to LLM, returns answer with citations

# Modules
1. Frontend (Streamlit): Upload, chat, filter, history
2. Backend (FastAPI): Upload, RAG pipeline, chat API
3. Vector DB (ChromaDB): Store/retrieve embeddings

# Tools/Tech Used
- FastAPI, Streamlit, ChromaDB, Docker, OpenAI API, PyPDF2

# Results + Screenshots Plan
- Upload PDF
- Ask question, see answer with citations
- Ask unrelated question, see "Not found"

# Future Scope
- Add support for DOCX/PPTX
- Improve chunking (semantic)
- Add user authentication
- Enhance UI (React)
