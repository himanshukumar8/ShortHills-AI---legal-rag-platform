from __future__ import annotations

import logging
from hybrid_retriever.models import RetrievedResult
from answer_engine.models import CitationVerificationResult

logger = logging.getLogger(__name__)

class CitationMatcher:
    """Matches parsed citations against retrieved legal chunks."""
    
    @staticmethod
    def match(parsed_citations: list[dict], retrieved_chunks: list[RetrievedResult]) -> list[CitationVerificationResult]:
        results = []
        for cit in parsed_citations:
            doc_title = cit["document_title"]
            page = cit["page_number"]
            section = cit["section"]
            citation_str = cit["citation"]
            
            status = "FAILED"
            chunk_id = None
            confidence = 0.0
            msg = "Document not found in retrieved chunks."
            
            for chunk in retrieved_chunks:
                # Basic heuristic matching
                doc_match = doc_title.lower() in chunk.document_title.lower() or chunk.document_title.lower() in doc_title.lower()
                citation_match = citation_str.lower() in chunk.citation.lower() or chunk.citation.lower() in citation_str.lower()
                
                # Check page bound (some chunks cover a range)
                page_match = False
                if chunk.page_start <= page <= chunk.page_end:
                    page_match = True
                    
                if doc_match or citation_match:
                    if page_match:
                        status = "VERIFIED"
                        chunk_id = chunk.chunk_id
                        confidence = 1.0
                        msg = "Exact match found."
                        break
                    else:
                        status = "PARTIALLY_VERIFIED"
                        chunk_id = chunk.chunk_id
                        confidence = 0.5
                        msg = f"Document found, but page {page} is outside chunk bounds {chunk.page_start}-{chunk.page_end}."
            
            results.append(CitationVerificationResult(
                document=doc_title,
                page=page,
                section=section,
                status=status,
                supporting_chunk_id=chunk_id,
                confidence=confidence,
                message=msg
            ))
            
        return results
