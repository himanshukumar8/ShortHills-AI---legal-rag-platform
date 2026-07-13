from __future__ import annotations

import logging
from es_indexer.client import BaseESClient

logger = logging.getLogger(__name__)

def validate_index(client: BaseESClient, index_name: str, expected_count: int, test_citation: str = "") -> dict:
    """Validate Elasticsearch index integrity."""
    
    issues = []
    
    # 1. Check total count
    actual_count = client.count(index_name)
    if actual_count != expected_count:
        issues.append(f"Count mismatch: Expected {expected_count}, got {actual_count}")
        
    # 2. Check filters (Simulated by searching a known category)
    # We will search for 'Acts / Statutes' to ensure the mapping works
    cat_res = client.search(index_name, {"term": {"category": "Acts / Statutes"}})
    cat_hits = cat_res["hits"]["total"]["value"]
    logger.info(f"Validator: Found {cat_hits} documents in category 'Acts / Statutes'.")
    if cat_hits == 0 and expected_count > 0:
        issues.append("Filter validation failed: No documents found for known category.")
        
    # 3. Check searchable citations
    if test_citation:
        cit_res = client.search(index_name, {"term": {"citation": test_citation}})
        cit_hits = cit_res["hits"]["total"]["value"]
        logger.info(f"Validator: Found {cit_hits} documents for citation '{test_citation}'.")
        
    return {
        "is_valid": len(issues) == 0,
        "indexed_count": actual_count,
        "issues": issues
    }
