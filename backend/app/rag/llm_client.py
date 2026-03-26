"""
CampusGenie — Educational LLM Client
Integrates with Ollama (Gemma 2B) to provide detailed, explanatory answers for students.

Why Ollama + Educational Focus?
  - Runs 100% locally inside Docker — no API keys, no internet
  - Gemma 2B provides excellent balance of performance and memory efficiency
  - Educational prompt engineering ensures detailed, learning-focused responses
  - Proper citation formatting helps students learn to reference sources

The LLM is designed to provide comprehensive educational responses while
maintaining strict adherence to provided context to ensure accuracy.
"""

import logging
import ollama
from app.config import settings

logger = logging.getLogger(__name__)

# ── Prompt Template ───────────────────────────────────────────────────────────
# The system prompt is the KEY to preventing hallucination.
# We explicitly tell the model: use ONLY the context below.

RAG_PROMPT_TEMPLATE = """You are CampusGenie, an educational AI assistant designed to help college students understand their course materials thoroughly.

Your purpose is to provide detailed, explanatory answers that help students learn and understand concepts deeply.

GUIDELINES:
1. Use the provided context to answer the student's question comprehensively
2. Provide detailed explanations that break down complex concepts into understandable parts
3. Include relevant examples, context, and background information when available
4. Structure your answers clearly with proper formatting (bullet points, numbered lists, or paragraphs)
5. Always cite your sources using the format: [Source: Document Name, Page X]
6. If multiple sources provide different perspectives, synthesize them and reference each
7. If you cannot find relevant information after careful review, respond with exactly:
   "Not found in uploaded documents."

EDUCATIONAL APPROACH:
- Explain concepts step-by-step for better understanding
- Provide context to help students see the bigger picture
- Use clear, educational language appropriate for college-level learning
- Include practical implications or applications when relevant
- Help students connect new information to what they might already know

Context from campus documents:
---
{context}
---

Chat History:
{chat_history}

Student Question: {question}

Detailed Educational Answer:"""

NOT_FOUND_RESPONSE = "Not found in uploaded documents."


class LLMClient:
    """
    Educational LLM Client for CampusGenie.
    Provides detailed, explanatory answers for student learning with proper citations.
    Engineered to prevent hallucination while maximizing educational value.
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
                    'temperature': 0.2,  # Slightly higher for more detailed responses
                    'num_ctx': 4096,
                    'num_predict': 1024,  # Allow longer responses
                }
            )
            answer = response['response'].strip()
            
            # Post-process answer for better formatting
            answer = self._enhance_answer_formatting(answer)
            
            # Check if answer indicates not found
            if not answer or answer.lower() in ['not found in uploaded documents.', 'i cannot answer based on the provided context.']:
                return NOT_FOUND_RESPONSE
                
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return NOT_FOUND_RESPONSE

    def _enhance_answer_formatting(self, answer: str) -> str:
        """
        Enhance answer formatting for better readability and educational value.
        """
        # Ensure proper spacing and formatting
        lines = answer.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add proper spacing for bullet points and numbered lists
                if line.startswith(('•', '-', '*')):
                    formatted_lines.append(f"  {line}")
                elif line and line[0].isdigit() and '.' in line[:10]:
                    formatted_lines.append(f"  {line}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append("")  # Preserve empty lines
        
        # Ensure proper paragraph breaks
        formatted_answer = '\n\n'.join(formatted_lines)
        
        # Add educational closing if not present
        if not any(phrase in formatted_answer.lower() for phrase in ['source:', 'reference:', 'see also']):
            formatted_answer += "\n\n*Remember to review the source documents for complete details.*"
        
        return formatted_answer

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
