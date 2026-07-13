from __future__ import annotations

"""Domain models for Semantic Chunking."""

from dataclasses import dataclass, field
import enum

class ChunkingStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"

@dataclass
class SemanticChunk:
    chunk_id: str
    chunk_hash: str
    parent_document_id: str
    parent_section: str
    parent_heading: str
    category: str
    page_start: int
    page_end: int
    text: str
    token_estimate: int
    citation: str
    hierarchy_level: int
    cross_references: list[str] = field(default_factory=list)

@dataclass
class DocumentChunkingResult:
    document_id: str
    status: ChunkingStatus
    chunks: list[SemanticChunk] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error_message: str = ""
    duration_seconds: float = 0.0

@dataclass
class ChunkingSummary:
    documents_processed: int
    chunks_generated: int
    average_chunk_size: float
    max_chunk_size: int
    min_chunk_size: int
    max_hierarchy_depth: int
    duplicate_chunks_detected: int
    execution_time_seconds: float
