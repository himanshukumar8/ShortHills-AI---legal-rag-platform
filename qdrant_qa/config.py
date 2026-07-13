from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class QdrantQAConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="QDRANTQA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    chunks_dir: Path = Path("data/optimized_chunks")
    embeddings_dir: Path = Path("data/embeddings")
    report_dir: Path = Path("reports")
    log_dir: Path = Path("logs")

    queries_per_type: int = 25
    query_types: list[str] = ["paraphrased", "concept", "citation", "natural_language"]
    
    collection_name: str = "legal_chunks"
    use_mock: bool = True
