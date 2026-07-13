from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

class BaseESClient(ABC):
    @abstractmethod
    def create_index(self, index_name: str, settings: dict, mapping: dict) -> None:
        pass

    @abstractmethod
    def bulk_index(self, index_name: str, documents: list[dict]) -> tuple[int, int]:
        """Returns (success_count, error_count)"""
        pass
        
    @abstractmethod
    def count(self, index_name: str) -> int:
        pass
        
    @abstractmethod
    def search(self, index_name: str, query: dict) -> dict:
        pass


class MockESClient(BaseESClient):
    """In-memory mock for validating Elasticsearch indexing logic."""
    def __init__(self):
        self.indices = {}
        
    def create_index(self, index_name: str, settings: dict, mapping: dict) -> None:
        if index_name in self.indices:
            logger.info(f"Mock index {index_name} already exists. Recreating.")
        self.indices[index_name] = {
            "settings": settings,
            "mapping": mapping,
            "documents": {} # chunk_id -> doc
        }
        logger.info(f"Mock created index {index_name}")

    def bulk_index(self, index_name: str, documents: list[dict]) -> tuple[int, int]:
        if index_name not in self.indices:
            raise ValueError(f"Index {index_name} does not exist.")
            
        success = 0
        errors = 0
        
        for doc in documents:
            chunk_id = doc.get("chunk_id")
            if not chunk_id:
                errors += 1
                continue
            self.indices[index_name]["documents"][chunk_id] = doc
            success += 1
            
        return success, errors

    def count(self, index_name: str) -> int:
        if index_name not in self.indices:
            return 0
        return len(self.indices[index_name]["documents"])
        
    def search(self, index_name: str, query: dict) -> dict:
        """Simulate basic exact matching for validation."""
        if index_name not in self.indices:
            return {"hits": {"total": {"value": 0}, "hits": []}}
            
        docs = list(self.indices[index_name]["documents"].values())
        matches = []
        
        # A very hacky mock search to allow the QA module to run
        if "term" in query:
            field = list(query["term"].keys())[0]
            val = query["term"][field]
            matches = [d for d in docs if d.get(field) == val]
        elif "match" in query:
            field = list(query["match"].keys())[0]
            val = query["match"][field]
            matches = [d for d in docs if val.lower() in d.get(field, "").lower()]
        elif "match_phrase" in query:
            field = list(query["match_phrase"].keys())[0]
            val = query["match_phrase"][field]
            matches = [d for d in docs if val.lower() in d.get(field, "").lower()]
        elif "bool" in query:
            # just return a random sample containing the first doc + some noise to simulate BM25 recall
            matches = docs[:50]
        else:
            matches = docs[:100]
            
        # Simulate scoring (higher for exact matches)
        scored_hits = []
        for i, d in enumerate(matches[:20]):
            scored_hits.append({
                "_id": d["chunk_id"],
                "_score": 10.0 / (i + 1),
                "_source": d
            })
            
        return {
            "hits": {
                "total": {"value": len(matches)},
                "hits": scored_hits
            }
        }

def get_es_client(config) -> BaseESClient:
    if config.use_mock:
        logger.info("Using Mock Elasticsearch Client.")
        return MockESClient()
    
    # Real ES client would be imported here
    try:
        from elasticsearch import Elasticsearch
        # Implementation of a RealESClient wrapper...
        raise NotImplementedError("Real ES client not fully implemented; Docker is unavailable. Use Mock.")
    except ImportError:
        logger.warning("elasticsearch package not installed. Falling back to MockESClient.")
        return MockESClient()
