from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMResponse:
    raw_response: str
    latency_s: float
    prompt_tokens: int
    completion_tokens: int
    cost_estimate: float
    provider_name: str

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers (Strategy Pattern)."""
    
    def __init__(self, model_name: str, temperature: float = 0.0, max_tokens: int = 1500):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call the LLM API and return a standard response object."""
        pass
