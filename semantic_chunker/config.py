from __future__ import annotations

"""Configuration for the Semantic Chunker Pipeline."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class ChunkerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHUNKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    input_dir: Path = Path("data/normalized")
    output_dir: Path = Path("data/chunks")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    max_workers: int = 4
    test_mode: bool = False
    test_sample_size: int = 5
