# 🎓 CampusGenie

> **Chat with your college PDFs. Get accurate, citation-based answers. Zero hallucination.**

CampusGenie is a **Dockerized RAG-based AI assistant** built for students and faculty to interact with campus documents — syllabus PDFs, subject notes, lab manuals, exam rules, timetables — through a natural language chat interface.

---

## 🚀 Why CampusGenie?

Students waste hours scrolling through:
- 📄 Syllabus PDFs
- 📚 Subject notes
- 🧪 Lab manuals
- 📋 Rules & regulations
- 🗓️ Timetables

**CampusGenie** turns all of that into a single chat interface.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 RAG-based answers | Retrieval-Augmented Generation — answers only from your documents |
| 📌 Citation-based | Every answer includes source document + page number |
| 🚫 No hallucination | If not in docs, it says "Not found in uploaded documents" |
| 🗂️ Document filtering | Query specific docs or all at once |
| 🐳 Dockerized | One command setup: `docker compose up` |
| 💬 Chat history | Maintains conversation context |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI / RAG** | LangChain + Ollama (Llama 3) |
| **Vector DB** | ChromaDB |
| **PDF Processing** | PyMuPDF (fitz) |
| **Backend API** | FastAPI |
| **Frontend UI** | Streamlit |
| **Containerization** | Docker + Docker Compose |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   CampusGenie                        │
│                                                      │
│  ┌──────────┐    ┌──────────────┐   ┌────────────┐  │
│  │Streamlit │───▶│  FastAPI     │──▶│  ChromaDB  │  │
│  │   UI     │    │  Backend     │   │ Vector DB  │  │
│  └──────────┘    └──────┬───────┘   └────────────┘  │
│                         │                            │
│                  ┌──────▼───────┐                   │
│                  │  Ollama LLM  │                   │
│                  │  (Llama 3)   │                   │
│                  └──────────────┘                   │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

```bash
# Clone the repo
git clone https://github.com/asutoshsabat91/Campus-Genie.git
cd Campus-Genie

# Start all services
docker compose up --build

# Open browser
http://localhost:8501
```

---

## 📁 Project Structure

```
Campus-Genie/
├── backend/              # FastAPI backend + RAG pipeline
│   ├── app/
│   │   ├── main.py       # API routes
│   │   ├── rag/          # RAG pipeline
│   │   └── models/       # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # Streamlit UI
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml    # Orchestrates all services
├── .env.example          # Environment variable template
└── README.md
```

---

## 🎓 University Project

This project is built as part of the **ETT (Emerging Technology Trends)** course at university.

**Technologies demonstrated:**
1. **RAG (Retrieval-Augmented Generation)** — AI answers grounded in real documents
2. **Docker & Docker Compose** — Containerized multi-service deployment

---

## 👨‍💻 Author

**Asutosh Sabat**  
ETT Course Project — CampusGenie

---

## 📜 License

MIT License
