from __future__ import annotations
import json, argparse, pathlib
from typing import Dict, Any, List
from agent.core import respond

def load_events(path: pathlib.Path) -> List[Dict[str, Any]]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

def first_input_for_run(events: List[Dict[str, Any]], run_id: str) -> str | None:
    for e in events:
        if e.get("trace", {}).get("run_id") == run_id and e.get("kind") == "info" and e.get("name") == "user_input":
            return e.get("meta", {}).get("text")
    return None

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--log", default="logs/agent.jsonl")
    args = ap.parse_args()
    events = load_events(pathlib.Path(args.log))
    text = first_input_for_run(events, args.run_id)
    if not text:
        raise SystemExit("No user_input event found for that run_id. Ensure you log it in core.py.")
    out = respond(text)
    print(out.get("text"))
