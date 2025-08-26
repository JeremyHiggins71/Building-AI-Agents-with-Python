# Hands-On Agents — Code Bundle (Ch.1–6)

This repository accompanies the book *Hands-On Agents* (Python track). It includes:

- Minimal agent core with tool registry and circuit breaker (Ch.1–4)
- Structured logging, metrics, evaluation harness, and replay (Ch.5)
- Packaging and Makefile targets for local runs and CI (Ch.6)

## Quickstart

```bash
# 1) Python 3.12 recommended
python -V

# 2) Create venv and install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # or: pip install -e .

# 3) Copy env template and fill values
cp .env.example .env

# 4) Sanity test
make test

# 5) Run a prompt
make run PROMPT="Summarize the benefits of structured logging for AI agents."

# 6) Evaluate on golden tasks
make eval

# 7) Inspect logs/ and reports/
ls -lah logs/ reports/
```

> Note: The code supports both the legacy Chat Completions API and the newer Responses API.
Set `USE_RESPONSES=true` in `.env` to opt into Responses when available.
