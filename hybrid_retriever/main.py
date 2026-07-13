from __future__ import annotations

import hashlib
import logging
import sys
import time
import uuid

from hybrid_retriever.config import HybridConfig
from hybrid_retriever.elasticsearch_client import ElasticsearchRetriever
from hybrid_retriever.qdrant_client import QdrantRetriever
from hybrid_retriever.embedding_provider import EmbedderWrapper
from hybrid_retriever.metadata_filter import extract_filters
from hybrid_retriever.fusion import reciprocal_rank_fusion
from hybrid_retriever.ranker import rank_and_truncate
from hybrid_retriever.citation_validator import validate_citations
from hybrid_retriever.validator import verify_output
from hybrid_retriever.response_builder import build_response
from hybrid_retriever.reporter import generate_reports
from hybrid_retriever.models import RetrievalTrace

logger = logging.getLogger("hybrid_retriever")

# ---------------------------------------------------------------------------
# In-memory mock corpus — 8 representative legal chunks.
# Used ONLY when use_mock=True so Render (and CI) never touch the filesystem.
# ---------------------------------------------------------------------------
_MOCK_LEGAL_CHUNKS: list[dict] = [
    {
        "chunk_id": "mock-chunk-tax-001",
        "document_id": "doc-irc-162",
        "parent_document_id": "doc-irc-162",
        "document_title": "Internal Revenue Code — Section 162",
        "category": "Tax Law",
        "text": (
            "Section 162 of the Internal Revenue Code allows a deduction for all "
            "ordinary and necessary expenses paid or incurred during the taxable year "
            "in carrying on any trade or business. This includes reasonable salaries, "
            "travel expenses, and rental payments for property used in the trade or business."
        ),
        "citation": "26 U.S.C. § 162",
        "cross_references": ["26 U.S.C. § 212", "26 U.S.C. § 262"],
        "page_start": 1,
        "page_end": 3,
        "hierarchy_level": 1,
        "chunk_hash": "a1b2c3d4e5f6",
    },
    {
        "chunk_id": "mock-chunk-tax-002",
        "document_id": "doc-irc-1",
        "parent_document_id": "doc-irc-1",
        "document_title": "Internal Revenue Code — Section 1",
        "category": "Tax Law",
        "text": (
            "Section 1 of Title 26 imposes a tax on the taxable income of every "
            "individual, estate, and trust. Tax rates are graduated and depend on "
            "filing status. Independent contractors are generally subject to "
            "self-employment tax under Section 1401 in addition to income tax."
        ),
        "citation": "26 U.S.C. § 1",
        "cross_references": ["26 U.S.C. § 1401", "26 U.S.C. § 162"],
        "page_start": 1,
        "page_end": 2,
        "hierarchy_level": 1,
        "chunk_hash": "b2c3d4e5f6a1",
    },
    {
        "chunk_id": "mock-chunk-const-001",
        "document_id": "doc-const-amend-1",
        "parent_document_id": "doc-const-amend-1",
        "document_title": "United States Constitution — First Amendment",
        "category": "Constitutional Law",
        "text": (
            "Congress shall make no law respecting an establishment of religion, or "
            "prohibiting the free exercise thereof; or abridging the freedom of speech, "
            "or of the press; or the right of the people peaceably to assemble, and to "
            "petition the Government for a redress of grievances."
        ),
        "citation": "U.S. Const. amend. I",
        "cross_references": ["U.S. Const. amend. XIV"],
        "page_start": 10,
        "page_end": 10,
        "hierarchy_level": 0,
        "chunk_hash": "c3d4e5f6a1b2",
    },
    {
        "chunk_id": "mock-chunk-const-002",
        "document_id": "doc-const-amend-14",
        "parent_document_id": "doc-const-amend-14",
        "document_title": "United States Constitution — Fourteenth Amendment",
        "category": "Constitutional Law",
        "text": (
            "No State shall make or enforce any law which shall abridge the privileges "
            "or immunities of citizens of the United States; nor shall any State deprive "
            "any person of life, liberty, or property, without due process of law; nor "
            "deny to any person within its jurisdiction the equal protection of the laws."
        ),
        "citation": "U.S. Const. amend. XIV, § 1",
        "cross_references": ["U.S. Const. amend. I", "U.S. Const. amend. V"],
        "page_start": 15,
        "page_end": 16,
        "hierarchy_level": 0,
        "chunk_hash": "d4e5f6a1b2c3",
    },
    {
        "chunk_id": "mock-chunk-contract-001",
        "document_id": "doc-ucc-art2",
        "parent_document_id": "doc-ucc-art2",
        "document_title": "Uniform Commercial Code — Article 2",
        "category": "Contract Law",
        "text": (
            "Article 2 of the Uniform Commercial Code governs the sale of goods. "
            "Under UCC § 2-204, a contract for sale of goods may be made in any manner "
            "sufficient to show agreement, including conduct by both parties which "
            "recognizes the existence of such a contract."
        ),
        "citation": "UCC § 2-204",
        "cross_references": ["UCC § 2-302", "UCC § 2-615"],
        "page_start": 20,
        "page_end": 22,
        "hierarchy_level": 1,
        "chunk_hash": "e5f6a1b2c3d4",
    },
    {
        "chunk_id": "mock-chunk-env-001",
        "document_id": "doc-caa-101",
        "parent_document_id": "doc-caa-101",
        "document_title": "Clean Air Act — Section 101",
        "category": "Environmental Law",
        "text": (
            "The Clean Air Act establishes federal standards for air quality and "
            "authorizes the EPA to regulate emissions of hazardous air pollutants. "
            "Section 101 declares that the purpose of the Act is to protect and enhance "
            "the quality of the Nation's air resources."
        ),
        "citation": "42 U.S.C. § 7401",
        "cross_references": ["42 U.S.C. § 7412", "42 U.S.C. § 7661"],
        "page_start": 1,
        "page_end": 4,
        "hierarchy_level": 1,
        "chunk_hash": "f6a1b2c3d4e5",
    },
    {
        "chunk_id": "mock-chunk-crim-001",
        "document_id": "doc-title18-1341",
        "parent_document_id": "doc-title18-1341",
        "document_title": "Federal Mail Fraud Statute",
        "category": "Criminal Law",
        "text": (
            "18 U.S.C. § 1341 prohibits the use of the United States Postal Service "
            "or other interstate delivery services for the purpose of executing a "
            "scheme to defraud. Violations are punishable by fines and imprisonment "
            "of up to 20 years, or 30 years if the fraud affects a financial institution."
        ),
        "citation": "18 U.S.C. § 1341",
        "cross_references": ["18 U.S.C. § 1343", "18 U.S.C. § 1346"],
        "page_start": 5,
        "page_end": 7,
        "hierarchy_level": 1,
        "chunk_hash": "a1c3e5b2d4f6",
    },
    {
        "chunk_id": "mock-chunk-emp-001",
        "document_id": "doc-flsa-201",
        "parent_document_id": "doc-flsa-201",
        "document_title": "Fair Labor Standards Act — Section 201",
        "category": "Employment Law",
        "text": (
            "The Fair Labor Standards Act establishes minimum wage, overtime pay, "
            "recordkeeping, and child labor standards affecting full-time and "
            "part-time workers in the private sector and in Federal, State, and local "
            "governments. Independent contractors are generally not covered by FLSA."
        ),
        "citation": "29 U.S.C. § 201",
        "cross_references": ["29 U.S.C. § 206", "29 U.S.C. § 207"],
        "page_start": 1,
        "page_end": 3,
        "hierarchy_level": 1,
        "chunk_hash": "b2d4f6a1c3e5",
    },
]

