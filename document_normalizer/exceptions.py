from __future__ import annotations

"""Custom exceptions for the Document Normalization Pipeline."""

class NormalizerError(Exception):
    """Base exception for normalization pipeline errors."""
    
    def __init__(self, message: str, document_id: str | None = None) -> None:
        self.message = message
        self.document_id = document_id
        doc_prefix = f"[{document_id}] " if document_id else ""
        super().__init__(f"{doc_prefix}{message}")


class ValidationFailedError(NormalizerError):
    """Raised when normalization output fails structural or semantic validation."""
    pass


class InvalidInputError(NormalizerError):
    """Raised when input files (e.g., parsed JSON) are missing or malformed."""
    pass
