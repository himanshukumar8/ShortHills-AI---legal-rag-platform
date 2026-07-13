from __future__ import annotations

"""Quality validation for the PDF Parser Pipeline.

Performs consistency and quality checks on the extracted pages.
Produces warnings instead of crashing to ensure maximum throughput,
while flagging problematic documents for manual review.
"""

import logging

from pdf_parser.models import PageExtract

logger = logging.getLogger(__name__)


def validate_extraction(
    document_id: str, pages: list[PageExtract], expected_pages: int
) -> list[str]:
    """Validate the extracted pages against expected metrics.

    Args:
        document_id: The document ID being validated.
        pages: The list of extracted pages.
        expected_pages: The page count recorded during download/validation.

    Returns:
        A list of warning messages. Empty if validation passes cleanly.
    """
    warnings: list[str] = []
    
    actual_pages = len(pages)
    
    # 1. Check page count mismatch
    if actual_pages != expected_pages:
        warn_msg = f"Page count mismatch: expected {expected_pages}, extracted {actual_pages}"
        logger.warning("[%s] %s", document_id, warn_msg)
        warnings.append(warn_msg)
        
    # 2. Check for missing pages (sequence gaps)
    # The extractor should yield page numbers 1..N
    expected_sequence = set(range(1, actual_pages + 1))
    actual_sequence = {p.page_number for p in pages}
    missing_pages = expected_sequence - actual_sequence
    
    if missing_pages:
        warn_msg = f"Missing pages in sequence: {sorted(missing_pages)}"
        logger.warning("[%s] %s", document_id, warn_msg)
        warnings.append(warn_msg)
        
    # 3. Check for empty text or persistent extraction warnings
    empty_pages = []
    for page in pages:
        if page.character_count == 0:
            empty_pages.append(page.page_number)
        
        # Propagate page-level warnings up
        if page.warnings:
            for w in page.warnings:
                warnings.append(f"Page {page.page_number}: {w}")
                
    if empty_pages:
        warn_msg = f"Empty text (0 chars) on {len(empty_pages)} pages: {empty_pages}"
        logger.warning("[%s] %s", document_id, warn_msg)
        warnings.append(warn_msg)

    return warnings
