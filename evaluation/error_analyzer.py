from evaluation.models import TraceResult, EvaluationMetrics

def classify_error(trace: TraceResult) -> str:
    """Classifies an evaluation failure into standard buckets."""
    m = trace.metrics
    
    if not m.success:
        return "Evaluation Dataset Issue" # Fallback if benchmark crashed
        
    if m.top_5_accuracy == 0:
        return "Wrong Retrieval"
        
    if m.top_1_accuracy == 0 and m.top_5_accuracy == 1:
        return "Wrong Ranking"
        
    if m.citation_accuracy < 0.5:
        return "Wrong Citation"
        
    if trace.unsupported_claims:
        return "Unsupported Claim"
        
    if m.faithfulness_score < 1.0:
        return "Hallucination"
        
    if m.retrieval_time_ms == 0:
        return "Prompt Failure"
        
    return "Other"
