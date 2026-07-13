from __future__ import annotations

"""Core chunking strategies by document category."""

import re
from document_normalizer.models import NormalizedDocument
from semantic_chunker.models import SemanticChunk
from semantic_chunker.hierarchy import HierarchyTracker
from semantic_chunker.utils import compute_chunk_hash, estimate_tokens
from semantic_chunker.metadata import extract_cross_references

def chunk_acts(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Chunk strategy for Acts/Statutes. Splits on Sections/Subsections."""
    return _chunk_by_regex(doc, r"^(?:SEC\.|Sec\.|§)\s*\d+", "STATUTE")

def chunk_judgments(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Chunk strategy for Court Judgments. Splits on paragraph breaks and roman numerals."""
    return _chunk_by_regex(doc, r"^(?:[IVX]+\.|\[\d+\])", "JUDGMENT_OPINION")

def chunk_regs(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Chunk strategy for Treasury Regulations. Splits on CFR section markers."""
    return _chunk_by_regex(doc, r"^§\s*\d+\.\d+", "REGULATION")

def chunk_irs(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Chunk strategy for IRS Publications. Splits on Headers (short uppercase/title case lines)."""
    return _chunk_by_regex(doc, r"^[A-Z][a-zA-Z\s]{2,50}$", "IRS_GUIDANCE")

def chunk_commentary(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Chunk strategy for Commentary. Standard double newline splitting."""
    return _chunk_by_regex(doc, r"^[A-Z][a-zA-Z\s]{2,50}$", "COMMENTARY")


def _chunk_by_regex(doc: NormalizedDocument, split_pattern: str, chunk_type: str) -> list[SemanticChunk]:
    """Generic recursive builder that splits text by a specific structural regex."""
    chunks: list[SemanticChunk] = []
    tracker = HierarchyTracker()
    
    # We will iterate through normalized pages to preserve page numbers
    # To split correctly while knowing the page, we read line by line.
    
    current_chunk_text = []
    start_page = 1
    current_page = 1
    chunk_index = 1
    
    regex = re.compile(split_pattern)
    
    def finalize_chunk(text_lines: list[str], end_page: int):
        nonlocal chunk_index
        text = "\n".join(text_lines).strip()
        if not text:
            return
            
        chunk_id = f"{doc.metadata.document_id}_CHUNK-{chunk_index:04d}"
        
        chunk = SemanticChunk(
            chunk_id=chunk_id,
            chunk_hash=compute_chunk_hash(text),
            parent_document_id=doc.metadata.document_id,
            parent_section=tracker.get_parent_section(),
            parent_heading=tracker.get_parent_heading(),
            category=doc.metadata.category,
            page_start=start_page,
            page_end=end_page,
            text=text,
            token_estimate=estimate_tokens(text),
            citation=f"{doc.metadata.title}, {tracker.get_parent_section()}",
            hierarchy_level=tracker.get_depth_level(),
            cross_references=extract_cross_references(text)
        )
        chunks.append(chunk)
        chunk_index += 1

    for page in doc.pages:
        current_page = page.page_number
        lines = page.text.split("\n")
        
        for line in lines:
            line_str = line.strip()
            
            # If line matches the section boundary
            if line_str and regex.match(line_str):
                # Finalize previous chunk
                if current_chunk_text:
                    finalize_chunk(current_chunk_text, current_page)
                    current_chunk_text = []
                    start_page = current_page
                
                # Update tracker heuristically
                tracker.current_section = line_str[:100]
                tracker.current_heading = line_str[:100]
                
            current_chunk_text.append(line)
            
            # If chunk is getting massively oversized (e.g., > 1500 tokens / ~2000 words), force split at next paragraph
            if len(current_chunk_text) > 1 and current_chunk_text[-1].strip() == "":
                if estimate_tokens("\n".join(current_chunk_text)) > 1500:
                    finalize_chunk(current_chunk_text, current_page)
                    current_chunk_text = []
                    start_page = current_page

    # Finalize remaining text
    if current_chunk_text:
        finalize_chunk(current_chunk_text, current_page)
        
    return chunks
