# CampusGenie

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

CampusGenie is an advanced Retrieval-Augmented Generation (RAG) powered AI assistant specifically designed to revolutionize how students and faculty interact with institutional documents. By leveraging cutting-edge natural language processing and vector database technology, CampusGenie transforms static PDF documents into dynamic, conversational knowledge bases. The system enables users to ask complex questions in natural language and receive precise, citation-backed answers sourced directly from uploaded campus documents, eliminating the need for manual document searching and significantly enhancing academic productivity.

Built with enterprise-grade architecture principles, CampusGenie combines the power of local large language models with sophisticated document retrieval mechanisms to ensure accuracy, privacy, and verifiability. The system is engineered with a strong emphasis on hallucination prevention, explicitly constraining responses to verified document sources. When information is not available in the uploaded materials, the system transparently communicates this limitation rather than generating speculative content. This commitment to accuracy makes CampusGenie a reliable tool for academic research, administrative queries, and educational support.

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
                        │   │  Vector DB   │   │ (Gemma 2B) │ │  │
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
6. Retrieved chunks and the question are passed to the Ollama LLM (Gemma 2B) with a strict system prompt.
7. The response is returned to the UI along with source citations.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Ollama (Gemma 2B) | Local language model inference optimized for memory efficiency |
| RAG Framework | Direct Ollama Client | Lightweight pipeline orchestration without LangChain overhead |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Semantic vector generation for document similarity |
| Vector Database | ChromaDB 0.5.3 | Embedding storage and similarity search with persistent storage |
| PDF Processing | PyMuPDF (fitz) | High-performance text and metadata extraction from PDFs |
| Backend API | FastAPI | High-performance async REST API with automatic documentation |
| Frontend | Streamlit | Modern web interface with real-time chat and document management |
| Containerization | Docker + Docker Compose | Multi-service deployment with service orchestration |
| UI Theming | Custom CSS + Light Theme | Enhanced visibility and professional user interface |

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
- 4 GB RAM minimum (8 GB recommended for optimal performance)
- 5 GB free disk space (for the Gemma 2B model and document storage)
- Modern web browser for Streamlit interface

**Note**: CampusGenie has been optimized to run efficiently on resource-constrained systems using the lightweight Gemma 2B model instead of larger alternatives.

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

On first run, pull Gemma 2B into the Ollama container:

```bash
docker exec -it campusgenie_ollama ollama pull gemma:2b
```

This downloads approximately 1.7 GB. Run it once; subsequent starts use the cached model. The Gemma 2B model has been optimized for efficient memory usage while maintaining high-quality response generation.

**5. Open the application**

```
http://localhost:8501
```

Upload a PDF using the sidebar, then start asking questions. The system will automatically index your documents and provide citation-backed answers.

---

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `gemma:2b` | Model name to use for generation (optimized for memory efficiency) |
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
  -> LLMClient        : pass chunks + question to Ollama with optimized prompt
  -> Response         : answer text + citations (document name, page number, snippet)
```

The system prompt has been carefully engineered to balance strict adherence to provided context while maintaining flexibility to extract relevant information. The direct Ollama client implementation eliminates overhead from larger frameworks, resulting in faster response times and reduced memory footprint. This architecture ensures that every answer can be traced back to specific source documents, maintaining academic integrity and verifiability.

---

## Recent Improvements

### Performance Optimization
- **Model Upgrade**: Switched from Llama 3 (8B, 4.6GB) to Gemma 2B (3B, 1.7GB) for optimal memory usage
- **Framework Simplification**: Replaced LangChain with direct Ollama client for reduced overhead
- **Enhanced Prompts**: Improved prompt engineering for better context utilization and response accuracy

### Infrastructure Enhancements
- **Version Alignment**: Synchronized ChromaDB Docker image (0.5.3) with Python client for stability
- **Build Optimization**: Increased pip install timeout and retries for reliable Docker builds
- **UI Improvements**: Enhanced Streamlit theming with light theme for better visibility
- **Error Handling**: Comprehensive error handling and logging throughout the pipeline

### Memory Efficiency
- **Reduced Requirements**: Minimum RAM reduced from 8GB to 4GB
- **Storage Optimization**: Model size reduced from 4.7GB to 1.7GB
- **Resource Management**: Optimized Docker resource allocation for consistent performance

---

## 🚀 Deployment

CampusGenie can be deployed on modern cloud platforms with full RAG functionality. Both serverless (Vercel) and persistent (Render) options are supported.

### Quick Start
```bash
# Deploy to Vercel (Recommended)
./deploy.sh vercel

# Deploy to Render
./deploy.sh render
```

### Platform Options

| Feature | Vercel | Render |
|---|---|---|
| **Cost** | Free tier available | Free tier available |
| **Performance** | Excellent global CDN | Reliable persistent service |
| **Scaling** | Automatic serverless | Manual scaling |
| **Setup** | One-command deploy | Multiple services setup |
| **Domains** | `.vercel.app` | Custom domains |

### 📋 Detailed Deployment Guide

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions including:
- Step-by-step setup for both platforms
- Environment variable configuration
- Production Docker Compose files
- Troubleshooting common issues
- Security and performance considerations

### 🐳 Docker Images for Production

Pre-built Docker images available:
- `asutoshsabat91/campusgenie-backend:latest`
- `asutoshsabat91/campusgenie-frontend:latest`

### 🔧 Configuration Files

- `vercel.json` - Vercel deployment configuration
- `render.yaml` - Render service definitions
- `docker-compose.cloud.yml` - Production-ready Docker setup
- `deploy.sh` - Automated deployment script

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
