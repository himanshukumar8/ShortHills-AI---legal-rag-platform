"""Report generation for the Corpus Download Pipeline.

Generates two artifacts after a download run:
1. A detailed per-document CSV report (``download_report.csv``).
2. An aggregate JSON summary (``download_summary.json``).

These reports provide auditability and make it easy to diagnose
failures without parsing log files.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any

from corpus_downloader.models import DocumentStatus, DownloadResult
from corpus_downloader.utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_reports(
    results: list[DownloadResult],
    report_dir: Path,
    execution_time_seconds: float,
) -> None:
    """Generate download reports (CSV detail + JSON summary).

    Args:
        results: List of DownloadResult objects from the pipeline run.
        report_dir: Directory to write the report files into.
        execution_time_seconds: Total pipeline wall-clock time in seconds.
    """
    ensure_directory(report_dir)
    _generate_detail_report(results, report_dir)
    _generate_summary_report(results, report_dir, execution_time_seconds)


def _generate_detail_report(
    results: list[DownloadResult],
    report_dir: Path,
) -> None:
    """Generate a per-document CSV report with one row per document.

    Args:
        results: List of DownloadResult objects.
        report_dir: Directory to write the report file.
    """
    report_path = report_dir / "download_report.csv"

    fieldnames = [
        "document_id",
        "status",
        "file_path",
        "checksum",
        "actual_pages",
        "file_size_bytes",
        "error_message",
        "attempts",
        "duration_seconds",
        "duplicate_of",
    ]

    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                "document_id": result.document_id,
                "status": result.status.value,
                "file_path": result.file_path,
                "checksum": result.checksum,
                "actual_pages": result.actual_pages,
                "file_size_bytes": result.file_size_bytes,
                "error_message": result.error_message,
                "attempts": result.attempts,
                "duration_seconds": round(result.duration_seconds, 2),
                "duplicate_of": result.duplicate_of,
            })

    logger.info("Detail report written to %s", report_path)


def _generate_summary_report(
    results: list[DownloadResult],
    report_dir: Path,
    execution_time_seconds: float,
) -> None:
    """Generate an aggregate JSON summary report.

    Args:
        results: List of DownloadResult objects.
        report_dir: Directory to write the report file.
        execution_time_seconds: Total pipeline execution time in seconds.
    """
    report_path = report_dir / "download_summary.json"

    total = len(results)
    downloaded = _count_by_status(results, DocumentStatus.DOWNLOADED)
    skipped = _count_by_status(results, DocumentStatus.SKIPPED)
    failed = _count_by_status(results, DocumentStatus.FAILED)
    duplicates = _count_by_status(results, DocumentStatus.DUPLICATE)

    successful = [
        r for r in results if r.status == DocumentStatus.DOWNLOADED
    ]
    avg_file_size = (
        sum(r.file_size_bytes for r in successful) / len(successful)
        if successful
        else 0.0
    )
    avg_page_count = (
        sum(r.actual_pages for r in successful) / len(successful)
        if successful
        else 0.0
    )

    summary: dict[str, Any] = {
        "total_documents": total,
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "duplicates": duplicates,
        "average_file_size_bytes": round(avg_file_size, 2),
        "average_page_count": round(avg_page_count, 2),
        "execution_time_seconds": round(execution_time_seconds, 2),
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    logger.info("Summary report written to %s", report_path)
    logger.info(
        "Pipeline summary: %d total | %d downloaded | %d skipped | "
        "%d failed | %d duplicates | %.1fs elapsed",
        total,
        downloaded,
        skipped,
        failed,
        duplicates,
        execution_time_seconds,
    )


def _count_by_status(
    results: list[DownloadResult],
    status: DocumentStatus,
) -> int:
    """Count results matching a given status.

    Args:
        results: List of DownloadResult objects.
        status: The DocumentStatus to count.

    Returns:
        The number of results with the given status.
    """
    return sum(1 for r in results if r.status == status)
