from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from chunk_optimizer.models import OptimizedChunk
from semantic_chunker.utils import ensure_directory, generate_category_slug

def write_optimized_chunks(chunks: list[OptimizedChunk], document_id: str, category: str, base_output_dir: Path) -> None:
    category_slug = generate_category_slug(category)
    doc_dir = base_output_dir / category_slug / document_id
    ensure_directory(doc_dir)
    
    chunk_dicts = [asdict(c) for c in chunks]
    
    with open(doc_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunk_dicts, f, indent=2, ensure_ascii=False)
        
    chunk_index = {c.chunk_id: c.chunk_hash for c in chunks}
    with open(doc_dir / "chunk_index.json", "w", encoding="utf-8") as f:
        json.dump(chunk_index, f, indent=2)
