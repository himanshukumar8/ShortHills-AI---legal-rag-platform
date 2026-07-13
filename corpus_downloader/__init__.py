"""Corpus Download Pipeline for the Legal AI Search System.

Provides a modular, production-grade pipeline for downloading,
validating, and cataloguing U.S. tax and legal PDF documents
from the curated dataset manifest.
"""

from corpus_downloader.config import DownloaderConfig
from corpus_downloader.models import DocumentRecord, DocumentStatus, DownloadResult

__all__ = [
    "DownloaderConfig",
    "DocumentRecord",
    "DocumentStatus",
    "DownloadResult",
]
