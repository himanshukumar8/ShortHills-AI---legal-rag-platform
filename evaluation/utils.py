import json
from pathlib import Path
from evaluation.models import GoldenQuery
import logging

logger = logging.getLogger(__name__)

def load_golden_set(filepath: Path) -> list[GoldenQuery]:
    logger.info(f"Loading golden set from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    queries = []
    for item in data:
        queries.append(GoldenQuery(
            query_id=item["query_id"],
            user_query=item["user_query"],
            category=item["category"],
            expected_document=item["expected_document"],
            expected_document_id=item["expected_document_id"],
            expected_citation=item["expected_citation"],
            expected_section=item["expected_section"],
            expected_page_number=int(item["expected_page_number"]),
            expected_answer=item["expected_answer"],
            supporting_chunk_ids=item["supporting_chunk_ids"],
            difficulty=item["difficulty"]
        ))
    logger.info(f"Loaded {len(queries)} benchmark queries.")
    return queries
