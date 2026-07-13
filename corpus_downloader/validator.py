"""PDF validation module for the Corpus Download Pipeline.

Validates downloaded PDF files for integrity, readability, and
basic quality using PyMuPDF (fitz). Designed to catch corrupt
downloads, partial files, and non-PDF content before the file
enters the indexing pipeline.
"""

import logging
from pathlib import Path

import fitz  # PyMuPDF

from corpus_downloader.models import ValidationResult

logger = logging.getLogger(__name__)


def validate_pdf(file_path: Path, document_id: str) -> ValidationResult:
    """Validate a downloaded PDF file through a series of checks.

    Performs the following checks in order:
    1. File exists on disk.
    2. File size is greater than zero.
    3. File starts with the PDF magic bytes (``%PDF-``).
    4. File can be opened by PyMuPDF without errors.
    5. PDF is not encrypted (unreadable without a password).
    6. PDF has at least one page.

    Args:
        file_path: Path to the PDF file to validate.
        document_id: The document identifier (for structured logging).

    Returns:
        A ValidationResult indicating pass/fail with details.
    """
    # 1. Existence
    if not file_path.exists():
        return ValidationResult(
            is_valid=False,
            error_message=f"File does not exist: {file_path}",
        )

    # 2. Non-zero size
    file_size = file_path.stat().st_size
    if file_size == 0:
        return ValidationResult(
            is_valid=False,
            file_size_bytes=0,
            error_message="File is empty (0 bytes)",
        )

    # 3. PDF magic bytes
    if not _has_pdf_signature(file_path):
        return ValidationResult(
            is_valid=False,
            file_size_bytes=file_size,
            error_message=(
                "File does not begin with PDF signature (%PDF-). "
                "The downloaded content may be an HTML error page "
                "or a non-PDF file."
            ),
        )

    # 4–6. Open with PyMuPDF and inspect
    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        return ValidationResult(
            is_valid=False,
            file_size_bytes=file_size,
            mime_type="application/pdf",
            error_message=f"PyMuPDF failed to open file: {exc}",
        )

    try:
        # 5. Encryption check
        if doc.is_encrypted:
            return ValidationResult(
                is_valid=False,
                file_size_bytes=file_size,
                mime_type="application/pdf",
                error_message="PDF is encrypted and cannot be processed",
            )

        # 6. Page count
        page_count = doc.page_count
        if page_count <= 0:
            return ValidationResult(
                is_valid=False,
                file_size_bytes=file_size,
                mime_type="application/pdf",
                error_message="PDF contains zero pages",
            )
    finally:
        doc.close()

    logger.debug(
        "[%s] Validation passed: %d pages, %s bytes",
        document_id,
        page_count,
        f"{file_size:,}",
    )

    return ValidationResult(
        is_valid=True,
        actual_pages=page_count,
        file_size_bytes=file_size,
        mime_type="application/pdf",
    )


def _has_pdf_signature(file_path: Path) -> bool:
    """Check whether a file begins with the PDF magic bytes ``%PDF-``.

    This is a fast, lightweight check that avoids fully parsing the
    file just to verify its type.

    Args:
        file_path: Path to the file to inspect.

    Returns:
        True if the first 5 bytes are ``%PDF-``, False otherwise.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
            return header == b"%PDF-"
    except OSError:
        return False
