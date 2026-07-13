from __future__ import annotations
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseFaithfulnessChecker(ABC):
    @abstractmethod
    def check_faithfulness(self, claim: str, evidence: str) -> tuple[str, float]:
        """Returns a status ('SUPPORTED', 'PARTIALLY_SUPPORTS', 'CONTRADICTS', 'INSUFFICIENT_EVIDENCE') 
        and a confidence score (0.0 to 1.0)"""
        pass

class MockNLIChecker(BaseFaithfulnessChecker):
    def check_faithfulness(self, claim: str, evidence: str) -> tuple[str, float]:
        """Simulates an NLI check. In production, this would call a Cross-Encoder like roberta-large-mnli."""
        lower_claim = claim.lower()
        
        # Super basic heuristic to simulate NLI outcomes
        if "not" in lower_claim and "expenses" in evidence.lower():
            return "CONTRADICTS", 0.95
        elif "deduct" in lower_claim or "expense" in lower_claim:
            return "SUPPORTED", 0.98
        elif "must" in lower_claim:
            return "INSUFFICIENT_EVIDENCE", 0.85
        else:
            return "PARTIALLY_SUPPORTS", 0.60
            
class LLMJudgeChecker(BaseFaithfulnessChecker):
    def check_faithfulness(self, claim: str, evidence: str) -> tuple[str, float]:
        raise NotImplementedError("LLM Judge pending API implementation.")
        
def get_nli_checker(provider_name: str = "mock") -> BaseFaithfulnessChecker:
    if provider_name == "mock":
        return MockNLIChecker()
    else:
        return MockNLIChecker()
