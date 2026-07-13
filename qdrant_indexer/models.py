from dataclasses import dataclass
from typing import Any

@dataclass
class QdrantPoint:
    id: str # Qdrant uses UUID or Int. We will assume UUID str.
    vector: list[float]
    payload: dict[str, Any]

@dataclass
class IndexingStats:
    document_id: str
    points_indexed: int
    status: str
    error: str = ""
