from agent.core import respond

def test_respond_smoke(monkeypatch):
    # Monkeypatch model.chat to avoid external calls
    from agent import model
    def fake_chat(prompt: str):
        if '"tool"' in prompt:
            return {"text": '{"tool":"write_file","args":{"path":"out.txt","content":"hi"}}'}
        return {"text": "ok"}
    monkeypatch.setattr(model, "chat", fake_chat)

    out = respond("Save 'hi' to out.txt using a tool.")
    assert "text" in out and isinstance(out["text"], str)