_VECTOR_DIM = 1024


def _generate_deterministic_vector(seed_str: str) -> list[float]:
    """Generate a deterministic 1024-dim pseudo-vector from a string seed."""
    import hashlib as _hl
    # Use repeated hashing to fill the vector
    vector: list[float] = []
    block = seed_str.encode("utf-8")
    while len(vector) < _VECTOR_DIM:
        block = _hl.sha512(block).digest()
        for byte in block:
            if len(vector) >= _VECTOR_DIM:
                break
            vector.append((byte - 128) / 128.0)  # normalize to [-1, 1]
    return vector


def _seed_mock_environment(config: HybridConfig):
    """
    Populate mock ES and Qdrant clients with the in-memory corpus.
    Returns (mock_es_client, mock_qdrant_client) pre-loaded with data.
    No filesystem access occurs.
    """
    from es_indexer.client import MockESClient
    from es_indexer.schema import INDEX_MAPPING, INDEX_SETTINGS
    from qdrant_indexer.client import MockQdrantClient
    from qdrant_indexer.models import QdrantPoint

    # --- Elasticsearch ---
    es_client = MockESClient()
    es_client.create_index(config.es_index_name, INDEX_SETTINGS, INDEX_MAPPING)

    es_docs = []
    for chunk in _MOCK_LEGAL_CHUNKS:
        es_docs.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "category": chunk["category"],
            "text": chunk["text"],
            "citation": chunk["citation"],
            "cross_references": chunk.get("cross_references", []),
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "hierarchy_level": chunk.get("hierarchy_level", 0),
        })
    es_client.bulk_index(config.es_index_name, es_docs)
    logger.info(f"Mock ES seeded with {len(es_docs)} in-memory chunks.")

    # --- Qdrant ---
    qd_client = MockQdrantClient()
    qd_client.create_collection(
        collection_name=config.qdrant_collection_name,
        vector_size=_VECTOR_DIM,
        distance="Cosine",
    )
    # Create payload indices matching production setup
    for field in ["category", "parent_document_id", "citation"]:
        qd_client.create_payload_index(
            config.qdrant_collection_name, field, "keyword"
        )

    points = []
    for chunk in _MOCK_LEGAL_CHUNKS:
        point_id = str(uuid.UUID(hashlib.md5(chunk["chunk_id"].encode("utf-8")).hexdigest()))
        vector = _generate_deterministic_vector(chunk["chunk_id"])
        payload = {
            "chunk_id": chunk["chunk_id"],
            "chunk_hash": chunk.get("chunk_hash", ""),
            "parent_document_id": chunk["document_id"],
            "category": chunk["category"],
            "document_title": chunk.get("document_title", ""),
            "citation": chunk["citation"],
            "page_start": chunk.get("page_start", 0),
            "page_end": chunk.get("page_end", 0),
            "hierarchy_level": chunk.get("hierarchy_level", 0),
            "cross_references": chunk.get("cross_references", []),
            "embedding_model": "mock-deterministic",
        }
        points.append(QdrantPoint(id=point_id, vector=vector, payload=payload))

    qd_client.upsert(config.qdrant_collection_name, points)
    logger.info(f"Mock Qdrant seeded with {len(points)} in-memory vectors.")

    return es_client, qd_client


