from __future__ import annotations

from chunk_optimizer.models import OptimizedChunk
from chunk_optimizer.config import OptimizerConfig
from semantic_chunker.utils import compute_chunk_hash, estimate_tokens

def _merge_two_chunks(c1: OptimizedChunk, c2: OptimizedChunk) -> OptimizedChunk:
    """Merge two chunks together, preserving the earliest start page and latest end page."""
    merged_text = c1.text + "\n\n" + c2.text
    merged_cross = list(set(c1.cross_references + c2.cross_references))
    merged_orig = list(set(c1.original_chunk_ids + c2.original_chunk_ids))
    
    return OptimizedChunk(
        chunk_id=c1.chunk_id, # Inherit the ID of the first chunk
        chunk_hash=compute_chunk_hash(merged_text),
        parent_document_id=c1.parent_document_id,
        parent_section=c1.parent_section, # Retain parent section of the first chunk
        parent_heading=c1.parent_heading,
        category=c1.category,
        page_start=min(c1.page_start, c2.page_start),
        page_end=max(c1.page_end, c2.page_end),
        text=merged_text,
        token_estimate=estimate_tokens(merged_text),
        citation=c1.citation,
        hierarchy_level=c1.hierarchy_level,
        cross_references=sorted(merged_cross),
        original_chunk_ids=sorted(merged_orig)
    )

def coalesce_chunks(chunks: list[OptimizedChunk], config: OptimizerConfig) -> list[OptimizedChunk]:
    """Merge tiny chunks into their neighbors to ensure meaningful context size."""
    if not chunks:
        return []
        
    coalesced = []
    current = chunks[0]
    
    for i in range(1, len(chunks)):
        nxt = chunks[i]
        
        # If the current chunk is too small, OR the next chunk is too small, try to merge
        # ONLY IF merging won't violate the MAX_TOKENS threshold.
        if (current.token_estimate < config.min_tokens or nxt.token_estimate < config.min_tokens) and \
           (current.token_estimate + nxt.token_estimate <= config.max_tokens):
            
            # Merge forward
            current = _merge_two_chunks(current, nxt)
        else:
            coalesced.append(current)
            current = nxt
            
    coalesced.append(current)
    return coalesced
