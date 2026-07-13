"""HTTP download module for the Corpus Download Pipeline.

Handles downloading individual PDF documents with streaming writes,
configurable timeouts, User-Agent headers, and resume support via
HTTP Range requests.

Retry logic is intentionally NOT built into this module. The orchestrator
(main.py) manages retries so that each attempt can be individually
logged, counted, and controlled with exponential backoff.
"""

import logging
import time
from pathlib import Path

import requests

from corpus_downloader.config import DownloaderConfig
from corpus_downloader.exceptions import DownloadError

logger = logging.getLogger(__name__)

# HTTP status codes treated as successful for download responses.
_SUCCESS_CODES: frozenset[int] = frozenset({200, 206})


def create_session(config: DownloaderConfig) -> requests.Session:
    """Create a configured requests.Session for downloading documents.

    Sets the User-Agent header, SSL verification mode, and accept header.
    Does NOT configure automatic retries — retry logic is managed by
    the orchestrator for full visibility.

    Args:
        config: The downloader configuration.

    Returns:
        A configured requests.Session instance.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": config.user_agent,
        "Accept": "application/pdf, application/octet-stream, */*",
    })
    session.verify = config.verify_ssl
    return session


def download_document(
    session: requests.Session,
    url: str,
    destination: Path,
    document_id: str,
    config: DownloaderConfig,
) -> Path:
    """Download a single document from a URL to a local file path.

    Supports resuming partial downloads when the server supports
    HTTP Range requests (returns 206). If the server does not support
    Range, the file is re-downloaded from the beginning.

    A configurable delay is applied before each request to respect
    rate limits on government servers (IRS.gov, GovInfo, etc.).

    Args:
        session: The requests session to use for the HTTP call.
        url: The PDF URL to download.
        destination: The local file path to write the downloaded bytes to.
        document_id: The document identifier (for logging and error context).
        config: The downloader configuration.

    Returns:
        The Path to the successfully downloaded file.

    Raises:
        DownloadError: If the HTTP request fails or the response
            indicates an error status code.
    """
    # Rate-limiting delay before making the request
    time.sleep(config.request_delay_seconds)

    # Check for an existing partial file to attempt resume
    existing_size = destination.stat().st_size if destination.exists() else 0
    headers: dict[str, str] = {}

    if existing_size > 0:
        headers["Range"] = f"bytes={existing_size}-"
        logger.info(
            "[%s] Attempting resume from byte %d", document_id, existing_size
        )

    try:
        response = session.get(
            url,
            headers=headers,
            stream=True,
            timeout=config.timeout_seconds,
        )
    except requests.ConnectionError as exc:
        raise DownloadError(
            f"Connection error for {document_id}: {exc}",
            document_id=document_id,
            url=url,
        ) from exc
    except requests.Timeout as exc:
        raise DownloadError(
            f"Timeout after {config.timeout_seconds}s for {document_id}",
            document_id=document_id,
            url=url,
        ) from exc
    except requests.RequestException as exc:
        raise DownloadError(
            f"Network error downloading {document_id}: {exc}",
            document_id=document_id,
            url=url,
        ) from exc

    if response.status_code not in _SUCCESS_CODES:
        raise DownloadError(
            f"HTTP {response.status_code} for {document_id} from {url}",
            document_id=document_id,
            url=url,
            status_code=response.status_code,
        )

    # Determine write mode: append if resuming (206), overwrite otherwise
    is_resuming = response.status_code == 206 and existing_size > 0
    write_mode = "ab" if is_resuming else "wb"

    if not is_resuming and existing_size > 0:
        logger.debug(
            "[%s] Server returned 200 (no Range support); downloading fully",
            document_id,
        )

    try:
        with open(destination, write_mode) as f:
            for chunk in response.iter_content(
                chunk_size=config.stream_chunk_size
            ):
                if chunk:
                    f.write(chunk)
    except OSError as exc:
        raise DownloadError(
            f"Failed to write file for {document_id}: {exc}",
            document_id=document_id,
            url=url,
        ) from exc
    finally:
        response.close()

    final_size = destination.stat().st_size
    logger.info(
        "[%s] Download complete: %s (%s bytes)",
        document_id,
        destination.name,
        f"{final_size:,}",
    )
    return destination
