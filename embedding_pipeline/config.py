from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class EmbeddingConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    input_dir: Path = Path("data/optimized_chunks")
    output_dir: Path = Path("data/embeddings")
    log_dir: Path = Path("logs")
    report_dir: Path = Path("reports")

    # Embedding settings
    provider: str = "mock" # "openai", "sentence_transformers", "mock"
    model_name: str = "BAAI/bge-large-en-v1.5"
    embedding_dimension: int = 1024
    
    # Batching and Concurrency
    batch_size: int = 100
    max_retries: int = 3
    parallel_workers: int = 4
    
    test_mode: bool = False
    test_sample_size: int = 5
