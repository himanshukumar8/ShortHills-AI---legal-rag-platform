from __future__ import annotations

"""Pipeline orchestrator for the Document Normalization Pipeline.

1. Load configuration.
2. Read parsed documents from data/processed.
3. Process each document concurrently using ProcessPoolExecutor.
4. Generate normalization reports.
"""

import json
import logging
import logging.handlers
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from pdf_parser.models import ParsedDocument, DocumentMetadata, PageExtract, ParsingStatistics
from document_normalizer.config import NormalizerConfig
from document_normalizer.models import NormalizationResult, NormalizationStatus
from document_normalizer.normalizer import normalize_document
from document_normalizer.reporter import generate_reports
from document_normalizer.writer import write_normalized_document
from document_normalizer.utils import ensure_directory

logger = logging.getLogger("document_normalizer")


def _read_parsed_document(doc_dir: Path) -> ParsedDocument | None:
    """Reconstruct a ParsedDocument from disk."""
    doc_json_path = doc_dir / "document.json"
    if not doc_json_path.exists():
        return None
        
    with open(doc_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    metadata = DocumentMetadata(**data["metadata"])
    pages = [PageExtract(**p) for p in data["pages"]]
    stats = ParsingStatistics(**data["statistics"])
    
    return ParsedDocument(
        metadata=metadata,
        pages=pages,
        full_text=data.get("full_text", ""),
        statistics=stats,
        processing_info=data.get("processing_info", {})
    )


def _process_single_document(doc_dir: Path, config: NormalizerConfig) -> NormalizationResult:
    """Worker function to read, normalize, and write a single document."""
    start_time = time.monotonic()
    doc_id = doc_dir.name
    
    try:
        parsed_doc = _read_parsed_document(doc_dir)
        if not parsed_doc:
            return NormalizationResult(
                document_id=doc_id,
                status=NormalizationStatus.FAILED,
                error_message="document.json not found",
                duration_seconds=time.monotonic() - start_time
            )
            
        norm_doc = normalize_document(parsed_doc)
        write_normalized_document(norm_doc, config.output_dir)
        
        status = NormalizationStatus.WARNING if norm_doc.processing_info.get("warnings") else NormalizationStatus.SUCCESS
        
        return NormalizationResult(
            document_id=doc_id,
            status=status,
            pages_processed=len(norm_doc.pages),
            characters_removed=norm_doc.statistics.characters_removed,
            warnings=norm_doc.processing_info.get("warnings", []),
            duration_seconds=time.monotonic() - start_time
        )
        
    except Exception as exc:
        logger.error("[%s] Normalization failed: %s", doc_id, exc, exc_info=True)
        return NormalizationResult(
            document_id=doc_id,
            status=NormalizationStatus.FAILED,
            error_message=str(exc),
            duration_seconds=time.monotonic() - start_time
        )


def run_pipeline(config: NormalizerConfig | None = None) -> None:
    """Execute the full normalization pipeline."""
    if config is None:
        config = NormalizerConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("Document Normalization Pipeline — Starting")
    logger.info("=" * 60)

    start_time = time.monotonic()

    # 1. Discover documents
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

    logger.info("Documents to normalize: %d", len(doc_dirs))

    ensure_directory(config.output_dir)

    results: list[NormalizationResult] = []

    # 2. Process concurrently
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
                    if result.status == NormalizationStatus.SUCCESS:
                        logger.info("[%s] Normalized successfully", result.document_id)
                    elif result.status == NormalizationStatus.WARNING:
                        logger.warning("[%s] Normalized with warnings: %s", result.document_id, "; ".join(result.warnings))
                    else:
                        logger.error("[%s] Normalization failed: %s", result.document_id, result.error_message)
                except Exception as exc:
                    logger.error("Unexpected error for %s: %s", d.name, exc)
                    result = NormalizationResult(
                        document_id=d.name,
                        status=NormalizationStatus.FAILED,
                        error_message=f"Worker failure: {exc}"
                    )
                results.append(result)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        raise

    # 3. Generate reports
    elapsed = time.monotonic() - start_time
    generate_reports(results, config.report_dir, elapsed)

    logger.info("=" * 60)
    logger.info(
        "Pipeline complete in %.1f seconds (%d documents processed)",
        elapsed,
        len(results),
    )
    logger.info("=" * 60)


def _setup_logging(config: NormalizerConfig) -> None:
    ensure_directory(config.log_dir)
    root_logger = logging.getLogger("document_normalizer")
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

    log_file = config.log_dir / "normalizer.log"
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
