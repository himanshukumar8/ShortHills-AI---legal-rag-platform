from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from embedding_pipeline.models import EmbeddingRecord
from embedding_pipeline.utils import ensure_directory, generate_category_slug

def write_embeddings(records: list[EmbeddingRecord], document_id: str, category: str, base_output_dir: Path) -> None:
    category_slug = generate_category_slug(category)
    doc_dir = base_output_dir / category_slug / document_id
    ensure_directory(doc_dir)
    
    # In a real pipeline, we might use JSONL or Parquet for massive datasets.
    # JSON is acceptable here given we partition by document.
    data = [asdict(r) for r in records]
    
    with open(doc_dir / "embeddings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
