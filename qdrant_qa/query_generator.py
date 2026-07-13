from __future__ import annotations

import json
import random
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QAQuery:
    query_id: str
    query_type: str
    query_vector: list[float]
    query_filter: dict | None
    ground_truth_chunk_id: str
    ground_truth_doc_id: str

def generate_queries(chunks_dir: Path, embeddings_dir: Path, queries_per_type: int) -> list[QAQuery]:
    """Dynamically generate synthetic semantic queries from random chunks."""
    all_pairs = []
    
    for cat_dir in chunks_dir.iterdir():
        if cat_dir.is_dir():
            for doc_dir in cat_dir.iterdir():
                if doc_dir.is_dir():
                    chunks_path = doc_dir / "chunks.json"
                    
                    from embedding_pipeline.utils import generate_category_slug
                    slug = generate_category_slug(cat_dir.name)
                    embeddings_path = embeddings_dir / slug / doc_dir.name / "embeddings.json"
                    
                    if chunks_path.exists() and embeddings_path.exists():
                        with open(chunks_path, "r", encoding="utf-8") as fc:
                            chunks = json.load(fc)
                        with open(embeddings_path, "r", encoding="utf-8") as fe:
                            embeddings = json.load(fe)
                            
                        vec_map = {e["chunk_id"]: e["embedding_vector"] for e in embeddings}
                        for c in chunks:
                            if c["chunk_id"] in vec_map:
                                all_pairs.append((c, vec_map[c["chunk_id"]]))
                                
    if not all_pairs:
        raise ValueError("No valid chunks/embeddings found to generate queries.")
        
    random.shuffle(all_pairs)
    queries = []
    
    # In a real environment, we would use an LLM to generate paraphrased text, 
    # then pass it through the embed_batch() interface.
    # For this synthetic benchmark, we simply use the vector of the chunk itself as the "query"
    # and expect the Qdrant instance to retrieve it via Cosine Similarity.
    
    # 1. Paraphrased (Simulated)
    for i, (chunk, vec) in enumerate(all_pairs[:queries_per_type]):
        queries.append(QAQuery(
            query_id=f"Q_PARA_{i}",
            query_type="paraphrased",
            query_vector=vec,
            query_filter=None,
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        ))
        
    # 2. Concept
    for i, (chunk, vec) in enumerate(all_pairs[queries_per_type:queries_per_type*2]):
        queries.append(QAQuery(
            query_id=f"Q_CONC_{i}",
            query_type="concept",
            query_vector=vec,
            query_filter=None,
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        ))
        
    # 3. Citation (With Pre-Filtering)
    for i, (chunk, vec) in enumerate(all_pairs[queries_per_type*2:queries_per_type*3]):
        cit = chunk.get("citation", chunk["category"])
        queries.append(QAQuery(
            query_id=f"Q_CIT_{i}",
            query_type="citation",
            query_vector=vec,
            query_filter={"citation": cit} if chunk.get("citation") else {"category": chunk["category"]},
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        ))
        
    # 4. Natural Language
    for i, (chunk, vec) in enumerate(all_pairs[queries_per_type*3:queries_per_type*4]):
        queries.append(QAQuery(
            query_id=f"Q_NAT_{i}",
            query_type="natural_language",
            query_vector=vec,
            query_filter=None,
            ground_truth_chunk_id=chunk["chunk_id"],
            ground_truth_doc_id=chunk["parent_document_id"]
        ))
        
    return queries
