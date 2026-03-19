"""
CampusGenie — PDF Processor
Extracts text and metadata from uploaded PDF files using PyMuPDF (fitz).
Returns structured page-level data for chunking.
"""

import fitz  # PyMuPDF
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class PageContent:
    """Represents extracted content from a single PDF page."""
    page_number: int       # 1-indexed
    text: str
    word_count: int


@dataclass
class DocumentContent:
    """Represents extracted content from an entire PDF."""
    filename: str
    doc_id: str
    page_count: int
    pages: list[PageContent]
    total_words: int


class PDFProcessor:
    """
    Extracts text from PDF files page by page.
    Preserves page numbers for citation generation.
    """

    def __init__(self, min_page_words: int = 10):
        """
        Args:
            min_page_words: Minimum words a page must have to be included.
                            Filters out blank / header-only pages.
        """
        self.min_page_words = min_page_words

    def process(self, filepath: str, doc_id: Optional[str] = None) -> DocumentContent:
        """
        Process a PDF file and extract text per page.

        Args:
            filepath: Path to the PDF file
            doc_id:   Unique identifier for this document

        Returns:
            DocumentContent with per-page text and metadata
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF not found: {filepath}")

        filename = os.path.basename(filepath)
        if doc_id is None:
            doc_id = self._generate_doc_id(filename)

        pages: list[PageContent] = []

        with fitz.open(filepath) as pdf:
            total_pages = len(pdf)

            for page_idx in range(total_pages):
                page = pdf[page_idx]
                raw_text = page.get_text("text")
                cleaned = self._clean_text(raw_text)
                word_count = len(cleaned.split())

                if word_count < self.min_page_words:
                    continue  # skip mostly-empty pages

                pages.append(
                    PageContent(
                        page_number=page_idx + 1,
                        text=cleaned,
                        word_count=word_count,
                    )
                )

        total_words = sum(p.word_count for p in pages)

        return DocumentContent(
            filename=filename,
            doc_id=doc_id,
            page_count=total_pages,
            pages=pages,
            total_words=total_words,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _clean_text(text: str) -> str:
        """Remove excessive whitespace while preserving paragraph structure."""
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        return "\n".join(cleaned_lines)

    @staticmethod
    def _generate_doc_id(filename: str) -> str:
        """Generate a filesystem-safe doc_id from filename."""
        import re
        name = os.path.splitext(filename)[0]
        safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)
        return safe.lower()[:64]
