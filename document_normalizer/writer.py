from __future__ import annotations

"""File writing logic for normalized documents."""

import json
from dataclasses import asdict
from pathlib import Path

from document_normalizer.models import NormalizedDocument
from document_normalizer.utils import ensure_directory, generate_category_slug

def write_normalized_document(document: NormalizedDocument, base_output_dir: Path) -> None:
    """Write the normalized document components to disk.
    
    Creates:
      - normalized_document.json (full structured data)
      - normalized_pages.json (just the page array for easy iteration)
      - normalized_full_text.txt (pure text for embedding/chunking)
      
    Args:
        document: The NormalizedDocument to save.
        base_output_dir: The root output directory (e.g., 'data/normalized').
    """
    category_slug = generate_category_slug(document.metadata.category)
    doc_dir = base_output_dir / category_slug / document.metadata.document_id
    ensure_directory(doc_dir)
    
    doc_dict = asdict(document)
    
    # 1. Full document JSON
    with open(doc_dir / "normalized_document.json", "w", encoding="utf-8") as f:
        json.dump(doc_dict, f, indent=2, ensure_ascii=False)
        
    # 2. Pages array JSON
    with open(doc_dir / "normalized_pages.json", "w", encoding="utf-8") as f:
        json.dump(doc_dict["pages"], f, indent=2, ensure_ascii=False)
        
    # 3. Full text TXT
    with open(doc_dir / "normalized_full_text.txt", "w", encoding="utf-8") as f:
        f.write(document.full_text)
