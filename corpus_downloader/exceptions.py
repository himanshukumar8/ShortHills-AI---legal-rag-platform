from __future__ import annotations

"""Custom exception hierarchy for the Corpus Download Pipeline.

All exceptions inherit from CorpusDownloaderError, enabling both
granular catch blocks for specific failure modes and broad catch
blocks at the orchestrator level.

Design:
    CorpusDownloaderError
    ├── ConfigurationError
    ├── ManifestError
    ├── DownloadError
    ├── ValidationError
    └── DuplicateFileError
"""


class CorpusDownloaderError(Exception):
    """Base exception for all corpus downloader errors.

    Attributes:
        document_id: The ID of the document that triggered the error,
            or None if the error is not document-specific.
    """

    def __init__(
        self, message: str, document_id: str | None = None
    ) -> None:
        self.document_id = document_id
        super().__init__(message)


class ConfigurationError(CorpusDownloaderError):
    """Raised when pipeline configuration is invalid or missing."""


class ManifestError(CorpusDownloaderError):
    """Raised when the manifest file is malformed, missing, or unreadable."""


class DownloadError(CorpusDownloaderError):
    """Raised when an HTTP download fails.

    Attributes:
        url: The URL that was being downloaded.
        status_code: The HTTP status code, if available.
    """

    def __init__(
        self,
        message: str,
        document_id: str | None = None,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.url = url
        self.status_code = status_code
        super().__init__(message, document_id)


class ValidationError(CorpusDownloaderError):
    """Raised when a downloaded PDF fails integrity or quality checks.

    Attributes:
        file_path: The local path to the file that failed validation.
    """

    def __init__(
        self,
        message: str,
        document_id: str | None = None,
        file_path: str | None = None,
    ) -> None:
        self.file_path = file_path
        super().__init__(message, document_id)


class DuplicateFileError(CorpusDownloaderError):
    """Raised when a downloaded file duplicates an already-registered file.

    Attributes:
        duplicate_of: The document_id of the original file.
    """

    def __init__(
        self,
        message: str,
        document_id: str | None = None,
        duplicate_of: str | None = None,
    ) -> None:
        self.duplicate_of = duplicate_of
        super().__init__(message, document_id)
