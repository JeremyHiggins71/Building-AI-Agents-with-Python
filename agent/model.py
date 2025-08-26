from __future__ import annotations
import os, json, time
import requests
from typing import Dict, Any

API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
USE_RESPONSES = os.getenv("USE_RESPONSES", "false").lower() == "true"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    "Content-Type": "application/json",
}

def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{API_BASE.rstrip('/')}/{path.lstrip('/')}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

def chat(prompt: str) -> Dict[str, Any]:
    t0 = time.time()
    if USE_RESPONSES:
        # Newer Responses API
        data = _post("responses", {
            "model": MODEL,
            "input": prompt,
        })
        # Try to extract text and usage in a tolerant way
        text = ""
        if "output" in data and isinstance(data["output"], dict):
            text = data["output"].get("text", "")
        elif "content" in data and isinstance(data["content"], list) and data["content"]:
            # generic shape
            text = str(data["content"][0])
        usage = data.get("usage", {})
    else:
        # Legacy Chat Completions API
        data = _post("chat/completions", {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        })
        choice = (data.get("choices") or [{}])[0]
        text = choice.get("message", {}).get("content", "")
        usage = data.get("usage", {})

    dur = int((time.time() - t0) * 1000)
    return {
        "text": text,
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens") or usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "duration_ms": dur,
        "cost_usd": None,  # optional: add a cost map per model if desired
    }
