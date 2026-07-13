from __future__ import annotations

import logging
from qdrant_indexer.client import get_qdrant_client, BaseQdrantClient
from qdrant_indexer.config import QdrantConfig
from hybrid_retriever.utils import measure_latency
from hybrid_retriever.config import HybridConfig

logger = logging.getLogger(__name__)

class QdrantRetriever:
    def __init__(self, config: HybridConfig):
        qd_config = QdrantConfig()
        qd_config.use_mock = config.use_mock
        self.client: BaseQdrantClient = get_qdrant_client(qd_config)
        self.collection_name = config.qdrant_collection_name
        self.top_k = config.top_k
        
    @measure_latency
    def retrieve(self, query_vector: list[float], filters: dict | None = None) -> list[dict]:
        """Execute a dense semantic search returning hit payloads."""
        try:
            hits = self.client.search(self.collection_name, query_vector, filters, limit=self.top_k * 5)
            # Hits contain id, score, payload. We want payload for RRF.
            return [h.get("payload", {}) for h in hits]
        except Exception as e:
            logger.error(f"Qdrant retrieval failed: {e}")
            return []
