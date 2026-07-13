from __future__ import annotations

import os
import time
import logging

from answer_engine.llm_provider import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider using the official google-genai SDK."""

    def __init__(self, model_name: str, temperature: float = 0.0, max_tokens: int = 1500):
        super().__init__(model_name, temperature, max_tokens)
        self._client = self._init_client()

    def _init_client(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set. "
                "Obtain a key from https://aistudio.google.com/apikey"
            )

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
        except ImportError:
            raise ImportError(
                "google-genai package is not installed. "
                "Run: pip install google-genai"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Gemini client: {e}")

        return client

    def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call the Gemini API and return a standardized LLMResponse."""
        from google import genai
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        start = time.perf_counter()
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
        except Exception as e:
            latency = time.perf_counter() - start
            error_msg = str(e).lower()
            if "api key" in error_msg or "authenticate" in error_msg or "permission" in error_msg:
                raise PermissionError(f"Gemini authentication failed: {e}")
            elif "quota" in error_msg or "rate" in error_msg or "resource" in error_msg:
                raise RuntimeError(f"Gemini quota/rate limit exceeded: {e}")
            elif "timeout" in error_msg or "deadline" in error_msg:
                raise TimeoutError(f"Gemini request timed out after {latency:.2f}s: {e}")
            else:
                raise ConnectionError(f"Gemini API call failed: {e}")

        latency = time.perf_counter() - start

        # Extract text from the response
        raw_text = ""
        if response and response.text:
            raw_text = response.text
        if not raw_text.strip():
            raise ValueError(
                "Gemini returned an empty response. "
                "The model may have refused the prompt or hit a safety filter."
            )

        # Extract token usage if available, otherwise estimate
        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        if prompt_tokens == 0:
            prompt_tokens = len(system_prompt + user_prompt) // 4
        if completion_tokens == 0:
            completion_tokens = len(raw_text) // 4

        logger.info(
            f"Gemini response received in {latency:.2f}s "
            f"(prompt={prompt_tokens}, completion={completion_tokens})"
        )

        return LLMResponse(
            raw_response=raw_text,
            latency_s=latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_estimate=0.0,
            provider_name="gemini",
        )
