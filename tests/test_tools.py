from agent.tools import write_file, http_get_json
import os, json, pathlib

def test_write_file_valid(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path))
    res = write_file("notes/test.md", "hello")
    assert res.ok
    p = pathlib.Path(res.data["path"])
    assert p.exists() and p.read_text() == "hello"

def test_write_file_blocks_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path))
    r = write_file("../evil.txt", "x")
    assert not r.ok and "traversal" in (r.error or "").lower()

def test_http_get_json_text():
    # Should return something, but don't assume remote availability in CI
    r = http_get_json("https://example.com")
    assert r.ok
