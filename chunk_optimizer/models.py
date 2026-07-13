from __future__ import annotations

"""Adaptive Chunk Optimizer Domain Models."""

from dataclasses import dataclass, field
from semantic_chunker.models import SemanticChunk

@dataclass
class OptimizedChunk(SemanticChunk):
    """An optimized chunk containing lineage information."""
    original_chunk_ids: list[str] = field(default_factory=list)
