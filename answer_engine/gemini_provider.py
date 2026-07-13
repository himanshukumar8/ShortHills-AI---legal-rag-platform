from __future__ import annotations

import time
from answer_engine.llm_provider import BaseLLMProvider, LLMResponse

class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider."""
    
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        # In a real impl, we would initialize google.generativeai and call generate_content
        raise NotImplementedError("Gemini API integration requires an API key setup. Use mock for now.")
