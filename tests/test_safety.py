from agent.utils.validation import safe_join
import pytest, os, pathlib

def test_safe_join_blocks_escape(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        safe_join("../../etc/passwd")
