from __future__ import annotations

from chunk_optimizer.models import OptimizedChunk
from chunk_optimizer.config import OptimizerConfig
from chunk_optimizer.splitter import expand_splits
from chunk_optimizer.merger import coalesce_chunks

def optimize_document_chunks(chunks: list[OptimizedChunk], config: OptimizerConfig) -> list[OptimizedChunk]:
    """Optimize a list of chunks by splitting oversized ones and coalescing tiny ones."""
    if not chunks:
        return []
        
    # 1. Expand (Split)
    expanded = expand_splits(chunks, config)
    
    # 2. Coalesce (Merge)
    optimized = coalesce_chunks(expanded, config)
    
    return optimized
