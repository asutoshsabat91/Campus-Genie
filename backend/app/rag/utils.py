"""
CampusGenie — RAG Utilities
Shared helper functions for the RAG pipeline.
"""

import re
import os


def sanitize_doc_id(filename: str) -> str:
    """
    Generate a safe, consistent doc_id from a filename.
    Strips extension, lowercases, replaces non-alphanumeric with underscore.
    Truncates to 64 characters.

    Examples:
        "OS Notes (2024).pdf" -> "os_notes__2024_"
        "DBMS_Unit3.pdf"      -> "dbms_unit3"
    """
    name = os.path.splitext(filename)[0]
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
    return safe.lower()[:64]


def truncate_text(text: str, max_chars: int = 200, suffix: str = "...") -> str:
    """Truncate text to max_chars, appending suffix if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + suffix


def clean_answer(answer: str) -> str:
    """
    Post-process LLM answer text.
    - Strip leading/trailing whitespace
    - Collapse multiple blank lines into one
    """
    answer = answer.strip()
    answer = re.sub(r"\n{3,}", "\n\n", answer)
    return answer
