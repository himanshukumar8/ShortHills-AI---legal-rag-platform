from __future__ import annotations

"""Pipeline orchestrator for the Corpus Download Pipeline.

Coordinates the full download lifecycle:
1. Load configuration and read the manifest.
2. Select documents (all, or a per-category sample in test mode).
3. Process each document concurrently via ThreadPoolExecutor:
   a. Skip if already downloaded and valid.
   b. Download with manual retries and exponential backoff.
   c. Validate the PDF.
   d. Compute SHA-256 checksum.
   e. Check for cross-document duplicates.
4. Update the manifest CSV with results.
5. Generate detail and summary reports.

Design Decisions:
    - Manual retry loop instead of urllib3.Retry: Gives the orchestrator
      full control over logging each attempt, counting attempts accurately,
      and deciding which error classes warrant a retry.
    - ThreadPoolExecutor over asyncio: Simpler to reason about for I/O-bound
      work with 100 documents. The overhead of an event loop and aiohttp
      is not justified at this scale.
    - One failure never kills the pipeline: Each document is processed
      independently, and exceptions are caught and recorded as FAILED results.
"""

import logging
import logging.handlers
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from corpus_downloader.config import DownloaderConfig
from corpus_downloader.downloader import create_session, download_document
from corpus_downloader.duplicate_detector import DuplicateDetector
from corpus_downloader.exceptions import CorpusDownloaderError, DownloadError
from corpus_downloader.hash_generator import compute_sha256
from corpus_downloader.manifest_reader import read_manifest
from corpus_downloader.manifest_updater import update_manifest
from corpus_downloader.models import (
    DocumentCategory,
    DocumentRecord,
    DocumentStatus,
    DownloadResult,
)
from corpus_downloader.reporter import generate_reports
from corpus_downloader.utils import build_file_path, ensure_directory
from corpus_downloader.validator import validate_pdf

logger = logging.getLogger("corpus_downloader")

# Exponential backoff base for retries (seconds).
_BACKOFF_BASE: float = 2.0


def run_pipeline(config: DownloaderConfig | None = None) -> None:
    """Execute the full corpus download pipeline.

    This is the main entry point. It reads configuration, loads the
    manifest, processes documents concurrently, and produces updated
    manifest and reports.

    Args:
        config: Optional pre-built configuration. If None, a new
            DownloaderConfig is created from environment/defaults.
    """
    if config is None:
        config = DownloaderConfig()

    _setup_logging(config)

    logger.info("=" * 60)
    logger.info("Corpus Download Pipeline — Starting")
    logger.info("=" * 60)
    logger.info("Configuration:")
    logger.info("  Manifest:      %s", config.manifest_path)
    logger.info("  Download dir:  %s", config.download_dir)
    logger.info("  Max workers:   %d", config.max_workers)
    logger.info("  Max retries:   %d", config.max_retries)
    logger.info("  Request delay: %.1fs", config.request_delay_seconds)
    logger.info("  Test mode:     %s", config.test_mode)

    start_time = time.monotonic()

    # 1. Read manifest
    records = read_manifest(config.manifest_path)
    logger.info("Manifest loaded: %d documents", len(records))

    # 2. Select documents
    selected = _select_documents(records, config)
    logger.info("Documents to process: %d", len(selected))

    # 3. Create output directories
    _create_output_directories(config)

    # 4. Process documents concurrently
    duplicate_detector = DuplicateDetector()
    results = _process_all_documents(selected, config, duplicate_detector)

    # 5. Update manifest
    results_map = {r.document_id: r for r in results}
    update_manifest(config.manifest_path, results_map)

    # 6. Generate reports
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
    records: list[DocumentRecord],
    config: DownloaderConfig,
) -> list[DocumentRecord]:
    """Select documents to process based on the current mode.

    In test mode, selects one document per category to verify the
    pipeline end-to-end before scaling to the full corpus.

    Args:
        records: All document records from the manifest.
        config: The downloader configuration.

    Returns:
        The filtered list of documents to process.
    """
    if not config.test_mode:
        return records

    logger.info("TEST MODE: selecting one document per category")

    selected: list[DocumentRecord] = []
    seen_categories: set[str] = set()

    # Iterate through categories in a deterministic order
    category_order = [cat.value for cat in DocumentCategory]

    for category in category_order:
        if category in seen_categories:
            continue
        for record in records:
            if record.category == category:
                selected.append(record)
                seen_categories.add(category)
                logger.info(
                    "  [TEST] Selected %s: %s",
                    record.document_id,
                    record.title,
                )
                break

    return selected


