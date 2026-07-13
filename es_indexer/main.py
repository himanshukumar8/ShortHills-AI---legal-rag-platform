from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from es_indexer.config import ESIndexerConfig
from es_indexer.client import get_es_client
from es_indexer.schema import INDEX_MAPPING, INDEX_SETTINGS
from es_indexer.indexer import parse_optimized_chunks, _chunk_list
from es_indexer.validator import validate_index
from es_indexer.reporter import generate_reports

logger = logging.getLogger("es_indexer")

def run_pipeline(config: ESIndexerConfig | None = None) -> None:
    if config is None:
        config = ESIndexerConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("Elasticsearch Indexing Pipeline \u2014 Starting")
    logger.info("=" * 60)
    
    client = get_es_client(config)
    
    # 1. Create Index with Mapping and Analyzers
    client.create_index(config.index_name, INDEX_SETTINGS, INDEX_MAPPING)
    
    start_time = time.monotonic()
    
    total_indexed = 0
    total_failures = 0
    doc_stats = []
    
    # Iterate through optimized chunks
    for cat_dir in config.input_dir.iterdir():
        if cat_dir.is_dir():
            for doc_dir in cat_dir.iterdir():
                if doc_dir.is_dir():
                    doc_id = doc_dir.name
                    es_docs = parse_optimized_chunks(doc_dir)
                    if not es_docs:
                        continue
                        
                    cat = es_docs[0]["category"]
                    
                    # Batch processing
                    success = 0
                    errors = 0
                    for batch in _chunk_list(es_docs, config.batch_size):
                        s, e = client.bulk_index(config.index_name, batch)
                        success += s
                        errors += e
                        
                    total_indexed += success
                    total_failures += errors
                    
                    doc_stats.append({
                        "document_id": doc_id,
                        "category": cat,
                        "chunks_indexed": success,
                        "status": "SUCCESS" if errors == 0 else "PARTIAL_FAIL"
                    })
                    
                    logger.info(f"[{doc_id}] Indexed {success} chunks.")
                    
    elapsed_time = time.monotonic() - start_time
    
    # 2. Validate
    test_cit = "26 U.S.C. \u00a7 1" # A common citation
    val_res = validate_index(client, config.index_name, total_indexed, test_cit)
    
    if val_res["is_valid"]:
        logger.info("Validation PASSED.")
    else:
        logger.error(f"Validation FAILED: {val_res['issues']}")
        
    # 3. Generate Reports
    global_stats = {
        "documents_indexed": len(doc_stats),
        "total_chunks_indexed": total_indexed,
        "failures": total_failures,
        "indexing_speed_chunks_per_sec": round(total_indexed / max(0.01, elapsed_time), 2),
        "average_document_size": round(total_indexed / max(1, len(doc_stats)), 2),
        "total_execution_time": round(elapsed_time, 2),
        "validation": val_res
    }
    
    generate_reports(config.report_dir, doc_stats, global_stats)
    
    logger.info("=" * 60)
    logger.info(f"Elasticsearch Pipeline complete in {elapsed_time:.1f}s")
    logger.info("=" * 60)
    

def _setup_logging(config: ESIndexerConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("es_indexer")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
