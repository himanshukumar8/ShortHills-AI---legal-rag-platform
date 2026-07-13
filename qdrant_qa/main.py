from __future__ import annotations

import logging
import sys
from qdrant_qa.config import QdrantQAConfig
from qdrant_qa.query_generator import generate_queries
from qdrant_qa.evaluator import execute_queries, calculate_metrics
from qdrant_qa.reporter import generate_reports
from qdrant_indexer.client import get_qdrant_client

# We need to run the indexer first to populate the mock
from qdrant_indexer.main import run_pipeline as run_indexer
from qdrant_indexer.config import QdrantConfig

logger = logging.getLogger("qdrant_qa")

def _setup_logging(config: QdrantQAConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("qdrant_qa")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | QA | %(message)s"))
    root_logger.addHandler(console_handler)

def run_qa(config: QdrantQAConfig | None = None) -> None:
    if config is None:
        config = QdrantQAConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("Qdrant QA Module \u2014 Starting")
    logger.info("=" * 60)
    
    # 0. Setup Mock Environment
    logger.info("Initializing Index (Mock Environment Setup)...")
    idx_config = QdrantConfig()
    idx_config.use_mock = True
    logging.getLogger("qdrant_indexer").setLevel(logging.WARNING)
    run_indexer(idx_config)
    
    client = get_qdrant_client(idx_config)
    
    # 1. Generate Queries
    logger.info("Generating synthetic semantic queries...")
    queries = generate_queries(config.chunks_dir, config.embeddings_dir, config.queries_per_type)
    logger.info(f"Generated {len(queries)} semantic queries.")
    
    # 2. Execute
    logger.info("Executing queries against Qdrant...")
    results = execute_queries(client, config.collection_name, queries)
    
    # 3. Calculate Metrics
    metrics = calculate_metrics(results)
    logger.info(f"QA Metrics: {metrics}")
    
    # 4. Report
    generate_reports(config.report_dir, results, metrics)
    
    score = metrics.get("quality_score", 0)
    logger.info("=" * 60)
    logger.info(f"Qdrant Quality Score: {score}/100")
    if score < 90:
        logger.warning("Score below threshold. See summary JSON for recommendations.")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_qa()
