from __future__ import annotations

import json
import logging
import logging.handlers
import sys
import time
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

from embedding_pipeline.config import EmbeddingConfig
from embedding_pipeline.models import DocumentEmbeddingResult, EmbeddingStatus, EmbeddingRecord
from embedding_pipeline.generator import get_provider
from embedding_pipeline.validator import validate_embeddings
from embedding_pipeline.writer import write_embeddings
from embedding_pipeline.reporter import generate_reports
from embedding_pipeline.utils import ensure_directory, generate_category_slug

logger = logging.getLogger("embedding_pipeline")

def _chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def _read_optimized_chunks(doc_dir: Path) -> list[dict]:
    chunks_path = doc_dir / "chunks.json"
    if not chunks_path.exists():
        return []
    with open(chunks_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _is_resumable(doc_id: str, category: str, expected_count: int, config: EmbeddingConfig) -> bool:
    """Check if the document has already been fully embedded (Resumability logic)."""
    slug = generate_category_slug(category)
    embed_file = config.output_dir / slug / doc_id / "embeddings.json"
    if embed_file.exists():
        try:
            with open(embed_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all chunks were processed
                if len(data) == expected_count:
                    return True
        except Exception:
            return False
    return False

def _process_single_document(doc_dir: Path, config: EmbeddingConfig) -> DocumentEmbeddingResult:
    start_time = time.monotonic()
    doc_id = doc_dir.name
    
    try:
        chunks = _read_optimized_chunks(doc_dir)
        if not chunks:
            return DocumentEmbeddingResult(doc_id, EmbeddingStatus.FAILED, error_message="optimized chunks not found")
            
        category = chunks[0]["category"]
        
        # Resumability check
        if _is_resumable(doc_id, category, len(chunks), config):
            return DocumentEmbeddingResult(
                document_id=doc_id,
                status=EmbeddingStatus.SKIPPED,
                chunks_embedded=0,
                duration_seconds=time.monotonic() - start_time
            )
            
        # Instantiate provider per process
        provider = get_provider(config.provider, config.model_name, config.embedding_dimension)
        
        all_embeddings = []
        texts = [c["text"] for c in chunks]
        
        # Batching logic
        for batch_idx, text_batch in enumerate(_chunk_list(texts, config.batch_size)):
            for attempt in range(config.max_retries):
                try:
                    vectors = provider.embed_batch(text_batch)
                    
                    # Mathematical validation
                    validate_embeddings(vectors, config.embedding_dimension, doc_id)
                    all_embeddings.extend(vectors)
                    break
                except Exception as e:
                    if attempt == config.max_retries - 1:
                        raise e
                    logger.warning("[%s] Batch %d failed (attempt %d). Retrying... Error: %s", doc_id, batch_idx, attempt + 1, e)
                    time.sleep(2 ** attempt) # Exponential backoff
                    
        # Sanity check parity
        if len(all_embeddings) != len(chunks):
            raise ValueError(f"Parity error: Input chunks={len(chunks)}, Embeddings={len(all_embeddings)}")
            
        # Assemble records
        records = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for c, vec in zip(chunks, all_embeddings):
            metadata = {
                "parent_section": c.get("parent_section"),
                "page_start": c.get("page_start"),
                "hierarchy_level": c.get("hierarchy_level"),
                "cross_references": c.get("cross_references", [])
            }
            records.append(EmbeddingRecord(
                chunk_id=c["chunk_id"],
                chunk_hash=c["chunk_hash"],
                embedding_model=config.model_name,
                embedding_dimension=config.embedding_dimension,
                embedding_vector=vec,
                metadata=metadata,
                generation_timestamp=timestamp
            ))
            
        write_embeddings(records, doc_id, category, config.output_dir)
        
        return DocumentEmbeddingResult(
            document_id=doc_id,
            status=EmbeddingStatus.SUCCESS,
            chunks_embedded=len(records),
            duration_seconds=time.monotonic() - start_time
        )
        
    except Exception as exc:
        logger.error("[%s] Embedding failed: %s", doc_id, exc)
        return DocumentEmbeddingResult(
            document_id=doc_id,
            status=EmbeddingStatus.FAILED,
            error_message=str(exc),
            duration_seconds=time.monotonic() - start_time
        )

def run_pipeline(config: EmbeddingConfig | None = None) -> None:
    if config is None:
        config = EmbeddingConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("Embedding Pipeline — Starting")
    logger.info("Provider: %s | Model: %s | Dim: %d", config.provider, config.model_name, config.embedding_dimension)
    logger.info("=" * 60)

    start_time = time.monotonic()

    doc_dirs = []
    if config.input_dir.exists():
        for category_dir in config.input_dir.iterdir():
            if category_dir.is_dir():
                for doc_dir in category_dir.iterdir():
                    if doc_dir.is_dir():
                        doc_dirs.append(doc_dir)
                        
    if config.test_mode:
        logger.info("TEST MODE: Limiting to %d documents", config.test_sample_size)
        doc_dirs = doc_dirs[:config.test_sample_size]

    ensure_directory(config.output_dir)
    results = []

    try:
        # Use ThreadPoolExecutor for mocked/remote network APIs, ProcessPoolExecutor for heavy local compute.
        # Since 'mock' uses time.sleep, ThreadPoolExecutor is fine.
        ExecutorClass = ThreadPoolExecutor if config.provider in ("mock", "openai") else ProcessPoolExecutor
        
        with ExecutorClass(max_workers=config.parallel_workers) as executor:
            future_to_dir = {
                executor.submit(_process_single_document, d, config): d
                for d in doc_dirs
            }

            for future in as_completed(future_to_dir):
                d = future_to_dir[future]
                try:
                    result = future.result()
                    if result.status == EmbeddingStatus.SUCCESS:
                        logger.info("[%s] Embedded successfully (%d vectors)", result.document_id, result.chunks_embedded)
                    elif result.status == EmbeddingStatus.SKIPPED:
                        logger.info("[%s] SKIPPED (already embedded)", result.document_id)
                    else:
                        logger.error("[%s] Embedding failed: %s", result.document_id, result.error_message)
                except Exception as exc:
                    logger.error("Unexpected error for %s: %s", d.name, exc)
                    result = DocumentEmbeddingResult(
                        document_id=d.name,
                        status=EmbeddingStatus.FAILED,
                        error_message=f"Worker failure: {exc}"
                    )
                results.append(result)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        raise

    elapsed = time.monotonic() - start_time
    generate_reports(results, config.report_dir, elapsed, config)

    logger.info("=" * 60)
    logger.info(
        "Pipeline complete in %.1f seconds (%d processed)",
        elapsed, len(results)
    )
    logger.info("=" * 60)

def _setup_logging(config: EmbeddingConfig) -> None:
    ensure_directory(config.log_dir)
    root_logger = logging.getLogger("embedding_pipeline")
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
