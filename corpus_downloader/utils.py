"""Utility functions for the Corpus Download Pipeline.

Provides stateless helper functions for category-to-folder mapping,
filename sanitization, path construction, and directory management.
These are intentionally kept as pure functions with no side effects
(except ensure_directory) for easy testability.
"""

import re
from pathlib import Path

from corpus_downloader.models import DocumentCategory

# Mapping from manifest category strings to filesystem folder names.
# Keys must exactly match the values in the DocumentCategory enum.
_CATEGORY_FOLDER_MAP: dict[str, str] = {
    DocumentCategory.ACTS_STATUTES.value: "acts",
    DocumentCategory.COURT_JUDGMENTS.value: "court_judgments",
    DocumentCategory.IRS_PUBLICATIONS.value: "irs_publications",
    DocumentCategory.TREASURY_REGS.value: "regulations",
    DocumentCategory.LEGAL_COMMENTARY.value: "commentary",
}

# Maximum base filename length (excluding extension) to respect
# filesystem limits on all major operating systems.
_MAX_FILENAME_BASE_LENGTH: int = 100


def category_to_folder(category: str) -> str:
    """Convert a manifest category string to its filesystem folder name.

    Args:
        category: The category value from the manifest CSV
            (e.g., ``"Acts / Statutes"``).

    Returns:
        The corresponding folder name (e.g., ``"acts"``).

    Raises:
        ValueError: If the category is not in the allowed set.
    """
    folder = _CATEGORY_FOLDER_MAP.get(category)
    if folder is None:
        valid_categories = ", ".join(sorted(_CATEGORY_FOLDER_MAP.keys()))
        raise ValueError(
            f"Unknown category '{category}'. "
            f"Valid categories: {valid_categories}"
        )
    return folder


def sanitize_filename(document_id: str, title: str) -> str:
    """Generate a safe filesystem filename from a document ID and title.

    Produces a filename in the format ``{document_id}_{sanitized_title}.pdf``.
    Non-alphanumeric characters (except hyphens) are replaced with
    underscores, and consecutive underscores are collapsed.

    Args:
        document_id: The unique document identifier (e.g., ``"ACT-01"``).
        title: The document title.

    Returns:
        A sanitized filename string ending in ``.pdf``.

    Examples:
        >>> sanitize_filename("IRS-08", "Publication 463: Travel, Gift, and Car Expenses")
        'IRS-08_Publication_463_Travel_Gift_and_Car_Expenses.pdf'
    """
    # Remove characters that are unsafe for filenames
    sanitized = re.sub(r"[^\w\s-]", "", title)
    # Replace whitespace runs with single underscore
    sanitized = re.sub(r"\s+", "_", sanitized.strip())
    # Collapse multiple underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    # Truncate and strip trailing underscores
    sanitized = sanitized[:_MAX_FILENAME_BASE_LENGTH].rstrip("_")
    return f"{document_id}_{sanitized}.pdf"


def build_file_path(
    download_dir: Path,
    category: str,
    document_id: str,
    title: str,
) -> Path:
    """Construct the full local file path where a document will be stored.

    Args:
        download_dir: The base download directory (e.g., ``data/raw``).
        category: The document category from the manifest.
        document_id: The unique document identifier.
        title: The document title.

    Returns:
        The full Path for the document file.

    Example:
        ``data/raw/acts/ACT-01_Tax_Cuts_and_Jobs_Act_of_2017.pdf``
    """
    folder_name = category_to_folder(category)
    filename = sanitize_filename(document_id, title)
    return download_dir / folder_name / filename


def ensure_directory(path: Path) -> None:
    """Create a directory and all parent directories if they do not exist.

    This is a no-op if the directory already exists.

    Args:
        path: The directory path to create.
    """
    path.mkdir(parents=True, exist_ok=True)
