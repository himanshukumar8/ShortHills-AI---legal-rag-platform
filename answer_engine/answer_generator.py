from __future__ import annotations

import logging
import json
from pathlib import Path

from answer_engine.config import AnswerEngineConfig
from answer_engine.models import GeneratedPrompt
from answer_engine.llm_provider import BaseLLMProvider
from answer_engine.mock_provider import MockProvider
from answer_engine.openai_provider import OpenAIProvider
from answer_engine.gemini_provider import GeminiProvider
from answer_engine.response_parser import parse_llm_response, JSONParsingError
from answer_engine.response_validator import validate_answer_schema, ValidationFailedError

logger = logging.getLogger(__name__)

class AnswerGenerator:
    def __init__(self, config: AnswerEngineConfig):
        self.config = config
        self.provider = self._init_provider()
        
    def _init_provider(self) -> BaseLLMProvider:
        name = self.config.llm_provider.lower()
        if name == "mock":
            return MockProvider(self.config.llm_model, self.config.llm_temperature, self.config.llm_max_tokens)
        elif name == "openai":
            return OpenAIProvider(self.config.llm_model, self.config.llm_temperature, self.config.llm_max_tokens)
        elif name == "gemini":
            return GeminiProvider(self.config.llm_model, self.config.llm_temperature, self.config.llm_max_tokens)
        else:
            logger.warning(f"Unknown LLM provider: {name}. Falling back to Mock.")
            return MockProvider("mock", 0.0, 1000)
            
    def generate_answer(self, prompt: GeneratedPrompt) -> dict:
        """Executes the LLM request, parses the response, and generates execution reports."""
        
        logger.info(f"Calling LLM Provider: {self.config.llm_provider.upper()} ({self.provider.model_name})")
        
        try:
            # 1. Execute LLM
            llm_res = self.provider.generate(prompt.system_prompt, prompt.user_prompt)
            logger.info(f"LLM returned response in {llm_res.latency_s:.2f}s")
            
            # 2. Parse JSON
            parsed_json = parse_llm_response(llm_res)
            
            # 3. Validate Schema
            validate_answer_schema(parsed_json)
            logger.info("JSON Schema Validation PASSED.")
            
            # 4. Report metrics
            report = {
                "provider": llm_res.provider_name,
                "model": self.provider.model_name,
                "latency_s": round(llm_res.latency_s, 4),
                "tokens": {
                    "prompt": llm_res.prompt_tokens,
                    "completion": llm_res.completion_tokens,
                    "total": llm_res.prompt_tokens + llm_res.completion_tokens
                },
                "cost_estimate_usd": round(llm_res.cost_estimate, 6),
                "parsing_status": "SUCCESS",
                "answer_payload": parsed_json
            }
            
            self._save_report(report)
            return parsed_json
            
        except Exception as e:
            logger.error(f"Answer Generation Failed: {e}")
            error_report = {
                "provider": self.config.llm_provider,
                "parsing_status": "FAILED",
                "error": str(e)
            }
            self._save_report(error_report)
            raise
            
    def _save_report(self, report_data: dict) -> None:
        self.config.report_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.config.report_dir / "llm_generation_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)
        logger.info(f"Answer generation report written to {report_path}")
