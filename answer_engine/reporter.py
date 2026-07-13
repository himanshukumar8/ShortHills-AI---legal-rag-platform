from __future__ import annotations

import json
import csv
from pathlib import Path
import logging

from answer_engine.models import EngineVerificationOutput, FaithfulnessOutput

logger = logging.getLogger(__name__)

class CitationReporter:
    @staticmethod
    def generate_reports(output: EngineVerificationOutput, report_dir: Path) -> None:
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. JSON Summary
        summary = {
            "verification_status": output.verification_status,
            "overall_score": output.overall_score,
            "total_citations": len(output.citations),
            "verified_citations": sum(1 for c in output.citations if c.status == "VERIFIED"),
            "partially_verified": sum(1 for c in output.citations if c.status == "PARTIALLY_VERIFIED"),
            "failed_citations": sum(1 for c in output.citations if c.status == "FAILED"),
            "unsupported_claims_count": len(output.unsupported_claims),
            "unsupported_claims": output.unsupported_claims,
            "warnings": output.warnings
        }
        
        json_path = report_dir / "citation_verification_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
            
        # 2. CSV Report
        csv_path = report_dir / "citation_verification_report.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Document", "Page", "Section", "Status", "Confidence", "SupportingChunkID", "Message"])
            for cit in output.citations:
                writer.writerow([
                    cit.document,
                    cit.page,
                    cit.section,
                    cit.status,
                    cit.confidence,
                    cit.supporting_chunk_id or "N/A",
                    cit.message
                ])
                
        logger.info(f"Citation reports generated in {report_dir}")

class FaithfulnessReporter:
    @staticmethod
    def generate_reports(output: FaithfulnessOutput, report_dir: Path) -> None:
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. JSON Summary
        summary = {
            "overall_faithfulness_score": output.overall_faithfulness_score,
            "overall_status": output.overall_status,
            "total_claims": len(output.claims),
            "supported": sum(1 for c in output.claims if c.status == "SUPPORTED"),
            "partially_supported": sum(1 for c in output.claims if c.status == "PARTIALLY_SUPPORTS"),
            "unsupported": sum(1 for c in output.claims if c.status == "INSUFFICIENT_EVIDENCE"),
            "contradictions": len(output.contradictions),
            "unsupported_claims": output.unsupported_claims,
            "contradiction_claims": output.contradictions
        }
        
        json_path = report_dir / "faithfulness_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
            
        # 2. CSV Report
        csv_path = report_dir / "faithfulness_report.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Claim", "Status", "Confidence", "SupportingChunks"])
            for claim in output.claims:
                writer.writerow([
                    claim.claim,
                    claim.status,
                    claim.confidence,
                    ",".join(claim.supporting_chunks)
                ])
                
        logger.info(f"Faithfulness reports generated in {report_dir}")

