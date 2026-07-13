from __future__ import annotations

import logging
from answer_engine.models import CitationVerificationResult

logger = logging.getLogger(__name__)

class CitationParser:
    """Parses citations from the LLM JSON response."""
    
    @staticmethod
    def parse(llm_response_json: dict) -> list[dict]:
        citations = llm_response_json.get("citations", [])
        if not isinstance(citations, list):
            logger.warning("Citations field is not a list. Returning empty list.")
            return []
            
        valid_citations = []
        for i, cit in enumerate(citations):
            if not isinstance(cit, dict):
                logger.warning(f"Citation at index {i} is not a dictionary.")
                continue
                
            doc_title = cit.get("document_title") or cit.get("document", "Unknown")
            page = cit.get("page_number") or cit.get("page", 0)
            section = cit.get("section", "Unknown")
            citation_str = cit.get("citation", "Unknown")
            
            valid_citations.append({
                "document_title": str(doc_title),
                "page_number": int(page) if str(page).isdigit() else 0,
                "section": str(section),
                "citation": str(citation_str)
            })
            
        return valid_citations
