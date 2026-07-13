from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_reports(report_dir: Path, doc_stats: list[dict], global_stats: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = report_dir / "elasticsearch_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["document_id", "category", "chunks_indexed", "status"])
        writer.writeheader()
        for stat in doc_stats:
            writer.writerow(stat)
            
    json_path = report_dir / "elasticsearch_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(global_stats, f, indent=4)
        
    logger.info(f"Reports written to {report_dir}")
