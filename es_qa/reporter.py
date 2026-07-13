from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from es_qa.evaluator import QueryResult

logger = logging.getLogger(__name__)

def generate_reports(report_dir: Path, results: list[QueryResult], metrics: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = report_dir / "elasticsearch_quality_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "query_id", "query_type", "ground_truth", "retrieved_top_1", "found_in_top_5", "latency_s"
        ])
        writer.writeheader()
        
        for r in results:
            gt = r.query.ground_truth_chunk_id
            found = gt in r.top_k_ids[:5]
            top_1 = r.top_k_ids[0] if r.top_k_ids else None
            
            writer.writerow({
                "query_id": r.query.query_id,
                "query_type": r.query.query_type,
                "ground_truth": gt,
                "retrieved_top_1": top_1,
                "found_in_top_5": found,
                "latency_s": round(r.latency, 4)
            })
            
    summary = {
        "total_queries": len(results),
        "metrics": metrics,
        "recommendations": []
    }
    
    if metrics["quality_score"] < 85:
        summary["recommendations"].append("Consider adding fuzzy matching to keyword queries.")
        summary["recommendations"].append("Implement synonym graphs for legal terminology.")
    else:
        summary["recommendations"].append("Quality score is excellent. Ready for Hybrid Search integration.")
        
    json_path = report_dir / "elasticsearch_quality_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    logger.info(f"Quality reports written to {report_dir}")
