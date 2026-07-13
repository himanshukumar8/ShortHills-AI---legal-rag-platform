from __future__ import annotations

import logging
from es_indexer.client import get_es_client, BaseESClient
from es_indexer.config import ESIndexerConfig
from hybrid_retriever.utils import measure_latency
from hybrid_retriever.config import HybridConfig

logger = logging.getLogger(__name__)

class ElasticsearchRetriever:
    def __init__(self, config: HybridConfig, client: BaseESClient | None = None):
        if client is not None:
            self.client: BaseESClient = client
        else:
            es_config = ESIndexerConfig()
            es_config.use_mock = config.use_mock
            self.client = get_es_client(es_config)
        self.index_name = config.es_index_name
        self.top_k = config.top_k
        
    @measure_latency
    def retrieve(self, query_text: str, filters: dict | None = None) -> list[dict]:
        """Execute a BM25 keyword search returning hit sources."""
        # Build query DSL
        dsl = {
            "bool": {
                "must": [{"match": {"text": query_text}}]
            }
        }
        
        if filters:
            dsl["bool"]["filter"] = [{"term": {k: v}} for k, v in filters.items()]
            
        try:
            res = self.client.search(self.index_name, dsl)
            hits = res.get("hits", {}).get("hits", [])
            # Return ordered list of source dictionaries with rank implicitly defined by index
            return [h.get("_source", {}) for h in hits[:self.top_k * 5]] # fetch more for fusion
        except Exception as e:
            logger.error(f"Elasticsearch retrieval failed: {e}")
            return []
