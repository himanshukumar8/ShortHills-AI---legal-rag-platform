from __future__ import annotations

import logging
from document_normalizer.models import NormalizedDocument
from semantic_chunker.models import SemanticChunk
from semantic_chunker.chunk_builder import (
    chunk_acts,
    chunk_judgments,
    chunk_irs,
    chunk_regs,
    chunk_commentary
)

logger = logging.getLogger(__name__)

def analyze_and_chunk(doc: NormalizedDocument) -> list[SemanticChunk]:
    """Dispatch to the correct chunking strategy based on category."""
    cat = doc.metadata.category
    
    if cat == "Acts / Statutes":
        return chunk_acts(doc)
    elif cat == "Court Judgments":
        return chunk_judgments(doc)
    elif cat == "Treasury Regulations":
        return chunk_regs(doc)
    elif cat == "IRS Publications":
        return chunk_irs(doc)
    elif cat == "Legal Commentary":
        return chunk_commentary(doc)
    else:
        logger.warning("[%s] Unknown category '%s', falling back to commentary strategy.", doc.metadata.document_id, cat)
        return chunk_commentary(doc)
