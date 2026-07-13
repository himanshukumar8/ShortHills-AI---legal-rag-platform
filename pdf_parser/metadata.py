from __future__ import annotations

"""Metadata assembly for the PDF Parser Pipeline.

Synthesizes document-level metadata from the dataset manifest and 
runtime parsing state, ensuring all required fields are present for
downstream chunking and retrieval.
"""

from datetime import datetime, timezone

from corpus_downloader.models import DocumentRecord
from pdf_parser import __version__
from pdf_parser.models import DocumentMetadata


def build_metadata(record: DocumentRecord, total_pages: int) -> DocumentMetadata:
    """Build the structured metadata object for a parsed document.

    Args:
        record: The document record from the dataset manifest.
        total_pages: The actual number of pages extracted.

    Returns:
        A populated DocumentMetadata object.
    """
    return DocumentMetadata(
        document_id=record.document_id,
        title=record.title,
        category=record.category,
        source=record.source_name,
        publication_year=record.publication_year,
        page_count=total_pages,
        file_size_bytes=record.file_size_bytes or 0,
        checksum=record.checksum,
        processing_timestamp=datetime.now(timezone.utc).isoformat(),
        parser_version=__version__,
    )
