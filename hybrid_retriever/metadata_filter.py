from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

def extract_filters(query_string: str) -> dict:
    """
    Very simple heuristic metadata extraction.
    In a real system, an LLM Query Analyzer would extract structured filters.
    """
    filters = {}
    lower_q = query_string.lower()
    
    if "act" in lower_q or "statute" in lower_q:
        filters["category"] = "Acts / Statutes"
    elif "regulation" in lower_q:
        filters["category"] = "Treasury Regulations"
    elif "irs" in lower_q:
        filters["category"] = "IRS Publications"
        
    return filters
