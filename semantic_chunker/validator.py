from __future__ import annotations

from semantic_chunker.models import SemanticChunk
from semantic_chunker.exceptions import ValidatorError

def validate_chunks(chunks: list[SemanticChunk], document_id: str) -> list[str]:
    """Validate a set of chunks for a document."""
    warnings = []
    seen_hashes = set()
    seen_ids = set()
    
    if not chunks:
        raise ValidatorError("No chunks generated for document", document_id)
        
    for chunk in chunks:
        # No empty chunks
        if not chunk.text.strip():
            raise ValidatorError(f"Empty chunk detected: {chunk.chunk_id}", document_id)
            
        # No orphan chunks
        if chunk.parent_document_id != document_id:
            raise ValidatorError(f"Chunk belongs to {chunk.parent_document_id} but processing {document_id}", document_id)
            
        # Stable deterministic IDs
        if chunk.chunk_id in seen_ids:
            raise ValidatorError(f"Duplicate chunk ID detected: {chunk.chunk_id}", document_id)
        seen_ids.add(chunk.chunk_id)
        
        # Unique hashes (Warning, not fatal, as two sections might have identical boilerplate)
        if chunk.chunk_hash in seen_hashes:
            warnings.append(f"Duplicate chunk text detected (Hash: {chunk.chunk_hash})")
        seen_hashes.add(chunk.chunk_hash)
        
    return warnings
