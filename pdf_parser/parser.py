from __future__ import annotations

"""Facade for parsing a single document.

Coordinates text extraction, validation, metadata synthesis, and writing.
"""

import logging
import time
from pathlib import Path

from corpus_downloader.models import DocumentRecord
from pdf_parser.config import ParserConfig
from pdf_parser.exceptions import PdfParserError
from pdf_parser.extractor import extract_pages
from pdf_parser.metadata import build_metadata
from pdf_parser.models import ParsedDocument, ParsingResult, ParsingStatistics, ParsingStatus
from pdf_parser.validator import validate_extraction
from pdf_parser.writer import write_document

logger = logging.getLogger(__name__)


def parse_document(record: DocumentRecord, config: ParserConfig) -> ParsingResult:
    """Parse a single PDF document.

    Args:
        record: The document record from the manifest.
        config: The parser configuration.

    Returns:
        A ParsingResult detailing the outcome.
    """
    start_time = time.monotonic()
    doc_id = record.document_id
    
    try:
        if not record.local_file_path:
            raise PdfParserError("Missing local_file_path in manifest record", doc_id)
            
        file_path = Path(record.local_file_path)
        if not file_path.exists():
            raise PdfParserError(f"File not found on disk: {file_path}", doc_id)
            
        # 1. Extract Pages
        pages = extract_pages(file_path, doc_id)
        
        # 2. Validate
        # use actual_pages from manifest (which downloader verified), or fallback to estimated
        expected_pages = record.actual_pages or record.estimated_pages
        warnings = validate_extraction(doc_id, pages, expected_pages)
        
        # 3. Assemble Metadata
        metadata = build_metadata(record, total_pages=len(pages))
        
        # 4. Assemble Statistics & Full Text
        total_chars = sum(p.character_count for p in pages)
        total_words = sum(p.word_count for p in pages)
        avg_words = total_words / len(pages) if pages else 0.0
        
        stats = ParsingStatistics(
            total_pages=len(pages),
            total_characters=total_chars,
            total_words=total_words,
            average_words_per_page=round(avg_words, 2),
        )
        
        # We join with double newlines to separate pages clearly in the full text representation
        full_text = "\n\n".join(p.text for p in pages)
        
        # 5. Create Final Document
        parsed_doc = ParsedDocument(
            metadata=metadata,
            pages=pages,
            full_text=full_text,
            statistics=stats,
            processing_info={"warnings": warnings} if warnings else {},
        )
        
        # 6. Write to Disk
        write_document(parsed_doc, config.output_dir)
        
        status = ParsingStatus.WARNING if warnings else ParsingStatus.SUCCESS
        
        return ParsingResult(
            document_id=doc_id,
            status=status,
            pages_processed=len(pages),
            warnings=warnings,
            duration_seconds=time.monotonic() - start_time,
        )

    except Exception as exc:
        logger.error("[%s] Parsing failed: %s", doc_id, exc, exc_info=True)
        return ParsingResult(
            document_id=doc_id,
            status=ParsingStatus.FAILED,
            error_message=str(exc),
            duration_seconds=time.monotonic() - start_time,
        )
