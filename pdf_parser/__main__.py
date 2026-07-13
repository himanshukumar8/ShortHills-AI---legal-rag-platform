from __future__ import annotations

"""Entry point for running the pdf parser as a module.

Usage:
    python -m pdf_parser                 # Full run
    python -m pdf_parser --test-mode     # Test run (5 documents)
"""

import argparse
import sys

from pdf_parser.config import ParserConfig
from pdf_parser.main import run_pipeline


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pdf_parser",
        description="Parse and extract metadata from downloaded legal PDFs.",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        default=False,
        help="Run in test mode: parse only a small sample of documents.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = _parse_args()
    config = ParserConfig()

    if args.test_mode:
        config.test_mode = True

    try:
        run_pipeline(config)
    except KeyboardInterrupt:
        print("\nParsing interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
