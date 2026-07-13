"""Domain models for the Corpus Download Pipeline.

Contains dataclasses and enums representing documents, download outcomes,
and validation results used throughout the pipeline.

Design Rationale:
    - Dataclasses over Pydantic models: These are internal domain objects,
      not API request/response schemas. Dataclasses are lighter and avoid
      coupling the domain layer to a serialization library.
    - Enums for constrained values: DocumentStatus and DocumentCategory
      prevent invalid state from propagating through the pipeline.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class DocumentStatus(enum.Enum):
    """Possible lifecycle states of a document in the download pipeline."""

    NOT_DOWNLOADED = "NOT_DOWNLOADED"
    DOWNLOADED = "DOWNLOADED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    DUPLICATE = "DUPLICATE"


class DocumentCategory(enum.Enum):
    """Valid document categories as defined in the dataset manifest.

    The string values must exactly match the category column in
    dataset_manifest.csv.
    """

    ACTS_STATUTES = "Acts / Statutes"
    COURT_JUDGMENTS = "Court Judgments"
    IRS_PUBLICATIONS = "IRS Publications"
    TREASURY_REGS = "Treasury Regs"
    LEGAL_COMMENTARY = "Legal Commentary"


@dataclass
class DocumentRecord:
    """A single document entry from the dataset manifest.

    Maps one-to-one with a row in dataset_manifest.csv, including both
    the original curated fields and the fields added by the download
    pipeline during execution.
    """

    # --- Original manifest fields ---
    document_id: str
    title: str
    category: str
    source_name: str
    source_url: str
    pdf_url: str
    publication_year: int
    estimated_pages: int
    document_status: str = DocumentStatus.NOT_DOWNLOADED.value
    local_file_path: str = ""
    checksum: str = ""
    notes: str = ""

    # --- Fields added by the download pipeline ---
    actual_pages: int | None = None
    file_size_bytes: int | None = None
    downloaded_at: str = ""
    download_attempts: int = 0


@dataclass
class ValidationResult:
    """Outcome of PDF validation checks on a downloaded file.

    Attributes:
        is_valid: Whether the PDF passed all validation checks.
        actual_pages: Number of pages, if the PDF was successfully opened.
        file_size_bytes: File size in bytes.
        mime_type: Detected MIME type of the file.
        error_message: Description of the failure, if any.
    """

    is_valid: bool
    actual_pages: int = 0
    file_size_bytes: int = 0
    mime_type: str = ""
    error_message: str = ""


@dataclass
class DownloadResult:
    """Outcome of a complete download-validate-hash cycle for one document.

    Attributes:
        document_id: The unique identifier of the document.
        status: The final status after processing.
        file_path: Local path where the file was saved (relative).
        checksum: SHA-256 hex digest of the downloaded file.
        actual_pages: Page count from PDF validation.
        file_size_bytes: File size in bytes.
        error_message: Description of any error encountered.
        attempts: Total number of download attempts made.
        duration_seconds: Wall-clock time spent processing this document.
        duplicate_of: If duplicate, the document_id of the original.
    """

    document_id: str
    status: DocumentStatus
    file_path: str = ""
    checksum: str = ""
    actual_pages: int = 0
    file_size_bytes: int = 0
    error_message: str = ""
    attempts: int = 0
    duration_seconds: float = 0.0
    duplicate_of: str = ""