def _create_output_directories(config: DownloaderConfig) -> None:
    """Create all required output directories.

    Uses the canonical category_to_folder mapping from utils to avoid
    duplicating the category → folder name logic.

    Args:
        config: The downloader configuration.
    """
    from corpus_downloader.utils import category_to_folder

    for category in DocumentCategory:
        folder_name = category_to_folder(category.value)
        ensure_directory(config.download_dir / folder_name)

    ensure_directory(config.log_dir)
    ensure_directory(config.report_dir)


def _process_all_documents(
    records: list[DocumentRecord],
    config: DownloaderConfig,
    duplicate_detector: DuplicateDetector,
) -> list[DownloadResult]:
    """Process all selected documents using a thread pool.

    Each document is processed independently. Failures are caught
    and recorded — one document's failure never terminates the pipeline.

    Args:
        records: Documents to process.
        config: The downloader configuration.
        duplicate_detector: Shared duplicate detector instance.

    Returns:
        A list of DownloadResult objects, one per document.
    """
    results: list[DownloadResult] = []
    session = create_session(config)

    try:
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            future_to_record = {
                executor.submit(
                    _process_single_document,
                    record,
                    session,
                    config,
                    duplicate_detector,
                ): record
                for record in records
            }

            for future in as_completed(future_to_record):
                record = future_to_record[future]
                try:
                    result = future.result()
                except Exception as exc:
                    logger.error(
                        "[%s] Unexpected error: %s",
                        record.document_id,
                        exc,
                        exc_info=True,
                    )
                    result = DownloadResult(
                        document_id=record.document_id,
                        status=DocumentStatus.FAILED,
                        error_message=f"Unexpected error: {exc}",
                    )
                results.append(result)
    finally:
        session.close()

    return results


