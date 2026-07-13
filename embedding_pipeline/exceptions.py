from __future__ import annotations

class EmbeddingError(Exception):
    def __init__(self, message: str, document_id: str | None = None) -> None:
        self.message = message
        self.document_id = document_id
        doc_prefix = f"[{document_id}] " if document_id else ""
        super().__init__(f"{doc_prefix}{message}")

class ProviderError(EmbeddingError):
    """Raised when the embedding API/model fails to generate vectors."""
    pass

class ValidationError(EmbeddingError):
    """Raised when mathematical validation of vectors fails (NaN, zeros, wrong dims)."""
    pass
