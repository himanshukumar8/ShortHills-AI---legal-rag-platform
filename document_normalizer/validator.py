from __future__ import annotations

"""Validation logic for the normalized documents."""

from pdf_parser.models import ParsedDocument
from document_normalizer.models import NormalizedDocument
from document_normalizer.exceptions import ValidationFailedError

def validate_normalization(original: ParsedDocument, normalized: NormalizedDocument) -> list[str]:
    """Validate that the normalized document has not been destructively altered.
    
    Checks:
    1. Page count equality
    2. Missing pages
    3. Missing legal citations / section markers (rough heuristics)
    
    Raises:
        ValidationFailedError if fatal structural issues occur.
        
    Returns:
        List of warnings for non-fatal issues.
    """
    warnings = []
    
    # 1. Page Count Equality
    if len(original.pages) != len(normalized.pages):
        raise ValidationFailedError(
            f"Page count mismatch: Original had {len(original.pages)}, Normalized has {len(normalized.pages)}",
            normalized.metadata.document_id
        )
        
    # 2. Check for missing/reordered pages
    for orig_p, norm_p in zip(original.pages, normalized.pages):
        if orig_p.page_number != norm_p.page_number:
            raise ValidationFailedError(
                f"Page ordering mismatch at index {orig_p.page_number}: Original {orig_p.page_number} != Normalized {norm_p.page_number}",
                normalized.metadata.document_id
            )
            
    # 3. Legal marker heuristic checks
    # If the original text had section symbols (§) or U.S.C., the normalized text should not have lost them entirely.
    orig_text = original.full_text
    norm_text = normalized.full_text
    
    orig_section_count = orig_text.count("§")
    norm_section_count = norm_text.count("§")
    
    if orig_section_count > 0 and norm_section_count < (orig_section_count * 0.9):
        # We allow a slight discrepancy if some § were on standalone header lines, but losing >10% is bad.
        warnings.append(f"Significant loss of section symbols (§): {orig_section_count} -> {norm_section_count}")
        
    orig_usc_count = orig_text.count("U.S.C.")
    norm_usc_count = norm_text.count("U.S.C.")
    
    if orig_usc_count > 0 and norm_usc_count < (orig_usc_count * 0.9):
        warnings.append(f"Significant loss of U.S.C. citations: {orig_usc_count} -> {norm_usc_count}")
        
    return warnings
