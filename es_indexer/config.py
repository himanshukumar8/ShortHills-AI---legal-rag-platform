from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class ESIndexerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    input_dir: Path = Path("data/optimized_chunks")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    # ES Settings
    es_hosts: list[str] = ["http://localhost:9200"]
    index_name: str = "legal_corpus"
    batch_size: int = 500
    max_retries: int = 3
    
    use_mock: bool = True # Set to True to use in-memory mock when ES is unavailable
