from __future__ import annotations

"""Domain models for the PDF Parser Pipeline.

Contains dataclasses and enums representing parsing results,
page extractions, and metadata.
"""

import enum
from dataclasses import dataclass, field


class ParsingStatus(enum.Enum):
    """Lifecycle states of a document during parsing."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"


@dataclass
class PageExtract:
    """Represents the extracted text and metadata for a single page."""

    page_number: int
    text: str
    character_count: int
    word_count: int
    extractor_used: str  # e.g., 'pymupdf' or 'pdfplumber'
    warnings: list[str] = field(default_factory=list)


@dataclass
class DocumentMetadata:
    """Document-level metadata."""

    document_id: str
    title: str
    category: str
    source: str
    publication_year: int
    page_count: int
    file_size_bytes: int
    checksum: str
    processing_timestamp: str
    parser_version: str


@dataclass
class ParsingStatistics:
    """Statistics for the parsed document."""

    total_pages: int
    total_characters: int
    total_words: int
    average_words_per_page: float


@dataclass
class ParsedDocument:
    """The complete structured document."""

    metadata: DocumentMetadata
    pages: list[PageExtract]
    full_text: str
    statistics: ParsingStatistics
    processing_info: dict[str, str] = field(default_factory=dict)


@dataclass
class ParsingResult:
    """The outcome of a document parsing attempt for reporting."""

    document_id: str
    status: ParsingStatus
    pages_processed: int = 0
    warnings: list[str] = field(default_factory=list)
    error_message: str = ""
    duration_seconds: float = 0.0
