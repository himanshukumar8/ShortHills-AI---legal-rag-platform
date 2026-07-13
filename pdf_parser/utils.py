from __future__ import annotations

"""Utility functions for the PDF Parser Pipeline."""

import os
import re
from pathlib import Path


def ensure_directory(path: Path | str) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to ensure.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    """Clean and normalize extracted text.

    Removes excessive whitespace, null bytes, and non-printable characters
    while preserving newlines and basic formatting.

    Args:
        text: The raw extracted text.

    Returns:
        The cleaned text string.
    """
    if not text:
        return ""
        
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Normalize multiple newlines to double newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Normalize trailing spaces on lines
    text = re.sub(r"[ \t]+\n", "\n", text)
    
    return text.strip()


def count_words(text: str) -> int:
    """Count the number of words in a text string.

    Args:
        text: The text to count words in.

    Returns:
        The word count.
    """
    if not text:
        return 0
    # A simple split by whitespace is generally sufficient for word counting
    return len(text.split())
