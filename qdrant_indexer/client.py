from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from qdrant_indexer.models import QdrantPoint
from qdrant_indexer.exceptions import CollectionError, IndexingError

logger = logging.getLogger(__name__)

class BaseQdrantClient(ABC):
    @abstractmethod
    def create_collection(self, collection_name: str, vector_size: int, distance: str) -> None:
        pass
        
    @abstractmethod
    def create_payload_index(self, collection_name: str, field_name: str, field_schema: str) -> None:
        pass
        
    @abstractmethod
    def upsert(self, collection_name: str, points: list[QdrantPoint]) -> None:
        pass
        
    @abstractmethod
    def count(self, collection_name: str) -> int:
        pass
        
    @abstractmethod
    def search(self, collection_name: str, query_vector: list[float], query_filter: dict | None = None, limit: int = 10) -> list[dict]:
        pass


class MockQdrantClient(BaseQdrantClient):
    def __init__(self):
        self.collections = {}
        
    def create_collection(self, collection_name: str, vector_size: int, distance: str) -> None:
        if collection_name in self.collections:
            logger.info(f"Mock Qdrant: Collection {collection_name} exists, recreating.")
            
        self.collections[collection_name] = {
            "config": {"size": vector_size, "distance": distance},
            "indices": [],
            "points": {}
        }
        logger.info(f"Mock Qdrant: Created collection '{collection_name}' (dim={vector_size}, metric={distance})")
        
    def create_payload_index(self, collection_name: str, field_name: str, field_schema: str) -> None:
        if collection_name not in self.collections:
            raise CollectionError(f"Collection {collection_name} not found.")
        self.collections[collection_name]["indices"].append((field_name, field_schema))
        logger.info(f"Mock Qdrant: Indexed payload field '{field_name}' as {field_schema}.")
        
    def upsert(self, collection_name: str, points: list[QdrantPoint]) -> None:
        if collection_name not in self.collections:
            raise CollectionError(f"Collection {collection_name} not found.")
            
        col = self.collections[collection_name]
        dim = col["config"]["size"]
        
        for p in points:
            if len(p.vector) != dim:
                raise IndexingError(f"Dimension mismatch for {p.id}: expected {dim}, got {len(p.vector)}")
            col["points"][p.id] = p
            
    def count(self, collection_name: str) -> int:
        if collection_name not in self.collections:
            return 0
        return len(self.collections[collection_name]["points"])
        
    def search(self, collection_name: str, query_vector: list[float], query_filter: dict | None = None, limit: int = 10) -> list[dict]:
        """Simulate vector search for QA."""
        if collection_name not in self.collections:
            return []
            
        points = list(self.collections[collection_name]["points"].values())
        
        # Apply strict filtering if requested
        if query_filter:
            for k, v in query_filter.items():
                points = [p for p in points if p.payload.get(k) == v]
                
        # Simulate scoring and sorting
        results = []
        for i, p in enumerate(points[:limit * 5]):
            score = 1.0 - (i * 0.01) # Simulated cosine similarity
            if score < 0.0: score = 0.01
            results.append({
                "id": p.id,
                "score": score,
                "payload": p.payload
            })
            
        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]

def get_qdrant_client(config) -> BaseQdrantClient:
    if config.use_mock:
        logger.info("Using Mock Qdrant Client.")
        return MockQdrantClient()
        
    try:
        from qdrant_client import QdrantClient
        raise NotImplementedError("Real Qdrant client not implemented as Docker is unavailable. Use mock.")
    except ImportError:
        logger.warning("qdrant-client not installed. Falling back to MockQdrantClient.")
        return MockQdrantClient()
