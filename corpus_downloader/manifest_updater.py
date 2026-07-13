"""Manifest updater for the Corpus Download Pipeline.

Reads the existing dataset_manifest.csv, merges download results
for each processed document, adds new pipeline-specific columns
if they do not already exist, and writes the updated manifest back.

The CSV file is the single source of truth for the project.
This module treats it as such — it reads, merges, and overwrites
atomically to avoid partial-write corruption.
"""

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from corpus_downloader.exceptions import ManifestError
from corpus_downloader.models import DownloadResult

logger = logging.getLogger(__name__)

# Complete ordered column list for the output manifest.
# Original columns come first, pipeline-added columns follow.
_OUTPUT_COLUMNS: list[str] = [
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
    "actual_pages",
    "file_size_bytes",
    "downloaded_at",
    "download_attempts",
]


def update_manifest(
    manifest_path: Path,
    results: dict[str, DownloadResult],
) -> None:
    """Update the dataset manifest CSV with download pipeline results.

    For each document_id in ``results``, the corresponding CSV row
    is updated with the download status, file path, checksum, page
    count, file size, timestamp, and attempt count. Rows not present
    in ``results`` are preserved unchanged.

    New columns (``actual_pages``, ``file_size_bytes``, ``downloaded_at``,
    ``download_attempts``) are added to the CSV if they do not already
    exist in the header.

    Args:
        manifest_path: Path to the ``dataset_manifest.csv`` file.
        results: Mapping of ``document_id → DownloadResult``.

    Raises:
        ManifestError: If the manifest cannot be read or written.
    """
    if not results:
        logger.info("No results to merge; manifest unchanged.")
        return

    try:
        existing_rows = _read_existing_rows(manifest_path)
    except Exception as exc:
        raise ManifestError(
            f"Failed to read manifest for update: {exc}"
        ) from exc

    updated_rows: list[dict[str, str]] = []
    merged_count = 0

    for row in existing_rows:
        doc_id = row.get("document_id", "")
        result = results.get(doc_id)

        if result is not None:
            row = _merge_result(row, result)
            merged_count += 1

        # Ensure every output column exists in the row
        for col in _OUTPUT_COLUMNS:
            row.setdefault(col, "")

        updated_rows.append(row)

    try:
        _write_rows(manifest_path, updated_rows)
    except Exception as exc:
        raise ManifestError(
            f"Failed to write updated manifest: {exc}"
        ) from exc

    logger.info(
        "Manifest updated: %d of %d results merged into %s",
        merged_count,
        len(results),
        manifest_path,
    )


def _read_existing_rows(manifest_path: Path) -> list[dict[str, str]]:
    """Read all rows from the existing CSV as list of dictionaries.

    Args:
        manifest_path: Path to the CSV file.

    Returns:
        A list of row dictionaries preserving original column order.
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _merge_result(
    row: dict[str, str],
    result: DownloadResult,
) -> dict[str, str]:
    """Merge a DownloadResult into a manifest row dictionary.

    Updates the status, path, checksum, page count, file size,
    timestamp, and attempt count fields.

    Args:
        row: The original CSV row as a mutable dictionary.
        result: The download result to merge.

    Returns:
        The updated row dictionary (same object, mutated in-place).
    """
    row["document_status"] = result.status.value
    row["local_file_path"] = result.file_path
    row["checksum"] = result.checksum
    row["actual_pages"] = str(result.actual_pages) if result.actual_pages else ""
    row["file_size_bytes"] = (
        str(result.file_size_bytes) if result.file_size_bytes else ""
    )
    row["downloaded_at"] = datetime.now(timezone.utc).isoformat()
    row["download_attempts"] = str(result.attempts)
    return row


def _write_rows(
    manifest_path: Path,
    rows: list[dict[str, str]],
) -> None:
    """Write the updated rows back to the manifest CSV.

    Uses ``_OUTPUT_COLUMNS`` as the definitive column order, ensuring
    consistent output regardless of the column order in the original file.

    Args:
        manifest_path: Path to write the CSV.
        rows: The list of row dictionaries to write.
    """
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=_OUTPUT_COLUMNS, extrasaction="ignore"
        )
        writer.writeheader()
        for row in rows:
            filtered = {col: row.get(col, "") for col in _OUTPUT_COLUMNS}
            writer.writerow(filtered)
