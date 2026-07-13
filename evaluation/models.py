from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class GoldenQuery:
    query_id: str
    user_query: str
    category: str
    expected_document: str
    expected_document_id: str
    expected_citation: str
    expected_section: str
    expected_page_number: int
    expected_answer: str
    supporting_chunk_ids: List[str]
    difficulty: str

@dataclass
class EvaluationMetrics:
    # Retrieval
    top_1_accuracy: int
    top_5_accuracy: int
    recall_at_5: float
    recall_at_10: float
    precision_at_5: float
    mrr: float
    ndcg: float
    
    # RAG specific
    citation_accuracy: float
    faithfulness_score: float
    
    # Latency
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    
    # Reliability
    error_category: Optional[str] = None
    success: bool = True

@dataclass
class TraceResult:
    golden_query: GoldenQuery
    metrics: EvaluationMetrics
    generated_answer: str
    retrieved_chunk_ids: List[str]
    verified_citations: List[str]
    unsupported_claims: List[str]
