from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

class ClaimExtractor:
    """Splits the LLM answer into individual factual claims for validation."""
    
    @staticmethod
    def extract_claims(answer: str) -> list[str]:
        """A simple heuristic sentence splitter. 
        In production, this could use an NLP library like spaCy or an LLM call.
        """
        # Basic split on periods that are followed by a space
        sentences = [s.strip() for s in answer.split(".") if len(s.strip()) > 5]
        
        logger.info(f"Extracted {len(sentences)} claims from the answer.")
        return sentences
