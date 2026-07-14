from __future__ import annotations

import logging
from hybrid_retriever.models import RetrievedResult, RetrievalTrace

logger = logging.getLogger(__name__)

def build_response(trace: RetrievalTrace) -> dict:
    """Builds the final structured dictionary for API or LLM consumption."""
    return {
        "query": trace.query,
        "metadata": {
            "total_latency_s": round(trace.total_latency, 4),
            "es_latency_s": round(trace.es_latency, 4),
            "qdrant_latency_s": round(trace.qdrant_latency, 4),
            "fusion_latency_s": round(trace.fusion_latency, 4),
            "embedding_latency_s": round(trace.embedding_latency, 4),
            "candidates": {
                "elasticsearch": trace.es_candidate_count,
                "qdrant": trace.qdrant_candidate_count,
                "fusion_parameters": {"rrf_k": trace.rrf_k}
            }
        },
        "results": [
            {
                "chunk_id": r.chunk_id,
                "document_id": r.document_id,
                "document_title": r.document_title,
                "category": r.category,
                "citation": r.citation,
                "text": r.text,
                "pages": [r.page_start, r.page_end],
                "retrieval_metadata": {
                    "source": r.retrieval_source,
                    "rrf_score": round(r.rrf_score, 4),
                    "bm25_rank": r.bm25_rank,
                    "vector_rank": r.vector_rank
                }
            }
            for r in trace.results
        ]
    }
