from __future__ import annotations

import time
from answer_engine.llm_provider import BaseLLMProvider, LLMResponse

class MockProvider(BaseLLMProvider):
    """Mock LLM Provider for local testing and pipeline validation."""
    
    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        time.sleep(0.05) # Simulate network latency
        
        # We simulate a perfect JSON response
        mock_response_json = '''{
  "answer": "Under IRS Section 162, independent contractors may deduct ordinary and necessary business expenses.",
  "citations": [
    {
      "document_title": "Internal Revenue Code",
      "page_number": 1,
      "section": "162(a)",
      "citation": "26 U.S.C. 162"
    }
  ],
  "confidence": "HIGH",
  "limitations": "The provided context does not cover state-specific tax laws."
}'''

        prompt_tokens = len(system_prompt + user_prompt) // 4
        completion_tokens = len(mock_response_json) // 4
        
        return LLMResponse(
            raw_response=mock_response_json,
            latency_s=0.05,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_estimate=0.0001,
            provider_name="mock"
        )
