"""Centralized configuration for the Corpus Download Pipeline.

Uses pydantic-settings to load all values from environment variables
or a .env file, ensuring zero hardcoded configuration anywhere in the
pipeline. Every field has a sensible default for local development.

Environment variables are prefixed with DOWNLOADER_ to avoid
collisions with other components of the Legal AI Search System.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class DownloaderConfig(BaseSettings):
    """Configuration for the corpus download pipeline.

    All values can be overridden via environment variables prefixed
    with ``DOWNLOADER_`` or through a ``.env`` file in the project root.

    Example:
        Setting ``DOWNLOADER_MAX_WORKERS=5`` in the environment will
        override the default worker count of 3.
    """

    model_config = SettingsConfigDict(
        env_prefix="DOWNLOADER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Paths ---
    manifest_path: Path = Path("data/manifest/dataset_manifest.csv")
    download_dir: Path = Path("data/raw")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    # --- Network ---
    timeout_seconds: int = 120
    max_retries: int = 3
    request_delay_seconds: float = 2.0
    verify_ssl: bool = True
    user_agent: str = (
        "LegalAISearchSystem/1.0 "
        "(Academic Research; U.S. Tax and Legal Corpus Builder)"
    )

    # --- Concurrency ---
    max_workers: int = 3

    # --- Test Mode ---
    test_mode: bool = False
    test_sample_size: int = 5

    # --- Streaming ---
    stream_chunk_size: int = 65536  # 64 KB
