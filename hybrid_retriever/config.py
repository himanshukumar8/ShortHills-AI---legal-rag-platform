from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class HybridConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HYBRID_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    report_dir: Path = Path("reports")
    log_dir: Path = Path("logs")

    # RRF Parameters
    rrf_k: int = 60
    top_k: int = 10
    
    es_index_name: str = "legal_corpus"
    qdrant_collection_name: str = "legal_chunks"
    
    # Flags for mock environment testing
    use_mock: bool = True
