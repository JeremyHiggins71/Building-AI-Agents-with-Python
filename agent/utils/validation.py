from __future__ import annotations
import os, pathlib
from typing import Iterable

BASE = pathlib.Path(os.getenv("WORKSPACE_DIR", "workspace")).resolve()
ALLOWED_EXTS = set((os.getenv("ALLOWED_EXTS", ".txt,.md,.json,.csv")).split(","))

def ensure_workspace():
    BASE.mkdir(parents=True, exist_ok=True)

def safe_join(relpath: str) -> pathlib.Path:
    ensure_workspace()
    p = (BASE / relpath).resolve()
    if not str(p).startswith(str(BASE)):
        raise ValueError("Path traversal detected")
    if p.suffix and p.suffix not in ALLOWED_EXTS:
        raise ValueError(f"Extension {p.suffix} not in allowed set: {ALLOWED_EXTS}")
    return p
