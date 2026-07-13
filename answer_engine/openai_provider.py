from __future__ import annotations

import time
from answer_engine.llm_provider import BaseLLMProvider, LLMResponse

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider."""
    
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        # In a real impl, we would initialize openai.Client and call chat.completions.create
        raise NotImplementedError("OpenAI API integration requires an API key setup. Use mock for now.")
