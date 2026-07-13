from __future__ import annotations

"""Utility functions for the Document Normalization Pipeline."""

import re
from pathlib import Path

def ensure_directory(path: Path | str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)

def generate_category_slug(category: str) -> str:
    """Generate a filesystem-friendly slug for a category.
    
    Args:
        category: The raw category string (e.g., 'Acts / Statutes')
        
    Returns:
        A safe string (e.g., 'acts_statutes')
    """
    slug = category.lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    return slug.strip('_')
