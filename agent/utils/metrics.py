from __future__ import annotations
import csv, json, os, pathlib, statistics as stats
from typing import Dict, Any, List

OBS_JSONL = pathlib.Path(os.getenv("OBS_JSONL", "logs/agent.jsonl"))
METRICS_CSV = pathlib.Path(os.getenv("OBS_METRICS_CSV", "reports/metrics_summary.csv"))

DEFAULT_BUDGETS = {
    "max_cost_usd": float(os.getenv("MAX_RUN_COST_USD", "0.50")),
    "p95_latency_ms": int(os.getenv("P95_LATENCY_BUDGET_MS", "3500")),
}

class Metrics:
    def __init__(self, events: List[Dict[str, Any]]):
        self.events = events

    def _durations(self, kind_prefix: str) -> List[int]:
        return [e["duration_ms"] for e in self.events if e.get("kind") == kind_prefix and e.get("duration_ms") is not None]

    def totals(self) -> Dict[str, Any]:
        cost = sum(e.get("cost_usd", 0) or 0 for e in self.events)
        itoks = sum(e.get("input_tokens", 0) or 0 for e in self.events)
        otoks = sum(e.get("output_tokens", 0) or 0 for e in self.events)
        model_lat = self._durations("model_call")
        tool_lat = self._durations("tool_call")
        return {
            "cost_usd": round(cost, 6),
            "input_tokens": itoks,
            "output_tokens": otoks,
            "model_p50_ms": int(stats.median(model_lat)) if model_lat else 0,
            "model_p95_ms": int(stats.quantiles(model_lat, n=20)[18]) if len(model_lat) >= 20 else (max(model_lat) if model_lat else 0),
            "tool_p50_ms": int(stats.median(tool_lat)) if tool_lat else 0,
            "tool_p95_ms": int(stats.quantiles(tool_lat, n=20)[18]) if len(tool_lat) >= 20 else (max(tool_lat) if tool_lat else 0),
        }

    def write_csv(self, path: pathlib.Path = METRICS_CSV) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        t = self.totals()
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["metric", "value"])
            for k, v in t.items():
                w.writerow([k, v])

    def check_budgets(self, budgets: Dict[str, Any] = DEFAULT_BUDGETS) -> Dict[str, bool]:
        t = self.totals()
        return {
            "cost_ok": t["cost_usd"] <= budgets["max_cost_usd"],
            "latency_ok": t["model_p95_ms"] <= budgets["p95_latency_ms"],
        }

def load_events() -> List[Dict[str, Any]]:
    events = []
    if not OBS_JSONL.exists():
        return events
    with OBS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            try: events.append(json.loads(line))
            except Exception: continue
    return events
