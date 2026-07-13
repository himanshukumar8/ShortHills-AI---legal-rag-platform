from __future__ import annotations

"""Text manipulation and cleaning logic."""

import re

def fix_hyphenation(text: str) -> str:
    """Fix broken hyphenation across line breaks.
    
    Example: 'constitu-\ntion' -> 'constitution'
    Only targets lowercase letters to avoid accidentally mangling lists or tables.
    """
    # Match a lowercase word part, a hyphen, optional spaces, newline, optional spaces, and rest of the word.
    pattern = re.compile(r"([a-z]+)-\s*\n\s*([a-z]+)")
    return pattern.sub(r"\1\2", text)


def normalize_whitespace(text: str) -> str:
    """Normalize tabs, carriage returns, and excessive newlines."""
    if not text:
        return ""
        
    # Remove carriage returns
    text = text.replace("\r", "")
    
    # Replace weird unicode spaces with standard space
    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "") # zero width space
    
    # Normalize horizontal whitespace (tabs or multiple spaces) to a single space
    # but ONLY if they are not at the start of a line (to preserve indentation).
    # Wait, the prompt says "Preserve lists, tables". Aggressive space removal breaks tables.
    # We will ONLY remove trailing whitespace on lines and reduce >2 newlines.
    
    # Remove trailing whitespace on each line
    text = re.sub(r"[ \t]+\n", "\n", text)
    
    # Reduce 3 or more newlines to exactly 2 (paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()


def remove_page_numbers(text: str) -> str:
    """Remove standalone page numbers at the very top or bottom of a page.
    
    Also attempts to catch simple headers like 'Page 5' or '5 | Page'.
    """
    lines = text.split("\n")
    if not lines:
        return text
        
    # Check first line
    first = lines[0].strip()
    if re.fullmatch(r"(?:Page\s*)?\d+(?:\s*of\s*\d+)?|\d+\s*\|\s*Page", first, re.IGNORECASE):
        lines.pop(0)
        
    if not lines:
        return ""
        
    # Check last line
    last = lines[-1].strip()
    if re.fullmatch(r"(?:Page\s*)?\d+(?:\s*of\s*\d+)?|\d+\s*\|\s*Page", last, re.IGNORECASE):
        lines.pop(-1)
        
    return "\n".join(lines)


def clean_page_text(text: str) -> str:
    """Apply all cleaning rules to a single page's text."""
    if not text.strip():
        return ""
        
    text = remove_page_numbers(text)
    text = fix_hyphenation(text)
    text = normalize_whitespace(text)
    
    return text
