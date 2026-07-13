from __future__ import annotations

"""Report generation for the PDF Parser Pipeline.

Produces audit artifacts:
1. parsing_report.csv (per-document detail)
2. parsing_summary.json (aggregate metrics)
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any

from pdf_parser.models import ParsingResult, ParsingStatus
from pdf_parser.utils import ensure_directory

logger = logging.getLogger(__name__)


def generate_reports(
    results: list[ParsingResult],
    report_dir: Path,
    execution_time_seconds: float,
) -> None:
    """Generate parsing reports.

    Args:
        results: List of ParsingResult objects from the pipeline run.
        report_dir: Directory to write the reports into.
        execution_time_seconds: Total wall-clock time in seconds.
    """
    ensure_directory(report_dir)
    _generate_detail_report(results, report_dir)
    _generate_summary_report(results, report_dir, execution_time_seconds)


def _generate_detail_report(results: list[ParsingResult], report_dir: Path) -> None:
    report_path = report_dir / "parsing_report.csv"
    
    fieldnames = [
        "document_id",
        "status",
        "pages_processed",
        "warnings",
        "error_message",
        "duration_seconds",
    ]
    
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                "document_id": result.document_id,
                "status": result.status.value,
                "pages_processed": result.pages_processed,
                "warnings": "; ".join(result.warnings) if result.warnings else "",
                "error_message": result.error_message,
                "duration_seconds": round(result.duration_seconds, 2),
            })
            
    logger.info("Parsing detail report written to %s", report_path)


def _generate_summary_report(
    results: list[ParsingResult], report_dir: Path, execution_time_seconds: float
) -> None:
    report_path = report_dir / "parsing_summary.json"
    
    total = len(results)
    success = sum(1 for r in results if r.status == ParsingStatus.SUCCESS)
    warnings = sum(1 for r in results if r.status == ParsingStatus.WARNING)
    failed = sum(1 for r in results if r.status == ParsingStatus.FAILED)
    
    total_pages = sum(r.pages_processed for r in results)
    
    successful_results = [r for r in results if r.status in (ParsingStatus.SUCCESS, ParsingStatus.WARNING)]
    avg_pages = (total_pages / len(successful_results)) if successful_results else 0.0
    
    summary: dict[str, Any] = {
        "total_documents": total,
        "success": success,
        "warnings": warnings,
        "failed": failed,
        "total_pages_processed": total_pages,
        "average_pages_per_doc": round(avg_pages, 2),
        "execution_time_seconds": round(execution_time_seconds, 2),
    }
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    logger.info("Parsing summary report written to %s", report_path)
    logger.info(
        "Parsing summary: %d total | %d success | %d warnings | %d failed | %.1fs elapsed",
        total,
        success,
        warnings,
        failed,
        execution_time_seconds,
    )
