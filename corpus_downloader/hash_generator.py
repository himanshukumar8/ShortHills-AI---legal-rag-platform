"""SHA-256 checksum generation for downloaded PDF files.

Uses streaming reads to handle arbitrarily large files (e.g., the
Internal Revenue Code at 4000+ pages) without loading the entire
file into memory.
"""

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE: int = 65536  # 64 KB


def compute_sha256(
    file_path: Path,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
) -> str:
    """Compute the SHA-256 hash of a file using streaming reads.

    Args:
        file_path: Path to the file to hash.
        chunk_size: Number of bytes to read per iteration. Defaults
            to 64 KB, which balances memory usage and I/O throughput.

    Returns:
        The lowercase hexadecimal SHA-256 digest string (64 characters).

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file cannot be read.
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)

    digest = sha256.hexdigest()
    logger.debug("SHA-256 for %s: %s", file_path.name, digest)
    return digest
