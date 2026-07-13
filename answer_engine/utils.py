from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

def estimate_tokens(text: str) -> int:
    """
    Very rough estimation of tokens without loading heavy tokenizers (e.g. tiktoken).
    In a real environment, we would use `tiktoken.get_encoding("cl100k_base")`.
    We assume ~4 characters per token as a standard rule of thumb.
    """
    return len(text) // 4
