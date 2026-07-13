from __future__ import annotations

import logging
from hybrid_retriever.models import RetrievedResult

logger = logging.getLogger(__name__)

def rank_and_truncate(fused_results: dict[str, dict], top_k: int) -> list[RetrievedResult]:
    """Sorts fused results by RRF score descending and truncates to top_k."""
    # Convert dict back to list for sorting
    results_list = list(fused_results.values())
    results_list.sort(key=lambda x: x["score"], reverse=True)
    
    top_results = results_list[:top_k]
    final_output = []
    
    for res in top_results:
        payload = res["payload"]
        final_output.append(
            RetrievedResult(
                chunk_id=payload.get("chunk_id", ""),
                document_id=payload.get("parent_document_id", ""),
                document_title=payload.get("document_title", ""),
                category=payload.get("category", ""),
                citation=payload.get("citation", ""),
                page_start=payload.get("page_start", 0),
                page_end=payload.get("page_end", 0),
                bm25_rank=res["es_rank"],
                vector_rank=res["qdrant_rank"],
                rrf_score=res["score"],
                retrieval_source=res["source"]
            )
        )
        
    return final_output
