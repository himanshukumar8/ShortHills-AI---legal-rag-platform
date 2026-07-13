from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from qdrant_indexer.models import IndexingStats

logger = logging.getLogger(__name__)

def generate_reports(report_dir: Path, stats: list[IndexingStats], global_summary: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = report_dir / "qdrant_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["document_id", "points_indexed", "status", "error"])
        writer.writeheader()
        
        for s in stats:
            writer.writerow({
                "document_id": s.document_id,
                "points_indexed": s.points_indexed,
                "status": s.status,
                "error": s.error
            })
            
    json_path = report_dir / "qdrant_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(global_summary, f, indent=4)
        
    logger.info(f"Qdrant reports successfully written to {report_dir}")
