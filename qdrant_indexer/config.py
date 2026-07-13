from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class QdrantConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="QDRANT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    chunks_dir: Path = Path("data/optimized_chunks")
    embeddings_dir: Path = Path("data/embeddings")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    collection_name: str = "legal_chunks"
    vector_dimension: int = 1024 # Standard for our BAAI model
    batch_size: int = 100
    use_mock: bool = True
