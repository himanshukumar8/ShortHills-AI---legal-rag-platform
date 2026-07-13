from evaluation.config import WEIGHT_RETRIEVAL, WEIGHT_FAITHFULNESS, WEIGHT_CITATION, WEIGHT_LATENCY, WEIGHT_RELIABILITY, LATENCY_MAX_MS, LATENCY_IDEAL_MS
from evaluation.models import EvaluationMetrics

def compute_overall_quality_score(metrics: EvaluationMetrics) -> float:
    if not metrics.success:
        return 0.0
        
    retrieval_score = metrics.ndcg * 100.0
    faithfulness_score = metrics.faithfulness_score * 100.0
    citation_score = metrics.citation_accuracy * 100.0
    
    # Latency penalty mapping
    # Under ideal -> 100
    # Over max -> 0
    if metrics.total_time_ms <= LATENCY_IDEAL_MS:
        latency_score = 100.0
    elif metrics.total_time_ms >= LATENCY_MAX_MS:
        latency_score = 0.0
    else:
        latency_score = 100.0 * (1 - (metrics.total_time_ms - LATENCY_IDEAL_MS) / (LATENCY_MAX_MS - LATENCY_IDEAL_MS))
        
    reliability_score = 100.0 # Assuming success = true here
    
    final_score = (
        (retrieval_score * WEIGHT_RETRIEVAL) +
        (faithfulness_score * WEIGHT_FAITHFULNESS) +
        (citation_score * WEIGHT_CITATION) +
        (latency_score * WEIGHT_LATENCY) +
        (reliability_score * WEIGHT_RELIABILITY)
    )
    
    return final_score
