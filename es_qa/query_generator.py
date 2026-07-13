from __future__ import annotations

import json
import random
import re
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QAQuery:
    query_id: str
    query_type: str
    query_dsl: dict
    ground_truth_chunk_id: str
    ground_truth_doc_id: str

def _extract_words(text: str) -> list[str]:
    # Extract alphanumeric words > 4 chars
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text)
    return [w for w in words if w.lower() not in {"section", "paragraph", "which", "shall"}]

def generate_queries(chunks_dir: Path, queries_per_type: int) -> list[QAQuery]:
    """Dynamically generate synthetic queries from random chunks."""
    all_chunks = []
    
    for cat_dir in chunks_dir.iterdir():
        if cat_dir.is_dir():
            for doc_dir in cat_dir.iterdir():
                if doc_dir.is_dir():
                    chunks_path = doc_dir / "chunks.json"
                    if chunks_path.exists():
                        with open(chunks_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            all_chunks.extend(data)
                            
    if not all_chunks:
        raise ValueError("No chunks found to generate queries.")
        
    random.shuffle(all_chunks)
    queries = []
    
    # 1. Exact Citation
    chunks_with_citation = [c for c in all_chunks if c.get("citation")]
    selected_cit = chunks_with_citation[:queries_per_type] if chunks_with_citation else all_chunks[:queries_per_type]
    for i, chunk in enumerate(selected_cit):
        cit = chunk.get("citation", "")
        if not cit:
            cit = chunk.get("chunk_id") # fallback
        q = QAQuery(
            query_id=f"Q_CIT_{i}",
            query_type="citation",
            query_dsl={"term": {"citation": cit}},
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        )
        queries.append(q)
        
    # 2. Keyword Search
    for i, chunk in enumerate(all_chunks[:queries_per_type]):
        words = _extract_words(chunk["text"])
        term = words[0] if words else chunk["chunk_id"]
        q = QAQuery(
            query_id=f"Q_KEY_{i}",
            query_type="keyword",
            query_dsl={"match": {"text": term}},
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        )
        queries.append(q)
        
    # 3. Phrase Search
    for i, chunk in enumerate(all_chunks[queries_per_type:queries_per_type*2]):
        words = chunk["text"].split()
        phrase = " ".join(words[:4]) if len(words) >= 4 else chunk["text"]
        q = QAQuery(
            query_id=f"Q_PHR_{i}",
            query_type="phrase",
            query_dsl={"match_phrase": {"text": phrase}},
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        )
        queries.append(q)
        
    # 4. Boolean Queries
    for i, chunk in enumerate(all_chunks[queries_per_type*2:queries_per_type*3]):
        words = _extract_words(chunk["text"])
        term1 = words[0] if len(words) > 0 else chunk["chunk_id"]
        term2 = words[1] if len(words) > 1 else term1
        q = QAQuery(
            query_id=f"Q_BOOL_{i}",
            query_type="boolean",
            query_dsl={
                "bool": {
                    "must": [
                        {"match": {"text": term1}},
                        {"match": {"text": term2}}
                    ]
                }
            },
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        )
        queries.append(q)
        
    # 5. Metadata filtering
    for i, chunk in enumerate(all_chunks[queries_per_type*3:queries_per_type*4]):
        words = _extract_words(chunk["text"])
        term = words[0] if words else chunk["chunk_id"]
        q = QAQuery(
            query_id=f"Q_META_{i}",
            query_type="metadata",
            query_dsl={
                "bool": {
                    "must": [{"match": {"text": term}}],
                    "filter": [{"term": {"category": chunk["category"]}}]
                }
            },
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        )
        queries.append(q)
        
    return queries
