from __future__ import annotations

import re

def extract_cross_references(text: str) -> list[str]:
    """Extract U.S.C. and CFR citations from text."""
    refs = set()
    
    # 26 U.S.C. 123 or 26 U.S.C. § 123
    usc_pattern = re.findall(r"(\d+\s+U\.S\.C\.\s+(?:§\s*)?\d+[a-zA-Z0-9\-\(\)]*)", text)
    refs.update(usc_pattern)
    
    # 26 CFR 1.162-1
    cfr_pattern = re.findall(r"(\d+\s+CFR\s+(?:§\s*)?\d+\.\d+[a-zA-Z0-9\-\(\)]*)", text)
    refs.update(cfr_pattern)
    
    return sorted(list(refs))
