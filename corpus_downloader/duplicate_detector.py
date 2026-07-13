from __future__ import annotations

"""Duplicate file detection for the Corpus Download Pipeline.

Maintains a thread-safe, in-memory registry of SHA-256 checksums
to detect when two different manifest entries resolve to the same
underlying PDF file. This can happen when a source URL redirects
to a shared document or when two different editions of a document
share identical content.
"""

import logging
import threading

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Thread-safe duplicate file detector using SHA-256 checksums.

    Maintains a mapping of ``checksum → document_id`` for the first
    document registered with each unique checksum. Subsequent documents
    that produce the same checksum are flagged as duplicates.

    Thread Safety:
        All registry mutations are guarded by a threading.Lock,
        making this class safe for use with ThreadPoolExecutor.
    """

    def __init__(self) -> None:
        """Initialize an empty checksum registry."""
        self._registry: dict[str, str] = {}
        self._lock = threading.Lock()

    def check(self, checksum: str, document_id: str) -> str | None:
        """Register a checksum or detect a duplicate.

        If the checksum is new, it is registered under the given
        document_id and None is returned. If the checksum is already
        registered to a different document_id, the original document_id
        is returned (indicating a duplicate).

        Args:
            checksum: The SHA-256 hex digest of the file.
            document_id: The document_id attempting to register.

        Returns:
            None if this is the first occurrence of the checksum,
            or the document_id of the previously registered file.
        """
        with self._lock:
            existing_id = self._registry.get(checksum)

            if existing_id is not None and existing_id != document_id:
                logger.warning(
                    "[%s] Duplicate detected: identical checksum as [%s]",
                    document_id,
                    existing_id,
                )
                return existing_id

            self._registry[checksum] = document_id
            return None

    @property
    def registry(self) -> dict[str, str]:
        """Return a snapshot of the current checksum → document_id mapping.

        Returns:
            A copy of the internal registry dictionary.
        """
        with self._lock:
            return dict(self._registry)
