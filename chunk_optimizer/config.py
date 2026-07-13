from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class OptimizerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPTIMIZER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    input_dir: Path = Path("data/chunks")
    output_dir: Path = Path("data/optimized_chunks")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    max_workers: int = 4
    
    # Thresholds
    min_tokens: int = 50
    max_tokens: int = 1500
