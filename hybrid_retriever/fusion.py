from __future__ import annotations

import logging
from collections import defaultdict
from hybrid_retriever.utils import measure_latency
from hybrid_retriever.config import HybridConfig

logger = logging.getLogger(__name__)

@measure_latency
def reciprocal_rank_fusion(es_hits: list[dict], qdrant_hits: list[dict], rrf_k: int) -> dict[str, dict]:
    """
    Applies Reciprocal Rank Fusion (RRF) to combine lexical and semantic ranks.
    RRF Score = 1 / (k + rank)
    """
    fused = defaultdict(lambda: {"es_rank": None, "qdrant_rank": None, "score": 0.0, "source": None, "payload": {}})
    
    # Process Elasticsearch Hits
    for rank, hit in enumerate(es_hits, start=1):
        # We need chunk_id from ES source
        chunk_id = hit.get("chunk_id")
        if not chunk_id:
            continue
            
        score = 1.0 / (rrf_k + rank)
        fused[chunk_id]["es_rank"] = rank
        fused[chunk_id]["score"] += score
        fused[chunk_id]["payload"] = hit
        fused[chunk_id]["source"] = "elasticsearch"
        
    # Process Qdrant Hits
    for rank, hit in enumerate(qdrant_hits, start=1):
        # We need chunk_id from Qdrant payload
        chunk_id = hit.get("chunk_id")
        if not chunk_id:
            continue
            
        score = 1.0 / (rrf_k + rank)
        fused[chunk_id]["qdrant_rank"] = rank
        fused[chunk_id]["score"] += score
        
        # If already seen in ES, it's a hybrid hit, we just update the payload if missing
        if fused[chunk_id]["source"] == "elasticsearch":
            fused[chunk_id]["source"] = "hybrid"
        else:
            fused[chunk_id]["source"] = "qdrant"
            fused[chunk_id]["payload"] = hit
            
    return dict(fused)
