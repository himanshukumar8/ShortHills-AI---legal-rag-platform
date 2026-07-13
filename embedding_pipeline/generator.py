from __future__ import annotations

import hashlib
import random
from abc import ABC, abstractmethod
from typing import Any
import time

class BaseEmbeddingProvider(ABC):
    """Abstract base class for all embedding providers (Strategy Pattern)."""
    
    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of strings."""
        pass


class MockProvider(BaseEmbeddingProvider):
    """A deterministic mock provider for testing without GPU/API keys."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Simulate network/compute latency
        time.sleep(0.01)
        results = []
        for text in texts:
            # Deterministic pseudo-random generation based on text hash
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
            rng = random.Random(seed)
            # Create a normalized random vector
            vec = [rng.gauss(0, 1) for _ in range(self.dimension)]
            magnitude = sum(x*x for x in vec) ** 0.5
            if magnitude > 0:
                vec = [x / magnitude for x in vec]
            results.append(vec)
        return results


class OpenAIProvider(BaseEmbeddingProvider):
    """Provider for OpenAI embeddings API."""
    
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        # In a real impl: self.client = OpenAI(api_key=api_key)
        
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("OpenAI integration pending API key setup.")


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Provider for local BAAI / HuggingFace models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise RuntimeError("sentence-transformers is not installed. Use provider='mock' for testing.")
            
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # model.encode returns numpy arrays, we convert to standard float lists for JSON serialization
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


def get_provider(provider_name: str, model_name: str, dimension: int) -> BaseEmbeddingProvider:
    """Factory method to instantiate the correct strategy."""
    name = provider_name.lower()
    if name == "mock":
        return MockProvider(dimension=dimension)
    elif name == "openai":
        return OpenAIProvider(model_name=model_name, api_key="placeholder")
    elif name == "sentence_transformers":
        return SentenceTransformerProvider(model_name=model_name)
    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")
