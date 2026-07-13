from typing import List
from evaluation.models import GoldenQuery
from answer_engine.models import EngineVerificationOutput, FaithfulnessOutput

def calculate_retrieval_metrics(golden: GoldenQuery, retrieved_ids: List[str]) -> dict:
    expected_doc_id = golden.expected_document_id
    expected_chunk_ids = set(golden.supporting_chunk_ids)
    
    # We simulate reading document IDs from chunk IDs in this mock
    # since chunk IDs often contain the doc ID in our setup
    retrieved_doc_ids = [cid.split("-")[0] + "-" + cid.split("-")[1] if "-" in cid else cid for cid in retrieved_ids]
    
    top_1_acc = 1 if len(retrieved_doc_ids) > 0 and expected_doc_id in retrieved_doc_ids[0] else 0
    top_5_acc = 1 if any(expected_doc_id in did for did in retrieved_doc_ids[:5]) else 0
    
    # Recall @ 5
    retrieved_at_5 = set(retrieved_ids[:5])
    recall_5 = len(expected_chunk_ids.intersection(retrieved_at_5)) / len(expected_chunk_ids) if expected_chunk_ids else 0.0
    
    # Recall @ 10
    retrieved_at_10 = set(retrieved_ids[:10])
    recall_10 = len(expected_chunk_ids.intersection(retrieved_at_10)) / len(expected_chunk_ids) if expected_chunk_ids else 0.0
    
    # Precision @ 5
    precision_5 = len(expected_chunk_ids.intersection(retrieved_at_5)) / 5.0
    
    # MRR (Mean Reciprocal Rank)
    mrr = 0.0
    for i, cid in enumerate(retrieved_ids):
        if cid in expected_chunk_ids:
            mrr = 1.0 / (i + 1)
            break
            
    # NDCG (Simplified binary relevance)
    import math
    dcg = 0.0
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(expected_chunk_ids), len(retrieved_ids))))
    for i, cid in enumerate(retrieved_ids):
        if cid in expected_chunk_ids:
            dcg += 1.0 / math.log2(i + 2)
            
    ndcg = dcg / idcg if idcg > 0 else 0.0
    
    return {
        "top_1_accuracy": top_1_acc,
        "top_5_accuracy": top_5_acc,
        "recall_at_5": recall_5,
        "recall_at_10": recall_10,
        "precision_at_5": precision_5,
        "mrr": mrr,
        "ndcg": ndcg
    }

def calculate_citation_accuracy(citation_output: EngineVerificationOutput) -> float:
    return citation_output.overall_score / 100.0 if citation_output else 0.0

def calculate_faithfulness(faithfulness_output: FaithfulnessOutput) -> float:
    return faithfulness_output.overall_faithfulness_score / 100.0 if faithfulness_output else 0.0
