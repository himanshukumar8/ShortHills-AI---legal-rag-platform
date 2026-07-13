from __future__ import annotations

import logging
import sys
from es_qa.config import ESQAConfig
from es_qa.query_generator import generate_queries
from es_qa.evaluator import execute_queries, calculate_metrics
from es_qa.reporter import generate_reports
from es_indexer.client import get_es_client

# Note: In a real environment we would query the running ES daemon.
# Since we are mocking ES, we need to populate the mock index first so we have something to query.
from es_indexer.main import run_pipeline as run_indexer
from es_indexer.config import ESIndexerConfig

logger = logging.getLogger("es_qa")

def _setup_logging(config: ESQAConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("es_qa")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | QA | %(message)s"))
    root_logger.addHandler(console_handler)

def run_qa(config: ESQAConfig | None = None) -> None:
    if config is None:
        config = ESQAConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("Elasticsearch QA Module \u2014 Starting")
    logger.info("=" * 60)
    
    # Pre-requisite: The mock needs data to search over.
    # We silently run the indexer into the global mock.
    logger.info("Initializing Index (Mock Environment Setup)...")
    idx_config = ESIndexerConfig()
    idx_config.use_mock = True
    
    # We intercept the loggers to suppress indexer noise during QA
    logging.getLogger("es_indexer").setLevel(logging.WARNING)
    run_indexer(idx_config)
    client = get_es_client(idx_config)
    
    # 1. Generate Queries
    logger.info("Generating synthetic legal queries...")
    queries = generate_queries(config.chunks_dir, config.queries_per_type)
    logger.info(f"Generated {len(queries)} queries.")
    
    # 2. Execute
    logger.info("Executing queries against Elasticsearch...")
    results = execute_queries(client, config.index_name, queries)
    
    # 3. Calculate Metrics
    metrics = calculate_metrics(results)
    logger.info(f"QA Metrics: {metrics}")
    
    # 4. Report
    generate_reports(config.report_dir, results, metrics)
    
    score = metrics.get("quality_score", 0)
    logger.info("=" * 60)
    logger.info(f"Elasticsearch Quality Score: {score}/100")
    if score < 85:
        logger.warning("Score below threshold. See summary JSON for recommendations.")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_qa()
