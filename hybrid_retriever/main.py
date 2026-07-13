from __future__ import annotations

import logging
import sys
import time

from hybrid_retriever.config import HybridConfig
from hybrid_retriever.elasticsearch_client import ElasticsearchRetriever
from hybrid_retriever.qdrant_client import QdrantRetriever
from hybrid_retriever.embedding_provider import EmbedderWrapper
from hybrid_retriever.metadata_filter import extract_filters
from hybrid_retriever.fusion import reciprocal_rank_fusion
from hybrid_retriever.ranker import rank_and_truncate
from hybrid_retriever.citation_validator import validate_citations
from hybrid_retriever.validator import verify_output
from hybrid_retriever.response_builder import build_response
from hybrid_retriever.reporter import generate_reports
from hybrid_retriever.models import RetrievalTrace

# To mock end-to-end execution, we ensure dependencies have dummy data
from es_indexer.main import run_pipeline as run_es
from es_indexer.config import ESIndexerConfig
from qdrant_indexer.main import run_pipeline as run_qd
from qdrant_indexer.config import QdrantConfig

logger = logging.getLogger("hybrid_retriever")

def run_pipeline(config: HybridConfig | None = None, query: str = "Taxation rules for independent contractors under IRS Section 162") -> dict:
    if config is None:
        config = HybridConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval Pipeline \u2014 Starting")
    logger.info(f"Query: '{query}'")
    logger.info("=" * 60)
    
    # 0. Setup Mock Environment
    logger.info("Initializing Indexers (Mock Environment Setup)...")
    logging.getLogger("es_indexer").setLevel(logging.WARNING)
    logging.getLogger("qdrant_indexer").setLevel(logging.WARNING)
    run_es(ESIndexerConfig(use_mock=True))
    run_qd(QdrantConfig(use_mock=True))
    
    # Initialize Clients
    es_retriever = ElasticsearchRetriever(config)
    qd_retriever = QdrantRetriever(config)
    embedder = EmbedderWrapper(config)
    
    total_start = time.monotonic()
    
    # 1. Metadata Filters Extraction
    filters = extract_filters(query)
    if filters:
        logger.info(f"Extracted metadata pre-filters: {filters}")
        
    # 2. Embedding Generation
    query_vector, emb_lat = embedder.embed_query(query)
    logger.info(f"Generated query embedding in {emb_lat:.4f}s")
    
    # 3. Parallel Retrieval (Simulated sequentially here)
    logger.info("Executing Elasticsearch (BM25)...")
    es_hits, es_lat = es_retriever.retrieve(query, filters)
    
    logger.info("Executing Qdrant (Dense Vector)...")
    qd_hits, qd_lat = qd_retriever.retrieve(query_vector, filters)
    
    logger.info(f"Candidate set: {len(es_hits)} lexical hits, {len(qd_hits)} semantic hits")
    
    # 4. Fusion
    logger.info(f"Applying Reciprocal Rank Fusion (k={config.rrf_k})...")
    fused_dict, fuse_lat = reciprocal_rank_fusion(es_hits, qd_hits, config.rrf_k)
    
    # 5. Ranking & Deduplication (Implicit in dictionary keys)
    final_results = rank_and_truncate(fused_dict, config.top_k)
    
    # 6. Verification
    validate_citations(final_results)
    val_res = verify_output(final_results, config.top_k)
    if val_res["is_valid"]:
        logger.info("Hybrid Pipeline Validation PASSED.")
    else:
        logger.error(f"Validation FAILED: {val_res['issues']}")
        
    total_lat = time.monotonic() - total_start
    
    # 7. Trace and Response
    trace = RetrievalTrace(
        query=query,
        embedding_latency=emb_lat,
        es_latency=es_lat,
        qdrant_latency=qd_lat,
        fusion_latency=fuse_lat,
        total_latency=total_lat,
        es_candidate_count=len(es_hits),
        qdrant_candidate_count=len(qd_hits),
        rrf_k=config.rrf_k,
        results=final_results
    )
    
    response = build_response(trace)
    generate_reports(config.report_dir, response, val_res)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval complete in {total_lat:.4f}s")
    logger.info(f"Retrieved Top-{len(final_results)} chunks.")
    logger.info("=" * 60)
    
    return response

def _setup_logging(config: HybridConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("hybrid_retriever")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | HYBRID | %(message)s"))
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
