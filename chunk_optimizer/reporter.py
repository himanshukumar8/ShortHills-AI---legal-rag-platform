from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from semantic_chunker.models import DocumentChunkingResult, ChunkingStatus, ChunkingSummary
from chunk_optimizer.utils import ensure_directory

# Reusing semantic_chunker's utils and reporters conceptually, but keeping logic separate
# Actually, I'll just write a basic summary for the optimizer run itself.
logger = logging.getLogger(__name__)

def generate_reports(results: list[DocumentChunkingResult], report_dir: Path, elapsed_time: float) -> None:
    ensure_directory(report_dir)
    
    csv_path = report_dir / "optimizer_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["document_id", "status", "optimized_chunks", "duration_seconds", "error_message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                "document_id": r.document_id,
                "status": r.status.value,
                "optimized_chunks": len(r.chunks),
                "duration_seconds": round(r.duration_seconds, 2),
                "error_message": r.error_message
            })
