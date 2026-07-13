from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class RetrievedResult:
    chunk_id: str
    document_id: str
    document_title: str
    category: str
    citation: str
    page_start: int
    page_end: int
    bm25_rank: int | None = None
    vector_rank: int | None = None
    rrf_score: float = 0.0
    retrieval_source: str = "" # "elasticsearch", "qdrant", or "hybrid"

@dataclass
class RetrievalTrace:
    query: str
    embedding_latency: float
    es_latency: float
    qdrant_latency: float
    fusion_latency: float
    total_latency: float
    es_candidate_count: int
    qdrant_candidate_count: int
    rrf_k: int
    results: list[RetrievedResult] = field(default_factory=list)
