from __future__ import annotations

import json
from pathlib import Path
from typing import Generator

def _chunk_list(lst: list, n: int) -> Generator[list, None, None]:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def parse_optimized_chunks(doc_dir: Path) -> list[dict]:
    chunks_path = doc_dir / "chunks.json"
    if not chunks_path.exists():
        return []
        
    with open(chunks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    documents = []
    for chunk in data:
        # Map the OptimizedChunk fields exactly to the Elasticsearch Schema
        es_doc = {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["parent_document_id"],
            "category": chunk["category"],
            "text": chunk["text"],
            "citation": chunk.get("citation", ""),
            "cross_references": chunk.get("cross_references", []),
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "hierarchy_level": chunk.get("hierarchy_level", 0)
        }
        documents.append(es_doc)
        
    return documents
