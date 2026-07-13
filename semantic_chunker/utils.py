from __future__ import annotations

import hashlib
import re
from pathlib import Path

def ensure_directory(path: Path | str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def generate_category_slug(category: str) -> str:
    slug = category.lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    return slug.strip('_')

def compute_chunk_hash(text: str) -> str:
    """Compute a SHA-256 hash for chunk uniqueness validation."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def estimate_tokens(text: str) -> int:
    """Rough heuristic for tokens (words / 0.75)."""
    if not text:
        return 0
    words = len(text.split())
    return int(words / 0.75)
