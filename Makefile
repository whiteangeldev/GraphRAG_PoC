# python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"
PYTHON ?= .venv/bin/python

.PHONY: up down test lint format typecheck ingest generate-cases index demo eval graph m3 service gold-check model-check baseline

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
	$(PYTHON) -m mypy src/graphrag_poc/models src/graphrag_poc/ingest src/graphrag_poc/cases src/graphrag_poc/index src/graphrag_poc/retrieve src/graphrag_poc/generate src/graphrag_poc/graph src/graphrag_poc/library src/graphrag_poc/service src/graphrag_poc/app src/graphrag_poc/eval

ingest:
	$(PYTHON) -m graphrag_poc.ingest

generate-cases:
	$(PYTHON) -m graphrag_poc.cases

index:
	$(PYTHON) -m graphrag_poc.index

demo:
	EMBEDDING_BACKEND=$${EMBEDDING_BACKEND:-fastembed} \
	EMBEDDING_MODEL=$${EMBEDDING_MODEL:-sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2} \
	$(PYTHON) -m graphrag_poc.app

service:
	docker compose up -d --build --wait graph

graph: up
	$(PYTHON) -m graphrag_poc.graph

m3:
	$(PYTHON) -m graphrag_poc.eval.gold --acceptance
	$(PYTHON) -m graphrag_poc.eval.config
	$(MAKE) up
	$(PYTHON) -m graphrag_poc.eval.m3

gold-check:
	$(PYTHON) -m graphrag_poc.eval.gold

model-check:
	$(PYTHON) -m graphrag_poc.eval.config

baseline:
	$(PYTHON) -m graphrag_poc.eval.gold --acceptance
	$(PYTHON) -m graphrag_poc.eval.config
	$(MAKE) up
	$(PYTHON) -m graphrag_poc.eval --score

eval:
	$(PYTHON) -m graphrag_poc.eval.gold --acceptance
	$(PYTHON) -m graphrag_poc.eval.config
	$(MAKE) up
	$(PYTHON) -m graphrag_poc.eval --reproduce
	$(PYTHON) -m graphrag_poc.eval.m3 --reproduce
