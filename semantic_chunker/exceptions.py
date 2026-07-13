from __future__ import annotations

"""Custom exceptions for Semantic Chunking."""

class ChunkerError(Exception):
    """Base exception for chunking pipeline errors."""
    def __init__(self, message: str, document_id: str | None = None) -> None:
        self.message = message
        self.document_id = document_id
        doc_prefix = f"[{document_id}] " if document_id else ""
        super().__init__(f"{doc_prefix}{message}")

class ValidatorError(ChunkerError):
    """Raised when chunks fail validation (e.g. empty chunks, orphans)."""
    pass

class DataFormatError(ChunkerError):
    """Raised when normalized input data is malformed."""
    pass
