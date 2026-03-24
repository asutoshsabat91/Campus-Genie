# CampusGenie

CampusGenie is a Retrieval-Augmented Generation (RAG) based AI assistant that enables students and faculty to query campus documents through a conversational interface. Instead of manually searching through PDFs, users can ask natural language questions and receive accurate, citation-backed answers sourced directly from the uploaded documents.

The system is fully containerized using Docker and Docker Compose, making it straightforward to deploy on any machine without environment configuration overhead.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [RAG Pipeline](#rag-pipeline)
- [University Project Context](#university-project-context)
- [Author](#author)
- [License](#license)

---

## Overview

Students commonly spend significant time searching through syllabus PDFs, subject notes, lab manuals, timetables, and institutional rule documents. CampusGenie addresses this by providing a unified chat interface over all uploaded campus documents.

The core design principle is accuracy over convenience — the system is explicitly constrained to answer only from the documents provided. If a question cannot be answered from the available content, the system responds with "Not found in uploaded documents" rather than generating a speculative answer. This behaviour is enforced at the prompt level and is a deliberate architectural decision.

---

## Features

- **RAG-based question answering** — Answers are grounded in retrieved document chunks, not generated from model weights alone.
- **Citation output** — Every response includes the source document name and page number so users can verify the answer.
- **Hallucination prevention** — The LLM is instructed to respond only from provided context. Out-of-scope questions are explicitly rejected.
- **Document filtering** — Users can restrict queries to one or more specific documents rather than searching across everything.
- **Multi-document support** — Multiple PDFs can be uploaded and indexed simultaneously.
- **Chat history** — Conversation context is maintained across turns within a session.
- **One-command deployment** — The entire stack (backend, frontend, vector database, LLM) runs via `docker compose up`.

---

## Architecture

```
                        ┌─────────────────────────────────────────┐
                        │              CampusGenie                 │
                        │                                          │
  User (Browser)        │   ┌──────────┐       ┌──────────────┐   │
       │                │   │Streamlit │       │   FastAPI    │   │
       └────────────────┼──▶│  UI      │──────▶│   Backend    │   │
                        │   │:8501     │       │   :8080      │   │
                        │   └──────────┘       └──────┬───────┘   │
                        │                             │           │
                        │              ┌──────────────┼────────┐  │
                        │              │              │        │  │
                        │   ┌──────────▼───┐   ┌──────▼─────┐ │  │
                        │   │   ChromaDB   │   │   Ollama   │ │  │
                        │   │  Vector DB   │   │  (Llama 3) │ │  │
                        │   │   :8000      │   │   :11434   │ │  │
                        │   └──────────────┘   └────────────┘ │  │
                        │                                      │  │
                        └──────────────────────────────────────┘  │
                                                                   │
```

Request flow:

1. User uploads a PDF via the Streamlit UI.
2. The backend extracts text page by page using PyMuPDF.
3. Text is split into overlapping chunks and embedded using `sentence-transformers`.
4. Embeddings are stored in ChromaDB with page-level metadata.
5. When a question is asked, the query is embedded and the top-k most similar chunks are retrieved.
6. Retrieved chunks and the question are passed to the Ollama LLM (Llama 3) with a strict system prompt.
7. The response is returned to the UI along with source citations.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Ollama (Llama 3) | Local language model inference |
| RAG Framework | LangChain | Pipeline orchestration |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Semantic vector generation |
| Vector Database | ChromaDB | Embedding storage and similarity search |
| PDF Processing | PyMuPDF (fitz) | Text and metadata extraction from PDFs |
| Backend API | FastAPI | REST API with async request handling |
| Frontend | Streamlit | Chat and document management UI |
| Containerization | Docker + Docker Compose | Multi-service deployment |

---

## Project Structure

```
Campus-Genie/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── config.py             # Settings loaded from environment
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic request/response schemas
│   │   ├── rag/
│   │   │   ├── pdf_processor.py  # PDF text extraction (PyMuPDF)
│   │   │   ├── chunker.py        # Word-based sliding window chunker
│   │   │   ├── embeddings.py     # Sentence-transformer embedding engine
│   │   │   ├── vector_store.py   # ChromaDB client wrapper
│   │   │   ├── llm_client.py     # Ollama LLM client
│   │   │   ├── indexer.py        # Document indexing coordinator
│   │   │   └── pipeline.py       # RAG pipeline orchestrator
│   │   └── routes/
│   │       ├── documents.py      # Upload, list, delete endpoints
│   │       ├── chat.py           # Question answering endpoint
│   │       └── health.py         # Service health check endpoint
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py                    # Streamlit application
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml            # Service orchestration
├── .env.example                  # Environment variable reference
└── README.md
```

---

## Prerequisites

- Docker >= 24.0
- Docker Compose >= 2.0
- 8 GB RAM minimum (16 GB recommended for running Llama 3 locally)
- 10 GB free disk space (for the Llama 3 model)

---

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/asutoshsabat91/Campus-Genie.git
cd Campus-Genie
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` if needed. The defaults work out of the box for local Docker deployment.

**3. Start all services**

```bash
docker compose up --build
```

This starts four containers: `backend`, `frontend`, `chromadb`, and `ollama`.

**4. Pull the language model**

On first run, pull Llama 3 into the Ollama container:

```bash
docker exec -it campusgenie-ollama ollama pull llama3
```

This downloads approximately 4.7 GB. Run it once; subsequent starts use the cached model.

**5. Open the application**

```
http://localhost:8501
```

Upload a PDF using the sidebar, then start asking questions.

---

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3` | Model name to use for generation |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama service URL |
| `CHROMA_HOST` | `chromadb` | ChromaDB service hostname |
| `CHROMA_PORT` | `8000` | ChromaDB service port |
| `CHROMA_COLLECTION` | `campus_docs` | Collection name for document embeddings |
| `CHUNK_SIZE` | `500` | Target word count per chunk |
| `CHUNK_OVERLAP` | `50` | Word overlap between consecutive chunks |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum PDF upload size |
| `RETRIEVAL_TOP_K` | `5` | Number of chunks retrieved per query |

---

## API Reference

The backend exposes a REST API at `http://localhost:8080`.

Interactive documentation is available at `http://localhost:8080/docs`.

**Documents**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/documents/upload` | Upload and index a PDF |
| GET | `/api/documents/` | List all indexed documents |
| DELETE | `/api/documents/{doc_id}` | Delete a document and its chunks |

**Chat**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/ask` | Submit a question, receive answer with citations |
| GET | `/api/chat/status` | Check LLM availability and document count |

**Health**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Returns status of all dependent services |

---

## RAG Pipeline

The pipeline has two phases:

**Indexing (on PDF upload)**

```
PDF file
  -> PDFProcessor     : extract text per page using PyMuPDF
  -> TextChunker      : sliding window word-based chunks (size=500, overlap=50)
  -> EmbeddingEngine  : generate vectors via sentence-transformers
  -> VectorStore      : persist vectors + metadata in ChromaDB
```

**Querying (on user question)**

```
User question
  -> EmbeddingEngine  : embed question into query vector
  -> VectorStore      : retrieve top-k similar chunks
  -> LLMClient        : pass chunks + question to Ollama with system prompt
  -> Response         : answer text + citations (document name, page number, snippet)
```

The system prompt instructs the model to answer strictly from the provided context and explicitly return "Not found in uploaded documents" if the answer is not present. This is the primary mechanism for hallucination prevention.

---

## University Project Context

This project is submitted as part of the **ETT (Emerging Technology Trends)** course.

The two primary technologies demonstrated are:

**1. Retrieval-Augmented Generation (RAG)**

RAG is an architecture that combines information retrieval with language model generation. Rather than relying on a model's parametric knowledge, relevant documents are fetched at query time and provided as context. This approach improves factual accuracy and makes the system auditable — every answer can be traced back to a source.

**2. Docker and Docker Compose**

The application is decomposed into four independent services, each running in its own container. Docker Compose handles service dependencies, networking, and volume management. This makes the project reproducible across machines and reflects real-world deployment practice.

---

## Author

Asutosh Sabat
ETT Course Project

---

## License

MIT License
