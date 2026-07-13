from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from hybrid_retriever.response_builder import build_response

logger = logging.getLogger(__name__)

def generate_reports(report_dir: Path, response: dict, validation_result: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = report_dir / "hybrid_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "chunk_id", "document_id", "category", "citation", "source", "rrf_score", "bm25_rank", "vector_rank"
        ])
        writer.writeheader()
        for res in response["results"]:
            meta = res["retrieval_metadata"]
            writer.writerow({
                "chunk_id": res["chunk_id"],
                "document_id": res["document_id"],
                "category": res["category"],
                "citation": res["citation"],
                "source": meta["source"],
                "rrf_score": meta["rrf_score"],
                "bm25_rank": meta["bm25_rank"],
                "vector_rank": meta["vector_rank"]
            })
            
    summary = {
        "trace": response,
        "validation": validation_result
    }
    
    json_path = report_dir / "hybrid_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
        
    logger.info(f"Hybrid retrieval trace reports written to {report_dir}")
