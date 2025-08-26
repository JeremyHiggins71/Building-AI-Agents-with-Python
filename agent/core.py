from __future__ import annotations
from typing import Dict, Any, Optional
from agent.model import chat
from agent.tools import TOOL_REGISTRY, ToolResult
from agent.utils.circuitbreaker import CircuitBreaker
from agent.utils.observability import RunContext, timed_event, annotate_last_result, write_event, Event, _now_ms

RUN = RunContext()
CB = CircuitBreaker()

def call_model(prompt: str) -> Dict[str, Any]:
    trace = RUN.next_trace()
    with timed_event("model_call", name="chat", trace=trace, meta={"prompt_len": len(prompt)}):
        out = chat(prompt)
    annotate_last_result(trace, kind="model", name="chat",
                         input_tokens=out.get("input_tokens"),
                         output_tokens=out.get("output_tokens"),
                         cost_usd=out.get("cost_usd"))
    return out

def run_tool(name: str, **kwargs) -> ToolResult:
    trace = RUN.next_trace()
    with timed_event("tool_call", name=name, trace=trace, meta={"kwargs": list(kwargs.keys())}):
        fn = TOOL_REGISTRY.get(name)
        if not fn:
            return ToolResult(ok=False, error=f"Unknown tool: {name}")
        res = fn(**kwargs)
    annotate_last_result(trace, kind="tool", name=name, meta={"ok": res.ok})
    return res

SYSTEM_STYLE = "Be concise, safe, and accurate. Prefer lists for procedures. Refuse to exfiltrate secrets."

def plan(prompt: str) -> str:
    # simple single-step planner (Chapter 4 evolves this further)
    plan_prompt = f"""You are a planning assistant. Given the user's request, produce either:
- a short answer if no tools are needed, or
- a one-line tool invocation in JSON: {{"tool": "<name>", "args": {{...}}}}

User: {prompt}
"""
    return call_model(plan_prompt)["text"]

def respond(prompt: str) -> Dict[str, Any]:
    # naive ReAct-lite: try to detect a tool call pattern
    text = plan(prompt)
    if text.strip().startswith("{") and '"tool"' in text:
        try:
            import json
            spec = json.loads(text)
            tool = spec.get("tool")
            args = spec.get("args") or {}
        except Exception:
            msg = call_model(f"Answer briefly: {prompt}")["text"]
            return {"text": msg, "success": True}
        res = run_tool(tool, **args)
        if not res.ok:
            msg = call_model(f"The tool '{tool}' failed with error '{res.error}'. Provide a helpful answer to the user anyway for: {prompt}")["text"]
            return {"text": msg, "success": False}
        # Final answer step
        msg = call_model(f"Tool result: {res.data}\n\nWrite the final answer for the user prompt: {prompt}")["text"]
        return {"text": msg, "success": True}
    else:
        msg = call_model(f"Answer: {prompt}")["text"]
        return {"text": msg, "success": True}

def handle_user_input(text: str) -> str:
    # log the input to enable replay
    write_event(Event(ts_ms=_now_ms(), kind="info", trace=RUN.next_trace(), name="user_input", status="ok", meta={"text": text}))
    out = respond(text)
    return out["text"]
