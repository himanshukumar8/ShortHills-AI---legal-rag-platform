from __future__ import annotations

"""Custom exception hierarchy for the PDF Parser Pipeline.

All exceptions inherit from PdfParserError, enabling both
granular error handling and broad catch-alls.
"""

class PdfParserError(Exception):
    """Base exception for all PDF parsing errors."""

    def __init__(self, message: str, document_id: str | None = None) -> None:
        self.message = message
        self.document_id = document_id
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.document_id:
            return f"[{self.document_id}] {self.message}"
        return self.message


class ExtractionError(PdfParserError):
    """Raised when text extraction fails (e.g., corrupted file)."""
    
    def __init__(
        self,
        message: str,
        document_id: str | None = None,
        page_number: int | None = None,
    ) -> None:
        super().__init__(message, document_id)
        self.page_number = page_number

    def __str__(self) -> str:
        base = super().__str__()
        if self.page_number is not None:
            return f"{base} (Page {self.page_number})"
        return base


class ValidationError(PdfParserError):
    """Raised when extracted data fails quality checks."""
    pass


class MissingFileError(PdfParserError):
    """Raised when a required file is missing (e.g., manifest or PDF)."""
    pass
