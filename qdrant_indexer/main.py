from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from qdrant_indexer.config import QdrantConfig
from qdrant_indexer.client import get_qdrant_client
from qdrant_indexer.collection import setup_collection
from qdrant_indexer.indexer import load_document_points, index_document
from qdrant_indexer.validator import validate_collection
from qdrant_indexer.reporter import generate_reports
from embedding_pipeline.utils import generate_category_slug

logger = logging.getLogger("qdrant_indexer")

def run_pipeline(config: QdrantConfig | None = None) -> None:
    if config is None:
        config = QdrantConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info(f"Qdrant Vector Indexing Pipeline \u2014 Starting")
    logger.info("=" * 60)
    
    client = get_qdrant_client(config)
    
    # 1. Setup Collection
    setup_collection(client, config.collection_name, config.vector_dimension)
    
    start_time = time.monotonic()
    
    all_stats = []
    total_indexed = 0
    total_failed = 0
    total_skipped = 0
    
    # 2. Iterate and Index
    for cat_dir in config.chunks_dir.iterdir():
        if cat_dir.is_dir():
            for doc_dir in cat_dir.iterdir():
                if doc_dir.is_dir():
                    doc_id = doc_dir.name
                    category = cat_dir.name
                    slug = generate_category_slug(category)
                    
                    chunks_path = doc_dir / "chunks.json"
                    embeddings_path = config.embeddings_dir / slug / doc_id / "embeddings.json"
                    
                    points = load_document_points(doc_id, chunks_path, embeddings_path)
                    stat = index_document(client, config.collection_name, doc_id, points, config.batch_size)
                    
                    all_stats.append(stat)
                    if stat.status == "SUCCESS":
                        total_indexed += stat.points_indexed
                        logger.info(f"[{doc_id}] Indexed {stat.points_indexed} vectors.")
                    elif stat.status == "FAILED":
                        total_failed += 1
                    else:
                        total_skipped += 1
                        
    elapsed = time.monotonic() - start_time
    
    # 3. Validation
    val_res = validate_collection(client, config.collection_name, total_indexed, config.vector_dimension)
    if val_res["is_valid"]:
        logger.info("Qdrant Validation PASSED.")
    else:
        logger.error(f"Qdrant Validation FAILED: {val_res['issues']}")
        
    # 4. Reports
    summary = {
        "collection_name": config.collection_name,
        "vector_dimension": config.vector_dimension,
        "vectors_indexed": total_indexed,
        "documents_failed": total_failed,
        "documents_skipped": total_skipped,
        "indexing_speed_vectors_per_sec": round(total_indexed / max(0.01, elapsed), 2),
        "execution_time_seconds": round(elapsed, 2),
        "validation": val_res
    }
    
    generate_reports(config.report_dir, all_stats, summary)
    
    logger.info("=" * 60)
    logger.info(f"Qdrant Pipeline complete in {elapsed:.1f}s")
    logger.info("=" * 60)

def _setup_logging(config: QdrantConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("qdrant_indexer")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
