from __future__ import annotations
import logging

from answer_engine.config import AnswerEngineConfig
from answer_engine.models import FaithfulnessOutput, ClaimVerificationResult, EngineVerificationOutput
from hybrid_retriever.models import RetrievedResult

from answer_engine.claim_extractor import ClaimExtractor
from answer_engine.evidence_retriever import EvidenceRetriever
from answer_engine.nli_checker import get_nli_checker
from answer_engine.scorer import FaithfulnessScorer

logger = logging.getLogger(__name__)

class FaithfulnessValidator:
    def __init__(self, config: AnswerEngineConfig):
        self.config = config
        self.checker = get_nli_checker("mock")
        
    def validate(self, llm_json: dict, citation_output: EngineVerificationOutput, retrieved_chunks: list[RetrievedResult]) -> FaithfulnessOutput:
        """Main orchestrator for Faithfulness Validation."""
        logger.info("Starting Faithfulness Validation Phase...")
        
        answer_text = llm_json.get("answer", "")
        
        # 1. Extract Claims
        claims = ClaimExtractor.extract_claims(answer_text)
        
        # 2. Retrieve Evidence
        supporting_ids, combined_evidence = EvidenceRetriever.collect_evidence(citation_output, retrieved_chunks)
        
        if not combined_evidence.strip():
            logger.warning("No verified evidence found. All claims will be marked unsupported.")
            
        # 3. Check Faithfulness
        claim_results = []
        unsupported = []
        contradictions = []
        
        for claim in claims:
            if not combined_evidence.strip():
                status = "INSUFFICIENT_EVIDENCE"
                conf = 1.0
            else:
                status, conf = self.checker.check_faithfulness(claim, combined_evidence)
                
            claim_results.append(ClaimVerificationResult(
                claim=claim,
                status=status,
                supporting_chunks=supporting_ids,
                confidence=conf
            ))
            
            if status == "INSUFFICIENT_EVIDENCE":
                unsupported.append(claim)
            elif status == "CONTRADICTS":
                contradictions.append(claim)
                
        # 4. Calculate final score
        score, status = FaithfulnessScorer.calculate_score(claim_results)
        
        logger.info(f"Faithfulness Validation Complete: {status} (Score: {score:.1f})")
        
        return FaithfulnessOutput(
            overall_faithfulness_score=score,
            overall_status=status,
            claims=claim_results,
            unsupported_claims=unsupported,
            contradictions=contradictions
        )
