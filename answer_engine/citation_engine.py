from __future__ import annotations

import logging
import json
from pathlib import Path

from answer_engine.config import AnswerEngineConfig
from answer_engine.models import EngineVerificationOutput
from answer_engine.citation_parser import CitationParser
from answer_engine.citation_matcher import CitationMatcher
from answer_engine.evidence_checker import EvidenceChecker
from answer_engine.verifier import VerificationRules
from hybrid_retriever.models import RetrievedResult

logger = logging.getLogger(__name__)

class CitationEngine:
    def __init__(self, config: AnswerEngineConfig):
        self.config = config
        
    def verify(self, query: str, retrieved_chunks: list[RetrievedResult], llm_json: dict) -> EngineVerificationOutput:
        """Runs the full citation verification pipeline."""
        
        logger.info("Starting Citation Verification Engine...")
        
        # 1. Parse Citations
        parsed_citations = CitationParser.parse(llm_json)
        logger.info(f"Parsed {len(parsed_citations)} citations from LLM output.")
        
        # 2. Match against chunks
        matched_results = CitationMatcher.match(parsed_citations, retrieved_chunks)
        
        # 3. Run validation rules (duplicates, malformed)
        warnings = VerificationRules.run_checks(matched_results)
        
        # 4. Check Evidence (Heuristic)
        answer_text = llm_json.get("answer", "")
        unsupported, ev_warnings = EvidenceChecker.check_evidence(answer_text, matched_results, retrieved_chunks)
        warnings.extend(ev_warnings)
        
        # 5. Calculate Score
        total = len(matched_results)
        if total == 0:
            score = 0.0
            overall_status = "FAILED"
        else:
            verified_count = sum(1 for r in matched_results if r.status == "VERIFIED")
            partial_count = sum(1 for r in matched_results if r.status == "PARTIALLY_VERIFIED")
            
            score = ((verified_count * 1.0) + (partial_count * 0.5)) / total * 100
            
            if score == 100.0 and not unsupported:
                overall_status = "VERIFIED"
            elif score > 50.0:
                overall_status = "PARTIALLY_VERIFIED"
            else:
                overall_status = "FAILED"
                
        output = EngineVerificationOutput(
            verification_status=overall_status,
            overall_score=score,
            citations=matched_results,
            unsupported_claims=unsupported,
            warnings=warnings
        )
        
        logger.info(f"Verification complete. Status: {overall_status}, Score: {score:.1f}")
        return output
