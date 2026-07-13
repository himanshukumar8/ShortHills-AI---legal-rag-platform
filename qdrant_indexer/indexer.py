from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Generator
from qdrant_indexer.models import QdrantPoint, IndexingStats
from qdrant_indexer.utils import generate_uuid
from qdrant_indexer.client import BaseQdrantClient

logger = logging.getLogger(__name__)

def _chunk_list(lst: list, n: int) -> Generator[list, None, None]:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def load_document_points(doc_id: str, chunks_path: Path, embeddings_path: Path) -> list[QdrantPoint]:
    """Loads text metadata and dense vectors, returning unified QdrantPoints."""
    if not chunks_path.exists() or not embeddings_path.exists():
        return []
        
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    with open(embeddings_path, "r", encoding="utf-8") as f:
        embeddings = json.load(f)
        
    # Map chunk_id to embedding vector for O(1) lookup
    vec_map = {e["chunk_id"]: e["embedding_vector"] for e in embeddings}
    points = []
    
    for c in chunks:
        cid = c["chunk_id"]
        if cid not in vec_map:
            continue
            
        vector = vec_map[cid]
        
        # Build strict payload
        payload = {
            "chunk_id": cid,
            "chunk_hash": c["chunk_hash"],
            "parent_document_id": c["parent_document_id"],
            "category": c["category"],
            "document_title": c.get("document_title", ""),
            "citation": c.get("citation", ""),
            "page_start": c.get("page_start", 0),
            "page_end": c.get("page_end", 0),
            "hierarchy_level": c.get("hierarchy_level", 0),
            "cross_references": c.get("cross_references", []),
            "embedding_model": embeddings[0].get("embedding_model", "BAAI/bge-large-en-v1.5")
        }
        
        point_id = generate_uuid(cid)
        points.append(QdrantPoint(id=point_id, vector=vector, payload=payload))
        
    return points

def index_document(client: BaseQdrantClient, collection_name: str, doc_id: str, points: list[QdrantPoint], batch_size: int) -> IndexingStats:
    if not points:
        return IndexingStats(doc_id, 0, "SKIPPED", "No points found")
        
    try:
        for batch in _chunk_list(points, batch_size):
            client.upsert(collection_name, batch)
        return IndexingStats(doc_id, len(points), "SUCCESS")
    except Exception as e:
        logger.error(f"[{doc_id}] Failed to index: {e}")
        return IndexingStats(doc_id, 0, "FAILED", str(e))
