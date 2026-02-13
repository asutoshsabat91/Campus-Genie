# CampusGenie

CampusGenie is a Dockerized RAG-based AI assistant for campus documents.

## Project Structure

- backend/        # FastAPI backend (RAG pipeline, API)
- frontend/       # Streamlit frontend (upload, chat)
- vectordb/       # ChromaDB vector database
- docker-compose.yml
- .gitignore

## Features
- Citation-based answers (page number, document name)
- No hallucination (answers only from uploaded docs)
- Document filtering
- Role-based access (admin uploads, students query)
- Chat history

## Quick Start

1. Clone the repo
2. Run: `docker compose up`

## Technologies
- FastAPI
- Streamlit
- ChromaDB
- Docker

## Demo Sequence
1. Upload syllabus/notes PDFs
2. Ask questions ("What are COs?", "Attendance criteria?")
3. See answers with citations
4. Ask something not in docs ("Who is CEO of Google?")
5. Get: "Not found in uploaded documents"

## Viva One-liner
CampusGenie is a Dockerized RAG-based AI assistant that allows students to chat with campus PDFs and get accurate citation-based answers without hallucination.
