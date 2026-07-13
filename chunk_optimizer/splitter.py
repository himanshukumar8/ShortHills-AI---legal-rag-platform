from __future__ import annotations

import re
from chunk_optimizer.models import OptimizedChunk
from chunk_optimizer.config import OptimizerConfig
from semantic_chunker.utils import compute_chunk_hash, estimate_tokens
from semantic_chunker.metadata import extract_cross_references

def split_oversized_chunk(chunk: OptimizedChunk, max_tokens: int) -> list[OptimizedChunk]:
    """Recursively split a chunk that exceeds max_tokens using structural fallbacks."""
    if chunk.token_estimate <= max_tokens:
        return [chunk]
        
    # Structural hierarchy cascade for splitting
    patterns = [
        r"(?=\n\([a-z]\)\s)",     # 1. Subsection: (a)
        r"(?=\n\(\d+\)\s)",       # 2. Numbered para: (1)
        r"(?=\n[A-Z][A-Za-z\s]{2,50}\n)", # 3. Heading
        r"(?=\n\n)",              # 4. Paragraph break
        r"(?<=\.\s)"              # 5. Sentence break (last resort)
    ]
    
    for pattern in patterns:
        splits = re.split(pattern, chunk.text)
        splits = [s.strip() for s in splits if s.strip()]
        
        # Did the pattern successfully break the chunk into pieces?
        if len(splits) > 1:
            resulting_chunks = []
            for i, text_part in enumerate(splits):
                new_tokens = estimate_tokens(text_part)
                
                part_chunk = OptimizedChunk(
                    chunk_id=f"{chunk.chunk_id}_SUB-{i+1}",
                    chunk_hash=compute_chunk_hash(text_part),
                    parent_document_id=chunk.parent_document_id,
                    parent_section=chunk.parent_section,
                    parent_heading=chunk.parent_heading,
                    category=chunk.category,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    text=text_part,
                    token_estimate=new_tokens,
                    citation=chunk.citation,
                    hierarchy_level=chunk.hierarchy_level + 1,
                    cross_references=extract_cross_references(text_part),
                    original_chunk_ids=chunk.original_chunk_ids
                )
                
                # If a resulting part is STILL oversized, recurse
                if new_tokens > max_tokens:
                    resulting_chunks.extend(split_oversized_chunk(part_chunk, max_tokens))
                else:
                    resulting_chunks.append(part_chunk)
                    
            # Check if this strategy successfully reduced all pieces
            if all(c.token_estimate <= max_tokens for c in resulting_chunks):
                return resulting_chunks
                
    # If absolutely everything fails (a single >2000 token sentence without periods?!), just return it.
    return [chunk]

def expand_splits(chunks: list[OptimizedChunk], config: OptimizerConfig) -> list[OptimizedChunk]:
    """Iterate through all chunks and split oversized ones."""
    expanded = []
    for c in chunks:
        expanded.extend(split_oversized_chunk(c, config.max_tokens))
    return expanded
