from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from dataclasses import asdict
from embedding_pipeline.models import DocumentEmbeddingResult, EmbeddingStatus, EmbeddingSummary
from embedding_pipeline.utils import ensure_directory

logger = logging.getLogger(__name__)

def generate_reports(results: list[DocumentEmbeddingResult], report_dir: Path, elapsed_time: float, config) -> None:
    ensure_directory(report_dir)
    
    csv_path = report_dir / "embedding_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["document_id", "status", "chunks_embedded", "duration_seconds", "error_message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                "document_id": r.document_id,
                "status": r.status.value,
                "chunks_embedded": r.chunks_embedded,
                "duration_seconds": round(r.duration_seconds, 2),
                "error_message": r.error_message
            })
            
    logger.info("Embedding detail report written to %s", csv_path)
    
    successes = sum(1 for r in results if r.status == EmbeddingStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == EmbeddingStatus.FAILED)
    skipped = sum(1 for r in results if r.status == EmbeddingStatus.SKIPPED)
    total_embedded = sum(r.chunks_embedded for r in results)
    
    avg_latency = 0.0
    processed_runs = [r.duration_seconds for r in results if r.status == EmbeddingStatus.SUCCESS]
    if processed_runs:
        avg_latency = sum(processed_runs) / len(processed_runs)
        
    summary = EmbeddingSummary(
        documents_processed=len(results),
        chunks_embedded=total_embedded,
        documents_failed=failed,
        documents_skipped=skipped,
        average_latency_seconds=round(avg_latency, 2),
        total_execution_time_seconds=round(elapsed_time, 2),
        embedding_dimensions=config.embedding_dimension,
        embedding_model=config.model_name
    )
    
    json_path = report_dir / "embedding_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(summary), f, indent=4)
        
    logger.info("Embedding summary written to %s", json_path)
