from __future__ import annotations

"""Pipeline orchestrator for the PDF Parser Pipeline.

Coordinates the full parsing lifecycle:
1. Load configuration and read the manifest.
2. Select documents (must be DOWNLOADED; test mode samples 5 documents).
3. Process each document concurrently using ProcessPoolExecutor.
4. Generate parsing reports.
"""

import logging
import logging.handlers
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from corpus_downloader.manifest_reader import read_manifest
from corpus_downloader.models import DocumentRecord, DocumentStatus
from pdf_parser.config import ParserConfig
from pdf_parser.models import ParsingResult, ParsingStatus
from pdf_parser.parser import parse_document
from pdf_parser.reporter import generate_reports
from pdf_parser.utils import ensure_directory

logger = logging.getLogger("pdf_parser")


def run_pipeline(config: ParserConfig | None = None) -> None:
    """Execute the full PDF parsing pipeline.

    Args:
        config: Optional pre-built configuration.
    """
    if config is None:
        config = ParserConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("PDF Parser Pipeline — Starting")
    logger.info("=" * 60)
    logger.info("Configuration:")
    logger.info("  Manifest:      %s", config.manifest_path)
    logger.info("  Input dir:     %s", config.input_dir)
    logger.info("  Output dir:    %s", config.output_dir)
    logger.info("  Max workers:   %d", config.max_workers)
    logger.info("  Test mode:     %s", config.test_mode)

    start_time = time.monotonic()

    # 1. Read manifest
    records = read_manifest(config.manifest_path)
    
    # 2. Select documents
    selected = _select_documents(records, config)
    logger.info("Documents to parse: %d", len(selected))

    # 3. Create output directory
    ensure_directory(config.output_dir)

    # 4. Process documents concurrently (CPU-bound -> ProcessPool)
    results = _process_all_documents(selected, config)

    # 5. Generate reports
    elapsed = time.monotonic() - start_time
    generate_reports(results, config.report_dir, elapsed)

    logger.info("=" * 60)
    logger.info(
        "Pipeline complete in %.1f seconds (%d documents processed)",
        elapsed,
        len(results),
    )
    logger.info("=" * 60)


def _select_documents(
    records: list[DocumentRecord], config: ParserConfig
) -> list[DocumentRecord]:
    """Select documents to process.

    Filters for DOWNLOADED documents. If test_mode is True, selects
    up to `test_sample_size` documents (one per category if possible).
    """
    # Only process documents that are downloaded or skipped (already on disk)
    valid_statuses = {DocumentStatus.DOWNLOADED.value, DocumentStatus.SKIPPED.value}
    downloaded = [
        r for r in records 
        if r.document_status in valid_statuses
    ]
    
    if not config.test_mode:
        return downloaded

    logger.info("TEST MODE: Selecting up to %d documents", config.test_sample_size)
    
    selected: list[DocumentRecord] = []
    seen_categories: set[str] = set()

    # Try to get one from each category first
    for record in downloaded:
        if record.category not in seen_categories:
            selected.append(record)
            seen_categories.add(record.category)
            logger.info("  [TEST] Selected %s: %s", record.document_id, record.title)
            if len(selected) >= config.test_sample_size:
                return selected
                
    # If we still need more to hit sample size, just pick the rest
    for record in downloaded:
        if record not in selected:
            selected.append(record)
            logger.info("  [TEST] Selected %s: %s", record.document_id, record.title)
            if len(selected) >= config.test_sample_size:
                break

    return selected


def _process_all_documents(
    records: list[DocumentRecord], config: ParserConfig
) -> list[ParsingResult]:
    """Process all selected documents using a process pool."""
    results: list[ParsingResult] = []
    
    # Parsing is CPU-bound, so we use ProcessPoolExecutor.
    # Passing Pydantic-settings into processes can sometimes be tricky with pickle,
    # but BaseSettings is generally picklable.
    
    try:
        with ProcessPoolExecutor(max_workers=config.max_workers) as executor:
            future_to_record = {
                executor.submit(parse_document, record, config): record
                for record in records
            }

            for future in as_completed(future_to_record):
                record = future_to_record[future]
                try:
                    result = future.result()
                    if result.status == ParsingStatus.SUCCESS:
                        logger.info("[%s] Parsed successfully", record.document_id)
                    elif result.status == ParsingStatus.WARNING:
                        logger.warning(
                            "[%s] Parsed with warnings: %s", 
                            record.document_id, 
                            "; ".join(result.warnings)
                        )
                    else:
                        logger.error("[%s] Parsing failed: %s", record.document_id, result.error_message)
                        
                except Exception as exc:
                    logger.error(
                        "[%s] Unexpected error in worker: %s",
                        record.document_id,
                        exc,
                        exc_info=True,
                    )
                    result = ParsingResult(
                        document_id=record.document_id,
                        status=ParsingStatus.FAILED,
                        error_message=f"Worker failure: {exc}",
                    )
                results.append(result)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        raise

    return results


def _setup_logging(config: ParserConfig) -> None:
    """Configure structured logging."""
    ensure_directory(config.log_dir)

    root_logger = logging.getLogger("pdf_parser")
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

    log_file = config.log_dir / "parser.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    logger.debug("Logging initialized. File: %s", log_file)
