from __future__ import annotations

import re
from pathlib import Path

def ensure_directory(path: Path | str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def generate_category_slug(category: str) -> str:
    slug = category.lower()
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    return slug.strip('_')
