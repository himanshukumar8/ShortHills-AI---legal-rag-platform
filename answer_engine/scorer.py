from __future__ import annotations
import logging
from answer_engine.models import ClaimVerificationResult

logger = logging.getLogger(__name__)

class FaithfulnessScorer:
    """Calculates the overall deterministic faithfulness score."""
    
    @staticmethod
    def calculate_score(claims: list[ClaimVerificationResult]) -> tuple[float, str]:
        if not claims:
            return 0.0, "FAIL"
            
        total = len(claims)
        supported = sum(1 for c in claims if c.status == "SUPPORTED")
        partial = sum(1 for c in claims if c.status == "PARTIALLY_SUPPORTS")
        contradictions = sum(1 for c in claims if c.status == "CONTRADICTS")
        
        # If there is even a single contradiction, we fail the entire answer
        if contradictions > 0:
            return 0.0, "FAIL"
            
        score = ((supported * 1.0) + (partial * 0.5)) / total * 100
        
        if score == 100.0:
            status = "PASS"
        elif score > 50.0:
            status = "WARNING"
        else:
            status = "FAIL"
            
        return score, status
