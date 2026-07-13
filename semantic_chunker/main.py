from __future__ import annotations

import json
import logging
import logging.handlers
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from document_normalizer.models import NormalizedDocument, DocumentMetadata, NormalizedPage, NormalizationStatistics
from semantic_chunker.config import ChunkerConfig
from semantic_chunker.models import DocumentChunkingResult, ChunkingStatus
from semantic_chunker.analyzer import analyze_and_chunk
from semantic_chunker.validator import validate_chunks
from semantic_chunker.writer import write_chunks
from semantic_chunker.reporter import generate_reports
from semantic_chunker.utils import ensure_directory

logger = logging.getLogger("semantic_chunker")

def _read_normalized_document(doc_dir: Path) -> NormalizedDocument | None:
    doc_json_path = doc_dir / "normalized_document.json"
    if not doc_json_path.exists():
        return None
        
    with open(doc_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    metadata = DocumentMetadata(**data["metadata"])
    pages = [NormalizedPage(**p) for p in data["pages"]]
    stats = NormalizationStatistics(**data["statistics"])
    
    return NormalizedDocument(
        metadata=metadata,
        pages=pages,
        full_text=data.get("full_text", ""),
        statistics=stats,
        processing_info=data.get("processing_info", {})
    )

def _process_single_document(doc_dir: Path, config: ChunkerConfig) -> DocumentChunkingResult:
    start_time = time.monotonic()
    doc_id = doc_dir.name
    
    try:
        norm_doc = _read_normalized_document(doc_dir)
        if not norm_doc:
            return DocumentChunkingResult(
                document_id=doc_id,
                status=ChunkingStatus.FAILED,
                error_message="normalized_document.json not found",
                duration_seconds=time.monotonic() - start_time
            )
            
        chunks = analyze_and_chunk(norm_doc)
        warnings = validate_chunks(chunks, doc_id)
        write_chunks(chunks, doc_id, norm_doc.metadata.category, config.output_dir)
        
        status = ChunkingStatus.WARNING if warnings else ChunkingStatus.SUCCESS
        
        return DocumentChunkingResult(
            document_id=doc_id,
            status=status,
            chunks=chunks,
            warnings=warnings,
            duration_seconds=time.monotonic() - start_time
        )
        
    except Exception as exc:
        logger.error("[%s] Chunking failed: %s", doc_id, exc, exc_info=True)
        return DocumentChunkingResult(
            document_id=doc_id,
            status=ChunkingStatus.FAILED,
            error_message=str(exc),
            duration_seconds=time.monotonic() - start_time
        )

def run_pipeline(config: ChunkerConfig | None = None) -> None:
    if config is None:
        config = ChunkerConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("Semantic Chunking Pipeline — Starting")
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

    results: list[DocumentChunkingResult] = []

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
                        logger.info("[%s] Chunked successfully (%d chunks)", result.document_id, len(result.chunks))
                    elif result.status == ChunkingStatus.WARNING:
                        logger.warning("[%s] Chunked with warnings: %s", result.document_id, "; ".join(result.warnings))
                    else:
                        logger.error("[%s] Chunking failed: %s", result.document_id, result.error_message)
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
        "Pipeline complete in %.1f seconds (%d documents processed)",
        elapsed, len(results)
    )
    logger.info("=" * 60)

def _setup_logging(config: ChunkerConfig) -> None:
    ensure_directory(config.log_dir)
    root_logger = logging.getLogger("semantic_chunker")
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

    log_file = config.log_dir / "chunker.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

if __name__ == "__main__":
    run_pipeline()
