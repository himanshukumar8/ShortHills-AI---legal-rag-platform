from __future__ import annotations

import logging
from hybrid_retriever.models import RetrievedResult

logger = logging.getLogger(__name__)

def validate_citations(results: list[RetrievedResult]) -> None:
    """Verifies that citations map cleanly to expected legal structures."""
    for res in results:
        if not res.citation:
            # Fallback to parent document ID as citation if missing
            res.citation = res.document_id
            
        # Example validation rule: U.S.C. shouldn't be empty if it's a statute
        if res.category == "Acts / Statutes" and "U.S.C." not in res.citation:
            # Just a diagnostic log, we don't drop the result
            logger.debug(f"Chunk {res.chunk_id} missing U.S.C. in citation: {res.citation}")
