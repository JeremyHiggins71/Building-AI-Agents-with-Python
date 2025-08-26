from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Callable
import requests
from agent.utils.validation import safe_join

@dataclass
class ToolResult:
    ok: bool
    data: Any = None
    error: str | None = None

TOOL_REGISTRY: Dict[str, Callable[..., ToolResult]] = {}

def tool(name: str):
    def deco(fn: Callable[..., ToolResult]):
        TOOL_REGISTRY[name] = fn
        return fn
    return deco

@tool("write_file")
def write_file(path: str, content: str) -> ToolResult:
    try:
        p = safe_join(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return ToolResult(ok=True, data={"path": str(p)})
    except Exception as e:
        return ToolResult(ok=False, error=str(e))

@tool("http_get_json")
def http_get_json(url: str) -> ToolResult:
    # A conservative fetcher: only allow http(s) and 200 OK; no redirects to non-http
    if not (url.startswith("http://") or url.startswith("https://")):
        return ToolResult(ok=False, error="Only http(s) URLs allowed")
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        # try json first; fallback to text
        try:
            return ToolResult(ok=True, data=r.json())
        except Exception:
            return ToolResult(ok=True, data={"text": r.text[:5000]})
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
