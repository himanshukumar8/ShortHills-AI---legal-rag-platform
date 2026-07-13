from __future__ import annotations

"""File writer for the PDF Parser Pipeline.

Serializes the parsed document data into the final output formats:
- metadata.json
- pages.json
- full_text.txt
- document.json (the aggregate)
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path

from pdf_parser.models import ParsedDocument
from pdf_parser.utils import ensure_directory

logger = logging.getLogger(__name__)


def write_document(
    document: ParsedDocument, base_output_dir: Path
) -> Path:
    """Write the parsed document to disk in structured formats.

    Creates a subdirectory: `{base_output_dir}/{category}/{document_id}/`
    and writes the 4 required files.

    Args:
        document: The ParsedDocument object to write.
        base_output_dir: The root processing directory.

    Returns:
        The path to the document's specific output directory.
    """
    # Sanitize category for folder name (simple lowercasing and replacing spaces/slashes)
    safe_category = document.metadata.category.lower().replace(" / ", "_").replace(" ", "_")
    
    doc_dir = base_output_dir / safe_category / document.metadata.document_id
    ensure_directory(doc_dir)

    # Convert dataclasses to dicts for JSON serialization
    doc_dict = asdict(document)
    metadata_dict = doc_dict["metadata"]
    pages_dict = doc_dict["pages"]

    # 1. Write metadata.json
    _write_json(doc_dir / "metadata.json", metadata_dict)
    
    # 2. Write pages.json
    _write_json(doc_dir / "pages.json", pages_dict)
    
    # 3. Write full_text.txt
    _write_text(doc_dir / "full_text.txt", document.full_text)
    
    # 4. Write document.json (aggregate)
    _write_json(doc_dir / "document.json", doc_dict)

    logger.debug("[%s] Successfully wrote output files to %s", document.metadata.document_id, doc_dir)
    return doc_dir


def _write_json(path: Path, data: dict | list) -> None:
    """Write data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _write_text(path: Path, text: str) -> None:
    """Write text to a TXT file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
