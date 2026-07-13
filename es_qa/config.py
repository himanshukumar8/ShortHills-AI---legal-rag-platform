from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class ESQAConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ESQA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    chunks_dir: Path = Path("data/optimized_chunks")
    report_dir: Path = Path("reports")
    log_dir: Path = Path("logs")

    queries_per_type: int = 20
    query_types: list[str] = ["citation", "keyword", "phrase", "boolean", "metadata"]
    
    # Needs to match ES Indexer Config
    index_name: str = "legal_corpus"
    use_mock: bool = True
