from __future__ import annotations

import math
from embedding_pipeline.exceptions import ValidationError

def validate_embeddings(vectors: list[list[float]], expected_dimension: int, document_id: str) -> None:
    """Validate mathematical correctness of the generated embeddings."""
    
    for i, vec in enumerate(vectors):
        if len(vec) != expected_dimension:
            raise ValidationError(
                f"Vector at index {i} has dimension {len(vec)}, expected {expected_dimension}.",
                document_id
            )
            
        magnitude_sq = 0.0
        for val in vec:
            if math.isnan(val):
                raise ValidationError(f"NaN value detected in vector at index {i}.", document_id)
            if math.isinf(val):
                raise ValidationError(f"Infinity detected in vector at index {i}.", document_id)
            magnitude_sq += val * val
            
        if magnitude_sq == 0.0:
            raise ValidationError(f"Zero vector detected at index {i} (magnitude is 0).", document_id)
