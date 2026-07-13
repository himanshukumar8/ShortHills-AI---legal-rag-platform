from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class AnswerEngineConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ANSWER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    report_dir: Path = Path("reports")
    log_dir: Path = Path("logs")

    # Prompt configuration
    max_context_tokens: int = 4000
    max_total_tokens: int = 8000
    
    # Validation settings
    strict_validation: bool = True
    
    # LLM settings
    llm_provider: str = "mock" # "mock", "openai", "gemini"
    llm_model: str = "gpt-4-turbo"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1500