def _process_single_document(
    record: DocumentRecord,
    session: requests.Session,
    config: DownloaderConfig,
    duplicate_detector: DuplicateDetector,
) -> DownloadResult:
    """Process a single document through the full download lifecycle.

    Steps:
    1. Check if already downloaded → SKIP.
    2. Download with retries → file on disk.
    3. Validate PDF → integrity confirmed.
    4. Compute checksum → SHA-256 digest.
    5. Check for duplicates → flag if found.

    Args:
        record: The document to process.
        session: The requests session for HTTP calls.
        config: The downloader configuration.
        duplicate_detector: The shared duplicate detector.

    Returns:
        A DownloadResult summarizing the outcome.
    """
    start_time = time.monotonic()

    # Determine the target file path
    file_path = build_file_path(
        config.download_dir,
        record.category,
        record.document_id,
        record.title,
    )
    ensure_directory(file_path.parent)
    relative_path = str(file_path)

    # 1. Skip if already downloaded and validated
    if _should_skip(record, file_path):
        logger.info("[%s] Skipping: already downloaded", record.document_id)
        return DownloadResult(
            document_id=record.document_id,
            status=DocumentStatus.SKIPPED,
            file_path=relative_path,
            checksum=record.checksum,
            actual_pages=record.actual_pages or 0,
            file_size_bytes=record.file_size_bytes or 0,
            duration_seconds=time.monotonic() - start_time,
        )

    # 2. Download with retries
    last_error = ""
    attempts = 0

    for attempt in range(1, config.max_retries + 1):
        attempts = attempt
        try:
            logger.info(
                "[%s] Download attempt %d/%d: %s",
                record.document_id,
                attempt,
                config.max_retries,
                record.pdf_url,
            )
            download_document(
                session,
                record.pdf_url,
                file_path,
                record.document_id,
                config,
            )

            # 3. Validate
            validation = validate_pdf(file_path, record.document_id)
            if not validation.is_valid:
                last_error = f"Validation failed: {validation.error_message}"
                logger.warning(
                    "[%s] Attempt %d — %s",
                    record.document_id,
                    attempt,
                    last_error,
                )
                # Delete the invalid file so the next attempt starts clean
                if file_path.exists():
                    file_path.unlink()
                if attempt < config.max_retries:
                    _backoff(attempt, record.document_id)
                continue

            # 4. Compute checksum
            checksum = compute_sha256(file_path, config.stream_chunk_size)

            # 5. Check for duplicates
            duplicate_of = duplicate_detector.check(
                checksum, record.document_id
            )
            if duplicate_of is not None:
                logger.info(
                    "[%s] Marked as duplicate of [%s]",
                    record.document_id,
                    duplicate_of,
                )
                return DownloadResult(
                    document_id=record.document_id,
                    status=DocumentStatus.DUPLICATE,
                    file_path=relative_path,
                    checksum=checksum,
                    actual_pages=validation.actual_pages,
                    file_size_bytes=validation.file_size_bytes,
                    attempts=attempts,
                    duration_seconds=time.monotonic() - start_time,
                    duplicate_of=duplicate_of,
                )

            # Success
            logger.info(
                "[%s] Successfully processed: %d pages, %s bytes",
                record.document_id,
                validation.actual_pages,
                f"{validation.file_size_bytes:,}",
            )
            return DownloadResult(
                document_id=record.document_id,
                status=DocumentStatus.DOWNLOADED,
                file_path=relative_path,
                checksum=checksum,
                actual_pages=validation.actual_pages,
                file_size_bytes=validation.file_size_bytes,
                attempts=attempts,
                duration_seconds=time.monotonic() - start_time,
            )

        except DownloadError as exc:
            last_error = str(exc)
            logger.warning(
                "[%s] Attempt %d failed: %s",
                record.document_id,
                attempt,
                last_error,
            )
            if attempt < config.max_retries:
                _backoff(attempt, record.document_id)

        except CorpusDownloaderError as exc:
            last_error = str(exc)
            logger.error(
                "[%s] Non-retryable error: %s", record.document_id, last_error
            )
            break

    # All retries exhausted
    logger.error(
        "[%s] Failed after %d attempts: %s",
        record.document_id,
        attempts,
        last_error,
    )
    return DownloadResult(
        document_id=record.document_id,
        status=DocumentStatus.FAILED,
        error_message=last_error,
        attempts=attempts,
        duration_seconds=time.monotonic() - start_time,
    )


def _should_skip(record: DocumentRecord, file_path: Path) -> bool:
    """Determine whether a document should be skipped.

    A document is skipped if:
    - Its status is already DOWNLOADED in the manifest, AND
    - The local file exists on disk, AND
    - A checksum is recorded in the manifest.

    Args:
        record: The document record from the manifest.
        file_path: The expected local file path.

    Returns:
        True if the document should be skipped.
    """
    return (
        record.document_status == DocumentStatus.DOWNLOADED.value
        and file_path.exists()
        and bool(record.checksum)
    )


def _backoff(attempt: int, document_id: str) -> None:
    """Apply exponential backoff between retry attempts.

    Wait time: ``_BACKOFF_BASE ** attempt`` seconds.
    Attempt 1 → 2s, attempt 2 → 4s, attempt 3 → 8s, etc.

    Args:
        attempt: The current attempt number (1-indexed).
        document_id: The document ID (for logging).
    """
    wait_seconds = _BACKOFF_BASE ** attempt
    logger.info(
        "[%s] Backing off %.1f seconds before retry",
        document_id,
        wait_seconds,
    )
    time.sleep(wait_seconds)


def _setup_logging(config: DownloaderConfig) -> None:
    """Configure structured logging for the pipeline.

    Sets up two handlers:
    1. Console handler (INFO level) for real-time progress.
    2. Rotating file handler (DEBUG level) for full audit trail.

    Args:
        config: The downloader configuration (provides log_dir).
    """
    ensure_directory(config.log_dir)

    root_logger = logging.getLogger("corpus_downloader")
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers to avoid duplicate output on re-runs
    root_logger.handlers.clear()

    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # File handler (rotating, 10 MB max, 3 backups)
    log_file = config.log_dir / "downloader.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    logger.debug("Logging initialized. File: %s", log_file)
