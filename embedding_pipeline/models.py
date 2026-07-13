from __future__ import annotations

"""Domain models for the Embedding Pipeline."""

from dataclasses import dataclass, field
import enum

class EmbeddingStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@dataclass
class EmbeddingRecord:
    chunk_id: str
    chunk_hash: str
    embedding_model: str
    embedding_dimension: int
    embedding_vector: list[float]
    metadata: dict
    generation_timestamp: str

@dataclass
class DocumentEmbeddingResult:
    document_id: str
    status: EmbeddingStatus
    chunks_embedded: int = 0
    duration_seconds: float = 0.0
    error_message: str = ""

@dataclass
class EmbeddingSummary:
    documents_processed: int
    chunks_embedded: int
    documents_failed: int
    documents_skipped: int
    average_latency_seconds: float
    total_execution_time_seconds: float
    embedding_dimensions: int
    embedding_model: str
