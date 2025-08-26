.PHONY: setup test run eval metrics fmt

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

test:
	pytest

run:
	python -m agent.cli --prompt "$(PROMPT)"

eval:
	python -m agent.utils.evalharness --dataset datasets/golden/basic.jsonl --report reports/eval_report.json --min_success 0.80

metrics:
	python -c "from agent.utils.metrics import load_events, Metrics; m=Metrics(load_events()); m.write_csv(); print(m.totals())"

fmt:
	python -m black agent tests
