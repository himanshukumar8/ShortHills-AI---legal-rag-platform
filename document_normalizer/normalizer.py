from __future__ import annotations

"""Facade for orchestrating document normalization."""

import logging
from pdf_parser.models import ParsedDocument
from document_normalizer.models import (
    NormalizedDocument, 
    NormalizedPage, 
    NormalizationStatistics
)
from document_normalizer.cleaner import clean_page_text
from document_normalizer.validator import validate_normalization

logger = logging.getLogger(__name__)

def normalize_document(parsed_doc: ParsedDocument) -> NormalizedDocument:
    """Normalize a parsed document.
    
    Applies text cleaning to each page, aggregates statistics, and validates
    the structural integrity of the output.
    """
    normalized_pages = []
    
    for page in parsed_doc.pages:
        # If the page is completely empty, preserve it to maintain page count
        if not page.text.strip():
            norm_page = NormalizedPage(
                page_number=page.page_number,
                text="",
                original_character_count=page.character_count,
                normalized_character_count=0,
                warnings=["Blank page preserved."]
            )
        else:
            cleaned_text = clean_page_text(page.text)
            norm_page = NormalizedPage(
                page_number=page.page_number,
                text=cleaned_text,
                original_character_count=page.character_count,
                normalized_character_count=len(cleaned_text),
                warnings=[]
            )
        normalized_pages.append(norm_page)
        
    # Assemble full text
    full_text = "\n\n".join(p.text for p in normalized_pages if p.text)
    
    # Calculate statistics
    orig_chars = sum(p.original_character_count for p in normalized_pages)
    norm_chars = sum(p.normalized_character_count for p in normalized_pages)
    chars_removed = orig_chars - norm_chars
    reduction_pct = (chars_removed / orig_chars * 100) if orig_chars > 0 else 0.0
    
    stats = NormalizationStatistics(
        total_pages=len(normalized_pages),
        original_characters=orig_chars,
        normalized_characters=norm_chars,
        characters_removed=chars_removed,
        reduction_percentage=round(reduction_pct, 2)
    )
    
    norm_doc = NormalizedDocument(
        metadata=parsed_doc.metadata,
        pages=normalized_pages,
        full_text=full_text,
        statistics=stats,
        processing_info=dict(parsed_doc.processing_info) # shallow copy
    )
    
    # Validate
    validation_warnings = validate_normalization(parsed_doc, norm_doc)
    if validation_warnings:
        if "warnings" not in norm_doc.processing_info:
            norm_doc.processing_info["warnings"] = []
        norm_doc.processing_info["warnings"].extend(validation_warnings)
        
    return norm_doc
