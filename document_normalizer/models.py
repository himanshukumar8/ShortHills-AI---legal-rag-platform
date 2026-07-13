from __future__ import annotations

"""Domain models for the Document Normalization Pipeline."""

import enum
from dataclasses import dataclass, field
from pdf_parser.models import DocumentMetadata, PageExtract, ParsedDocument

class NormalizationStatus(enum.Enum):
    """Lifecycle states of a document during normalization."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"

@dataclass
class NormalizedPage:
    """Represents a cleaned, normalized page."""
    page_number: int
    text: str
    original_character_count: int
    normalized_character_count: int
    warnings: list[str] = field(default_factory=list)

@dataclass
class NormalizationStatistics:
    """Statistics detailing the normalization reduction."""
    total_pages: int
    original_characters: int
    normalized_characters: int
    characters_removed: int
    reduction_percentage: float

@dataclass
class NormalizedDocument:
    """The complete normalized document."""
    metadata: DocumentMetadata
    pages: list[NormalizedPage]
    full_text: str
    statistics: NormalizationStatistics
    processing_info: dict[str, str] = field(default_factory=dict)

@dataclass
class NormalizationResult:
    """The outcome of a document normalization attempt for reporting."""
    document_id: str
    status: NormalizationStatus
    pages_processed: int = 0
    characters_removed: int = 0
    warnings: list[str] = field(default_factory=list)
    error_message: str = ""
    duration_seconds: float = 0.0
