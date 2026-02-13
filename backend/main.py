import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader
import openai
import glob

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8001))

openai.api_key = os.getenv("OPENAI_API_KEY", "sk-xxxx")

chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

class ChatRequest(BaseModel):
    question: str
    filter_docs: Optional[List[str]] = None
    role: str
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[dict]

@app.post("/upload")
def upload_document(file: UploadFile = File(...), doc_name: str = Form(...)):
    # Save file
    path = f"uploaded_docs/{doc_name}"
    os.makedirs("uploaded_docs", exist_ok=True)
    with open(path, "wb") as f:
        f.write(file.file.read())
    # Extract text and index
    reader = PdfReader(path)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            chunks.append({"text": text, "page": i+1, "doc": doc_name})
    # Chunking (simple: per page)
    # Embedding
    embeddings = [openai.Embedding.create(input=chunk["text"]) for chunk in chunks]
    # Store in ChromaDB
    collection = chroma_client.get_or_create_collection("campusgenie")
    for chunk, emb in zip(chunks, embeddings):
        collection.add(
            documents=[chunk["text"]],
            metadatas=[{"page": chunk["page"], "doc": chunk["doc"]}],
            embeddings=[emb["data"][0]["embedding"]],
            ids=[f"{chunk['doc']}_p{chunk['page']}"]
        )
    return {"status": "uploaded", "pages": len(chunks)}

@app.get("/docs")
def list_docs():
    files = glob.glob("uploaded_docs/*.pdf")
    docs = [os.path.basename(f) for f in files]
    return {"docs": docs}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    collection = chroma_client.get_or_create_collection("campusgenie")
    # Query embedding
    query_emb = openai.Embedding.create(input=req.question)["data"][0]["embedding"]
    # Filter docs
    filter = {"doc": {"$in": req.filter_docs}} if req.filter_docs else None
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=5,
        where=filter
    )
    if not results["documents"] or not any(results["documents"]):
        return ChatResponse(answer="Not found in uploaded documents.", citations=[])
    context = "\n".join([doc for doc in results["documents"][0]])
    citations = [
        {"doc": meta["doc"], "page": meta["page"], "snippet": doc}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
    # Generation
    prompt = f"Answer ONLY from this context. If not found say 'not found'.\nContext:\n{context}\nQuestion: {req.question}"
    answer = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )["choices"][0]["message"]["content"]
    return ChatResponse(answer=answer, citations=citations)
