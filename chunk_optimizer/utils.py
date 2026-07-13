from __future__ import annotations

import hashlib
import re
from pathlib import Path

def ensure_directory(path: Path | str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
