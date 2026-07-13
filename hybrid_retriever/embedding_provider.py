from __future__ import annotations

import logging
from embedding_pipeline.generator import get_provider, BaseEmbeddingProvider
from embedding_pipeline.config import EmbeddingConfig
from hybrid_retriever.utils import measure_latency
from hybrid_retriever.config import HybridConfig

logger = logging.getLogger(__name__)

class EmbedderWrapper:
    def __init__(self, config: HybridConfig):
        emb_config = EmbeddingConfig()
        provider_name = "mock" if config.use_mock else emb_config.provider
        self.provider: BaseEmbeddingProvider = get_provider(provider_name, emb_config.model_name, emb_config.embedding_dimension)
        
    @measure_latency
    def embed_query(self, query_text: str) -> list[float]:
        try:
            return self.provider.embed_batch([query_text])[0]
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            # Fallback to dimension 1024 for testing
            return [0.0] * 1024
