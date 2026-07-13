from __future__ import annotations

"""Configuration management for the Document Normalization Pipeline."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class NormalizerConfig(BaseSettings):
    """Configuration for the Normalizer Pipeline."""

    model_config = SettingsConfigDict(
        env_prefix="NORMALIZER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Paths ---
    input_dir: Path = Path("data/processed")
    output_dir: Path = Path("data/normalized")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    # --- Concurrency ---
    max_workers: int = 4

    # --- Test Mode ---
    test_mode: bool = False
    test_sample_size: int = 5
