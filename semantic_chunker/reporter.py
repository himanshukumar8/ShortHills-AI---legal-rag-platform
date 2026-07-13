from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from semantic_chunker.models import DocumentChunkingResult, ChunkingStatus, ChunkingSummary
from semantic_chunker.utils import ensure_directory

logger = logging.getLogger(__name__)

def generate_reports(results: list[DocumentChunkingResult], report_dir: Path, elapsed_time: float) -> None:
    ensure_directory(report_dir)
    
    csv_path = report_dir / "chunking_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["document_id", "status", "chunks_generated", "duration_seconds", "warnings", "error_message"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in results:
            writer.writerow({
                "document_id": r.document_id,
                "status": r.status.value,
                "chunks_generated": len(r.chunks),
                "duration_seconds": round(r.duration_seconds, 2),
                "warnings": "; ".join(r.warnings),
                "error_message": r.error_message
            })
            
    logger.info("Chunking detail report written to %s", csv_path)
    
    # Calculate summary metrics
    total_chunks = sum(len(r.chunks) for r in results)
    sizes = [len(c.text) for r in results for c in r.chunks]
    
    summary = ChunkingSummary(
        documents_processed=len(results),
        chunks_generated=total_chunks,
        average_chunk_size=round(sum(sizes) / len(sizes), 2) if sizes else 0.0,
        max_chunk_size=max(sizes) if sizes else 0,
        min_chunk_size=min(sizes) if sizes else 0,
        max_hierarchy_depth=max((c.hierarchy_level for r in results for c in r.chunks), default=0),
        duplicate_chunks_detected=sum(len(r.warnings) for r in results),
        execution_time_seconds=round(elapsed_time, 2)
    )
    
    from dataclasses import asdict
    json_path = report_dir / "chunking_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(summary), f, indent=4)
        
    logger.info("Chunking summary written to %s", json_path)
