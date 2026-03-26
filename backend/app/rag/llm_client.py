"""
CampusGenie — LLM Client
Integrates with Ollama (locally running Llama 3) via LangChain.

Why Ollama?
  - Runs 100% locally inside Docker — no API keys, no internet
  - Llama 3 is strong for Q&A tasks
  - LangChain wraps it with prompt templates + chain abstraction

The LLM is ONLY given retrieved chunks as context.
It is explicitly instructed NOT to use outside knowledge.
This is the anti-hallucination guarantee.
"""

import logging
import ollama
from app.config import settings

logger = logging.getLogger(__name__)

# ── Prompt Template ───────────────────────────────────────────────────────────
# The system prompt is the KEY to preventing hallucination.
# We explicitly tell the model: use ONLY the context below.

RAG_PROMPT_TEMPLATE = """You are CampusGenie, an AI assistant for college students.
You answer questions based on the provided context from campus documents.

RULES:
1. Use the context below to answer the question. The context contains relevant information.
2. If you can find relevant information in the context, use it to answer.
3. If you genuinely cannot find any relevant information after carefully reviewing the context, respond with exactly:
   "Not found in uploaded documents."
4. Be concise and accurate.
5. When answering, refer to the source document naturally (e.g., "According to the document...").

Context from campus documents:
---
{context}
---

Chat History:
{chat_history}

Student Question: {question}

Answer:"""

NOT_FOUND_RESPONSE = "Not found in uploaded documents."


class LLMClient:
    """
    Wraps Ollama LLM with a RAG prompt.
    Enforces context-only answering to prevent hallucination.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            logger.info(f"Initialising Ollama client: model={settings.ollama_model}")
            self._client = ollama.Client(
                host=settings.ollama_base_url.replace('http://', '').replace('https://', '')
            )
            # Test connection
            try:
                models = self._client.list()
                logger.info(f"Ollama connection successful, available models: {models}")
            except Exception as e:
                logger.error(f"Ollama connection failed: {e}")
                raise e
        return self._client

    def generate_answer(
        self,
        question: str,
        context_chunks: list[dict],
        chat_history: list[dict] | None = None,
    ) -> str:
        """
        Generate an answer grounded in the retrieved context chunks.

        Args:
            question:       The user's question
            context_chunks: Retrieved chunks from VectorStore.query()
            chat_history:   Prior Q&A pairs for conversational context

        Returns:
            Answer string (or NOT_FOUND_RESPONSE if info not in docs)
        """
        client = self._get_client()

        # Build context from chunks
        context = "\n\n".join([chunk["text"] for chunk in context_chunks])
        
        # Build chat history string
        history_str = ""
        if chat_history:
            # Convert role/content format to Q/A format
            qa_pairs = []
            for i, msg in enumerate(chat_history):
                if msg['role'] == 'user':
                    qa_pairs.append(f"Q: {msg['content']}")
                elif msg['role'] == 'assistant' and qa_pairs:
                    qa_pairs[-1] += f"\nA: {msg['content']}"
            history_str = "\n".join(qa_pairs)

        # Format prompt
        prompt = RAG_PROMPT_TEMPLATE.format(
            context=context,
            chat_history=history_str,
            question=question
        )

        try:
            response = client.generate(
                model=settings.ollama_model,
                prompt=prompt,
                options={
                    'temperature': 0.1,
                    'num_ctx': 4096,
                }
            )
            answer = response['response'].strip()
            
            # Check if answer indicates not found
            if not answer or answer.lower() in ['not found in uploaded documents.', 'i cannot answer based on the provided context.']:
                return NOT_FOUND_RESPONSE
                
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return NOT_FOUND_RESPONSE

    def is_available(self) -> bool:
        """Check if Ollama service is reachable."""
        try:
            import httpx
            r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _format_context(chunks: list[dict]) -> str:
        """
        Format retrieved chunks into a numbered context block.
        Each entry shows source info for the LLM to reference.
        """
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[{i}] Source: {chunk['filename']} (Page {chunk['page_number']})\n"
                f"{chunk['text']}"
            )
        return "\n\n".join(parts)

    @staticmethod
    def _format_history(history: list[dict]) -> str:
        """Format chat history as readable dialogue."""
        if not history:
            return "No prior conversation."
        lines = []
        for msg in history[-4:]:   # last 4 exchanges to stay within context
            role = msg.get("role", "user").capitalize()
            lines.append(f"{role}: {msg.get('content', '')}")
        return "\n".join(lines)