def run_pipeline(config: HybridConfig | None = None, query: str = "Taxation rules for independent contractors under IRS Section 162") -> dict:
    if config is None:
        config = HybridConfig()
        
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval Pipeline \u2014 Starting")
    logger.info(f"Query: '{query}'")
    logger.info("=" * 60)
    
    # 0. Setup Mock or Production Environment
    if config.use_mock:
        logger.info("Initializing Mock Environment (in-memory, no filesystem)...")
        mock_es, mock_qd = _seed_mock_environment(config)
        es_retriever = ElasticsearchRetriever(config, client=mock_es)
        qd_retriever = QdrantRetriever(config, client=mock_qd)
    else:
        # Production path — uses real indexer pipelines and clients
        from es_indexer.main import run_pipeline as run_es
        from es_indexer.config import ESIndexerConfig
        from qdrant_indexer.main import run_pipeline as run_qd
        from qdrant_indexer.config import QdrantConfig

        logger.info("Initializing Indexers (Production Environment Setup)...")
        logging.getLogger("es_indexer").setLevel(logging.WARNING)
        logging.getLogger("qdrant_indexer").setLevel(logging.WARNING)
        run_es(ESIndexerConfig(use_mock=True))
        run_qd(QdrantConfig(use_mock=True))
        es_retriever = ElasticsearchRetriever(config)
        qd_retriever = QdrantRetriever(config)

    embedder = EmbedderWrapper(config)
    
    total_start = time.monotonic()
    
    # 1. Metadata Filters Extraction
    filters = extract_filters(query)
    if filters:
        logger.info(f"Extracted metadata pre-filters: {filters}")
        
    # 2. Embedding Generation
    query_vector, emb_lat = embedder.embed_query(query)
    logger.info(f"Generated query embedding in {emb_lat:.4f}s")
    
    # 3. Parallel Retrieval (Simulated sequentially here)
    logger.info("Executing Elasticsearch (BM25)...")
    es_hits, es_lat = es_retriever.retrieve(query, filters)
    
    logger.info("Executing Qdrant (Dense Vector)...")
    qd_hits, qd_lat = qd_retriever.retrieve(query_vector, filters)
    
    logger.info(f"Candidate set: {len(es_hits)} lexical hits, {len(qd_hits)} semantic hits")
    
    # 4. Fusion
    logger.info(f"Applying Reciprocal Rank Fusion (k={config.rrf_k})...")
    fused_dict, fuse_lat = reciprocal_rank_fusion(es_hits, qd_hits, config.rrf_k)
    
    # 5. Ranking & Deduplication (Implicit in dictionary keys)
    final_results = rank_and_truncate(fused_dict, config.top_k)
    
    # 6. Verification
    validate_citations(final_results)
    val_res = verify_output(final_results, config.top_k)
    if val_res["is_valid"]:
        logger.info("Hybrid Pipeline Validation PASSED.")
    else:
        logger.error(f"Validation FAILED: {val_res['issues']}")
        
    total_lat = time.monotonic() - total_start
    
    # 7. Trace and Response
    trace = RetrievalTrace(
        query=query,
        embedding_latency=emb_lat,
        es_latency=es_lat,
        qdrant_latency=qd_lat,
        fusion_latency=fuse_lat,
        total_latency=total_lat,
        es_candidate_count=len(es_hits),
        qdrant_candidate_count=len(qd_hits),
        rrf_k=config.rrf_k,
        results=final_results
    )
    
    response = build_response(trace)
    generate_reports(config.report_dir, response, val_res)
    
    logger.info("=" * 60)
    logger.info(f"Hybrid Retrieval complete in {total_lat:.4f}s")
    logger.info(f"Retrieved Top-{len(final_results)} chunks.")
    logger.info("=" * 60)
    
    return response

def _setup_logging(config: HybridConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("hybrid_retriever")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | HYBRID | %(message)s"))
    root_logger.addHandler(console_handler)

if __name__ == "__main__":
    run_pipeline()
