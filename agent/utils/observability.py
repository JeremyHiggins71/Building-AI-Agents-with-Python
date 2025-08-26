from __future__ import annotations
import json, time, uuid, pathlib, os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

LOG_PATH = pathlib.Path(os.getenv("OBS_JSONL", "logs/agent.jsonl"))
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

@dataclass
class Trace:
    run_id: str
    step_id: int
    parent_id: Optional[int] = None

@dataclass
class Event:
    ts_ms: int
    kind: str  # model_call | model_result | tool_call | tool_result | error | info
    trace: Trace
    name: str
    status: str  # ok | error
    duration_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    meta: Dict[str, Any] = None

def _now_ms() -> int:
    return int(time.time() * 1000)

def write_event(ev: Event) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        data = asdict(ev)
        data["trace"] = asdict(ev.trace)
        json.dump(data, f, ensure_ascii=False)
        f.write("\n")

class RunContext:
    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or str(uuid.uuid4())
        self._step = 0

    def next_trace(self, parent_id: Optional[int] = None) -> Trace:
        self._step += 1
        return Trace(run_id=self.run_id, step_id=self._step, parent_id=parent_id)

class timed_event:
    def __init__(self, kind: str, name: str, trace: Trace, meta: Optional[Dict[str, Any]] = None):
        self.kind, self.name, self.trace = kind, name, trace
        self.meta = meta or {}
        self._t0 = 0

    def __enter__(self):
        self._t0 = _now_ms()
        return self

    def __exit__(self, exc_type, exc, tb):
        dur = _now_ms() - self._t0
        status = "ok" if exc is None else "error"
        write_event(Event(
            ts_ms=_now_ms(), kind=self.kind, trace=self.trace, name=self.name,
            status=status, duration_ms=dur, meta=self.meta
        ))
        return False

def annotate_last_result(trace: Trace, kind: str, name: str, *,
                         input_tokens: int | None = None,
                         output_tokens: int | None = None,
                         cost_usd: float | None = None,
                         meta: Optional[Dict[str, Any]] = None) -> None:
    write_event(Event(
        ts_ms=_now_ms(), kind=f"{kind}_result", trace=trace, name=name,
        status="ok", input_tokens=input_tokens, output_tokens=output_tokens,
        cost_usd=cost_usd, meta=meta or {},
    ))
