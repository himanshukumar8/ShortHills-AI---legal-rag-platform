from __future__ import annotations

"""Configuration management for the PDF Parser Pipeline.

Loads settings from environment variables or a .env file using
pydantic-settings, ensuring all configuration is centralized and
type-validated.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ParserConfig(BaseSettings):
    """Configuration for the PDF Parser Pipeline."""

    model_config = SettingsConfigDict(
        env_prefix="PARSER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Paths ---
    manifest_path: Path = Path("data/manifest/dataset_manifest.csv")
    input_dir: Path = Path("data/raw")
    output_dir: Path = Path("data/processed")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    # --- Concurrency ---
    max_workers: int = 3

    # --- Test Mode ---
    test_mode: bool = False
    test_sample_size: int = 5
