from __future__ import annotations

import logging
from answer_engine.models import CitationVerificationResult

logger = logging.getLogger(__name__)

class VerificationRules:
    """Applies validation rules to the matched citations."""
    
    @staticmethod
    def run_checks(results: list[CitationVerificationResult]) -> list[str]:
        warnings = []
        
        # 1. Duplicate check
        seen = set()
        for res in results:
            sig = (res.document, res.page, res.section)
            if sig in seen:
                warnings.append(f"Duplicate citation found: {sig}")
            seen.add(sig)
            
        # 2. Missing docs
        for res in results:
            if res.status == "FAILED":
                warnings.append(f"Citation completely unsupported: {res.document} - {res.section}")
                
        # 3. Invalid page numbers
        for res in results:
            if res.page < 0:
                warnings.append(f"Invalid page number {res.page} for {res.document}")
                
        return warnings
