from __future__ import annotations

"""Core text extraction for the PDF Parser Pipeline.

Uses PyMuPDF (fitz) as the primary extraction engine for its speed and accuracy.
Implements a fallback to pdfplumber when PyMuPDF extraction yields no text
(a common indicator of embedded fonts or encoding issues that pdfplumber
sometimes handles better).
"""

import logging
from pathlib import Path

import fitz  # PyMuPDF

from pdf_parser.exceptions import ExtractionError
from pdf_parser.models import PageExtract
from pdf_parser.utils import clean_text, count_words

logger = logging.getLogger(__name__)


def extract_pages(file_path: Path, document_id: str) -> list[PageExtract]:
    """Extract text from a PDF document, preserving page boundaries.

    Tries PyMuPDF first. If a page yields 0 characters, falls back to
    pdfplumber for that specific page.

    Args:
        file_path: Path to the PDF file.
        document_id: The document ID (for logging/errors).

    Returns:
        A list of PageExtract objects, one for each page.

    Raises:
        ExtractionError: If the PDF cannot be opened or parsed.
    """
    logger.debug("[%s] Starting text extraction", document_id)
    pages: list[PageExtract] = []
    
    # We will only import pdfplumber if needed to avoid overhead, but since we
    # might need it page-by-page, we import it lazily in the fallback function.
    
    try:
        with fitz.open(str(file_path)) as doc:
            for page_idx in range(len(doc)):
                page_number = page_idx + 1
                page = doc[page_idx]
                
                try:
                    raw_text = page.get_text("text")
                    cleaned_text = clean_text(raw_text)
                    char_count = len(cleaned_text)
                    
                    if char_count == 0:
                        # Empty text detected, trigger fallback
                        logger.warning(
                            "[%s] PyMuPDF extracted 0 chars on page %d; attempting fallback",
                            document_id,
                            page_number,
                        )
                        extract = _fallback_extract_page(
                            file_path, page_idx, page_number, document_id
                        )
                    else:
                        extract = PageExtract(
                            page_number=page_number,
                            text=cleaned_text,
                            character_count=char_count,
                            word_count=count_words(cleaned_text),
                            extractor_used="pymupdf",
                        )
                    pages.append(extract)
                    
                except Exception as exc:
                    logger.warning(
                        "[%s] Exception on page %d with PyMuPDF: %s; attempting fallback",
                        document_id,
                        page_number,
                        exc,
                    )
                    extract = _fallback_extract_page(
                        file_path, page_idx, page_number, document_id
                    )
                    pages.append(extract)
                    
    except Exception as exc:
        raise ExtractionError(
            f"Failed to open or parse PDF with PyMuPDF: {exc}", document_id
        ) from exc

    logger.debug("[%s] Extracted %d pages", document_id, len(pages))
    return pages


def _fallback_extract_page(
    file_path: Path, page_idx: int, page_number: int, document_id: str
) -> PageExtract:
    """Extract a single page using pdfplumber as a fallback.

    Args:
        file_path: Path to the PDF.
        page_idx: 0-indexed page number.
        page_number: 1-indexed page number.
        document_id: The document ID.

    Returns:
        The extracted page data.
    """
    import pdfplumber

    warnings = ["PyMuPDF extraction failed or yielded 0 characters. Used pdfplumber fallback."]
    
    try:
        with pdfplumber.open(file_path) as pdf:
            if page_idx >= len(pdf.pages):
                raise ExtractionError(
                    "pdfplumber page index out of range", document_id, page_number
                )
            
            page = pdf.pages[page_idx]
            raw_text = page.extract_text()
            
            # pdfplumber might return None if no text is found
            if raw_text is None:
                raw_text = ""
                warnings.append("pdfplumber also yielded 0 characters.")
                
            cleaned_text = clean_text(raw_text)
            
            return PageExtract(
                page_number=page_number,
                text=cleaned_text,
                character_count=len(cleaned_text),
                word_count=count_words(cleaned_text),
                extractor_used="pdfplumber",
                warnings=warnings,
            )
            
    except Exception as exc:
        logger.error(
            "[%s] pdfplumber fallback failed on page %d: %s",
            document_id,
            page_number,
            exc,
        )
        return PageExtract(
            page_number=page_number,
            text="",
            character_count=0,
            word_count=0,
            extractor_used="failed",
            warnings=warnings + [f"pdfplumber exception: {exc}"],
        )
