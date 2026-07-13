from __future__ import annotations

"""Manifest reader for the Corpus Download Pipeline.

Reads the dataset_manifest.csv file and returns a list of DocumentRecord
objects. Validates the CSV schema to fail fast on structural issues
before the pipeline begins any network activity.
"""

import csv
import logging
from pathlib import Path

from corpus_downloader.exceptions import ManifestError
from corpus_downloader.models import DocumentRecord

logger = logging.getLogger(__name__)

# Columns that must exist in the manifest CSV for the pipeline to run.
_REQUIRED_COLUMNS: frozenset[str] = frozenset({
    "document_id",
    "title",
    "category",
    "source_name",
    "source_url",
    "pdf_url",
    "publication_year",
    "estimated_pages",
    "document_status",
    "local_file_path",
    "checksum",
    "notes",
})


def read_manifest(manifest_path: Path) -> list[DocumentRecord]:
    """Read the dataset manifest CSV and parse it into DocumentRecord objects.

    Validates that:
    - The file exists and is non-empty.
    - All required columns are present in the header.
    - Each row has a non-empty document_id and valid numeric fields.

    Args:
        manifest_path: Path to the ``dataset_manifest.csv`` file.

    Returns:
        A list of DocumentRecord objects, one per CSV row.

    Raises:
        ManifestError: If the file is missing, empty, or structurally invalid.
    """
    if not manifest_path.exists():
        raise ManifestError(f"Manifest file not found: {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ManifestError(
                    f"Manifest file is empty or has no header: {manifest_path}"
                )

            _validate_columns(set(reader.fieldnames), manifest_path)

            records: list[DocumentRecord] = []
            for row_num, row in enumerate(reader, start=2):
                record = _parse_row(row, row_num, manifest_path)
                records.append(record)

    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError(
            f"Failed to read manifest {manifest_path}: {exc}"
        ) from exc

    if not records:
        raise ManifestError(
            f"Manifest contains no data rows: {manifest_path}"
        )

    logger.info(
        "Loaded %d document records from %s", len(records), manifest_path
    )
    return records


def _validate_columns(actual_columns: set[str], path: Path) -> None:
    """Check that all required columns exist in the CSV header.

    Args:
        actual_columns: Column names found in the CSV.
        path: Manifest file path (for error messages).

    Raises:
        ManifestError: If any required columns are missing.
    """
    missing = _REQUIRED_COLUMNS - actual_columns
    if missing:
        raise ManifestError(
            f"Manifest {path} is missing required columns: "
            f"{sorted(missing)}"
        )


def _parse_row(
    row: dict[str, str], row_num: int, path: Path
) -> DocumentRecord:
    """Parse a single CSV row into a DocumentRecord.

    Args:
        row: Column-name-to-value mapping from csv.DictReader.
        row_num: The 1-indexed row number for error messages.
        path: Manifest file path for error messages.

    Returns:
        A populated DocumentRecord.

    Raises:
        ManifestError: If required fields are empty or have invalid types.
    """
    document_id = row.get("document_id", "").strip()
    if not document_id:
        raise ManifestError(
            f"Row {row_num} in {path} has an empty document_id"
        )

    publication_year = _parse_required_int(
        row.get("publication_year", ""), "publication_year", row_num,
        document_id, path,
    )
    estimated_pages = _parse_required_int(
        row.get("estimated_pages", ""), "estimated_pages", row_num,
        document_id, path,
    )

    # Optional numeric fields added by the pipeline in prior runs
    actual_pages = _parse_optional_int(row.get("actual_pages", ""))
    file_size_bytes = _parse_optional_int(row.get("file_size_bytes", ""))
    download_attempts = _parse_optional_int(
        row.get("download_attempts", "")
    ) or 0

    return DocumentRecord(
        document_id=document_id,
        title=row.get("title", "").strip(),
        category=row.get("category", "").strip(),
        source_name=row.get("source_name", "").strip(),
        source_url=row.get("source_url", "").strip(),
        pdf_url=row.get("pdf_url", "").strip(),
        publication_year=publication_year,
        estimated_pages=estimated_pages,
        document_status=row.get("document_status", "NOT_DOWNLOADED").strip(),
        local_file_path=row.get("local_file_path", "").strip(),
        checksum=row.get("checksum", "").strip(),
        notes=row.get("notes", "").strip(),
        actual_pages=actual_pages,
        file_size_bytes=file_size_bytes,
        downloaded_at=row.get("downloaded_at", "").strip(),
        download_attempts=download_attempts,
    )


def _parse_required_int(
    value: str,
    field_name: str,
    row_num: int,
    document_id: str,
    path: Path,
) -> int:
    """Parse a required integer CSV field.

    Args:
        value: The raw string value from the CSV.
        field_name: The column name (for error messages).
        row_num: The row number (for error messages).
        document_id: The document ID (for error messages).
        path: The manifest path (for error messages).

    Returns:
        The parsed integer.

    Raises:
        ManifestError: If the value is empty or non-numeric.
    """
    value = value.strip()
    if not value:
        raise ManifestError(
            f"Row {row_num} ({document_id}) in {path}: "
            f"required field '{field_name}' is empty"
        )
    try:
        return int(value)
    except ValueError as exc:
        raise ManifestError(
            f"Row {row_num} ({document_id}) in {path}: "
            f"invalid {field_name} '{value}'"
        ) from exc


def _parse_optional_int(value: str) -> int | None:
    """Parse an optional integer field, returning None if empty or invalid.

    Args:
        value: The raw string value.

    Returns:
        The parsed integer, or None.
    """
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
