from __future__ import annotations
import logging
from answer_engine.models import EngineVerificationOutput
from hybrid_retriever.models import RetrievedResult

logger = logging.getLogger(__name__)

class EvidenceRetriever:
    """Collects the specific chunks of text that the LLM cited as evidence."""
    
    @staticmethod
    def collect_evidence(citation_output: EngineVerificationOutput, retrieved_chunks: list[RetrievedResult]) -> tuple[list[str], str]:
        """Returns a list of supporting chunk IDs and the concatenated string of their simulated texts."""
        
        supporting_ids = []
        evidence_text = []
        
        for cit in citation_output.citations:
            if cit.status in ["VERIFIED", "PARTIALLY_VERIFIED"] and cit.supporting_chunk_id:
                supporting_ids.append(cit.supporting_chunk_id)
                # Mock the chunk text. In a real system, we fetch from Qdrant/ES payload.
                evidence_text.append(f"[Mock Text for {cit.supporting_chunk_id}: taxpayer expenses under section {cit.section}]")
                
        # Remove duplicates
        supporting_ids = list(set(supporting_ids))
        combined_evidence = " ".join(evidence_text)
        
        return supporting_ids, combined_evidence
