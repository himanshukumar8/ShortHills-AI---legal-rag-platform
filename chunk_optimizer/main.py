from __future__ import annotations

import json
import logging
import logging.handlers
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from chunk_optimizer.config import OptimizerConfig
from chunk_optimizer.models import OptimizedChunk
from chunk_optimizer.optimizer import optimize_document_chunks
from chunk_optimizer.writer import write_optimized_chunks
from chunk_optimizer.reporter import generate_reports
from chunk_optimizer.utils import ensure_directory
from semantic_chunker.models import DocumentChunkingResult, ChunkingStatus

logger = logging.getLogger("chunk_optimizer")

def _read_chunks(doc_dir: Path) -> list[OptimizedChunk]:
    chunks_path = doc_dir / "chunks.json"
    if not chunks_path.exists():
        return []
    
    with open(chunks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return [
        OptimizedChunk(
            original_chunk_ids=[c["chunk_id"]],
            **c
        ) for c in data
    ]

def _process_single_document(doc_dir: Path, config: OptimizerConfig) -> DocumentChunkingResult:
    start_time = time.monotonic()
    doc_id = doc_dir.name
    
    try:
        raw_chunks = _read_chunks(doc_dir)
        if not raw_chunks:
            return DocumentChunkingResult(
                document_id=doc_id,
                status=ChunkingStatus.FAILED,
                error_message="chunks.json not found or empty",
                duration_seconds=time.monotonic() - start_time
            )
            
        cat = raw_chunks[0].category
        optimized = optimize_document_chunks(raw_chunks, config)
        write_optimized_chunks(optimized, doc_id, cat, config.output_dir)
        
        return DocumentChunkingResult(
            document_id=doc_id,
            status=ChunkingStatus.SUCCESS,
            chunks=optimized,
            duration_seconds=time.monotonic() - start_time
        )
        
    except Exception as exc:
        logger.error("[%s] Optimization failed: %s", doc_id, exc, exc_info=True)
        return DocumentChunkingResult(
            document_id=doc_id,
            status=ChunkingStatus.FAILED,
            error_message=str(exc),
            duration_seconds=time.monotonic() - start_time
        )

def run_pipeline(config: OptimizerConfig | None = None) -> None:
    if config is None:
        config = OptimizerConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("Adaptive Chunk Optimizer — Starting")
    logger.info("=" * 60)

    start_time = time.monotonic()

    doc_dirs = []
    if config.input_dir.exists():
        for category_dir in config.input_dir.iterdir():
            if category_dir.is_dir():
                for doc_dir in category_dir.iterdir():
                    if doc_dir.is_dir():
                        doc_dirs.append(doc_dir)
                        
    ensure_directory(config.output_dir)
    results = []

    try:
        with ProcessPoolExecutor(max_workers=config.max_workers) as executor:
            future_to_dir = {
                executor.submit(_process_single_document, d, config): d
                for d in doc_dirs
            }

            for future in as_completed(future_to_dir):
                d = future_to_dir[future]
                try:
                    result = future.result()
                    if result.status == ChunkingStatus.SUCCESS:
                        logger.info("[%s] Optimized successfully (%d chunks)", result.document_id, len(result.chunks))
                    else:
                        logger.error("[%s] Optimization failed: %s", result.document_id, result.error_message)
                except Exception as exc:
                    logger.error("Unexpected error for %s: %s", d.name, exc)
                    result = DocumentChunkingResult(
                        document_id=d.name,
                        status=ChunkingStatus.FAILED,
                        error_message=f"Worker failure: {exc}"
                    )
                results.append(result)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        raise

    elapsed = time.monotonic() - start_time
    generate_reports(results, config.report_dir, elapsed)

    logger.info("=" * 60)
    logger.info(
        "Optimization complete in %.1f seconds (%d documents processed)",
        elapsed, len(results)
    )
    logger.info("=" * 60)
    
    # Auto-QA Hook
    logger.info("Triggering Auto-QA over optimized chunks...")
    from chunk_qa import run_qa
    score = run_qa(config.output_dir, "optimized")
    logger.info(f"Final Optimized QA Score: {score}/100")
    if score >= 95:
        logger.info("SUCCESS: Target QA score achieved!")
    else:
        logger.error(f"FAILURE: QA score {score} did not meet target of 95.")

def _setup_logging(config: OptimizerConfig) -> None:
    ensure_directory(config.log_dir)
    root_logger = logging.getLogger("chunk_optimizer")
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(processName)-15s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
