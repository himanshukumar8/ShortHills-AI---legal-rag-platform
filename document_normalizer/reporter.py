from __future__ import annotations

"""Reporting logic for the Normalization Pipeline."""

import csv
import json
import logging
from pathlib import Path

from document_normalizer.models import NormalizationResult, NormalizationStatus
from document_normalizer.utils import ensure_directory

logger = logging.getLogger(__name__)

def generate_reports(results: list[NormalizationResult], report_dir: Path, elapsed_time: float) -> None:
    """Generate summary and detailed reports of the normalization run."""
    ensure_directory(report_dir)
    
    # Detailed CSV Report
    csv_path = report_dir / "normalization_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["document_id", "status", "pages_processed", "characters_removed", "duration_seconds", "warnings", "error_message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                "document_id": r.document_id,
                "status": r.status.value,
                "pages_processed": r.pages_processed,
                "characters_removed": r.characters_removed,
                "duration_seconds": round(r.duration_seconds, 2),
                "warnings": "; ".join(r.warnings),
                "error_message": r.error_message
            })
            
    logger.info("Normalization detail report written to %s", csv_path)
    
    # Summary JSON Report
    successes = sum(1 for r in results if r.status == NormalizationStatus.SUCCESS)
    warnings = sum(1 for r in results if r.status == NormalizationStatus.WARNING)
    failures = sum(1 for r in results if r.status == NormalizationStatus.FAILED)
    
    total_pages = sum(r.pages_processed for r in results)
    total_chars_removed = sum(r.characters_removed for r in results)
    
    summary = {
        "total_documents": len(results),
        "success": successes,
        "warnings": warnings,
        "failed": failures,
        "total_pages_processed": total_pages,
        "total_characters_removed": total_chars_removed,
        "execution_time_seconds": round(elapsed_time, 2)
    }
    
    json_path = report_dir / "normalization_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    logger.info("Normalization summary report written to %s", json_path)
    logger.info(
        "Normalization summary: %d total | %d success | %d warnings | %d failed | %.1fs elapsed",
        len(results), successes, warnings, failures, elapsed_time
    )
