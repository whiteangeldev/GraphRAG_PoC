# python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"
PYTHON ?= .venv/bin/python

.PHONY: up down test lint format typecheck ingest generate-cases index demo eval

up:
	docker compose up -d --wait

down:
	docker compose down

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

typecheck:
	$(PYTHON) -m mypy src/graphrag_poc/models src/graphrag_poc/ingest src/graphrag_poc/cases src/graphrag_poc/index src/graphrag_poc/retrieve src/graphrag_poc/generate

ingest:
	$(PYTHON) -m graphrag_poc.ingest

generate-cases:
	$(PYTHON) -m graphrag_poc.cases

index:
	$(PYTHON) -m graphrag_poc.index

demo eval:
	@echo "target '$@' is reserved for a later step" >&2
	@exit 1
