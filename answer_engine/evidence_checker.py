from __future__ import annotations

import logging
from hybrid_retriever.models import RetrievedResult
from answer_engine.models import CitationVerificationResult

logger = logging.getLogger(__name__)

class EvidenceChecker:
    """Checks if the factual claims in the answer are supported by the retrieved chunks.
    
    Note: Since this module MUST NOT call the LLM, we use a basic heuristic/mock-up
    to detect 'SUPPORTED', 'PARTIALLY_SUPPORTED', or 'NOT_SUPPORTED'. 
    A true semantic faithfulness check requires an NLI model or LLM.
    """
    
    @staticmethod
    def check_evidence(answer: str, matched_results: list[CitationVerificationResult], retrieved_chunks: list[RetrievedResult]) -> tuple[list[str], list[str]]:
        unsupported_claims = []
        warnings = []
        
        # We simulate factual extraction by splitting sentences (very naive heuristic)
        sentences = [s.strip() for s in answer.split(".") if len(s.strip()) > 10]
        
        for sentence in sentences:
            # Check if any chunk text 'supports' this sentence.
            # In our mock environment, chunk text is represented as "[Text content for chunk X]".
            # Since we can't do semantic NLI without an LLM, we assume sentences containing specific trigger words might be unsupported if no verified citation exists.
            
            if "must" in sentence.lower() or "shall" in sentence.lower() or "requires" in sentence.lower():
                # Strong claim. If we have no VERIFIED citations, flag it.
                has_verified = any(res.status == "VERIFIED" for res in matched_results)
                if not has_verified:
                    unsupported_claims.append(f"Strong claim lacks verified citation: '{sentence}'")
                    warnings.append(f"Claim classification: NOT_SUPPORTED - '{sentence}'")
                else:
                    warnings.append(f"Claim classification: SUPPORTED - '{sentence}'")
                    
        return unsupported_claims, warnings
