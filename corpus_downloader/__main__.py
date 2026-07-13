"""Entry point for running the corpus downloader as a module.

Usage:
    python -m corpus_downloader                 # Full run (all 100 documents)
    python -m corpus_downloader --test-mode     # Test run (5 documents, 1 per category)

All other configuration is loaded from environment variables or .env file.
See .env.example for the full list of configurable values.
"""

import argparse
import sys

from corpus_downloader.config import DownloaderConfig
from corpus_downloader.main import run_pipeline


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        The parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        prog="corpus_downloader",
        description=(
            "Download, validate, and catalogue U.S. tax and legal "
            "documents from the dataset manifest."
        ),
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        default=False,
        help="Run in test mode: download only one document per category.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the corpus downloader CLI."""
    args = _parse_args()

    config = DownloaderConfig()

    # CLI flag overrides env/config
    if args.test_mode:
        config.test_mode = True

    try:
        run_pipeline(config)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
