"""Appendix A.5 graph service."""

import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from graphrag_poc.library.api import CORPUS_BUILD, build_graph, graph_stats, link_entities, traverse
from graphrag_poc.library.models import Entity, Seed, TraversalResult

app = FastAPI(title="Graph library")
app.state.build = os.environ.get("GRAPH_BUILD", CORPUS_BUILD)


class BuildBody(BaseModel):
    node_files: list[str] = Field(min_length=1)
    case_file: str | None = None
    rules: str
    build: str
    out: str | None = None


class LinkBody(BaseModel):
    entities: list[Entity]
    build: str = ""


class TraverseBody(BaseModel):
    seeds: list[Seed]
    question_type: str
    hops: int = 2
    cap: int = 200
    build: str = ""
    question: str = ""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "build": str(app.state.build)}


@app.get("/graph/stats")
def stats(build: str = "") -> dict[str, object]:
    selected = build or str(app.state.build)
    return graph_stats(selected)


@app.post("/graph/build")
def build(body: BuildBody) -> dict[str, object]:
    destination = body.out or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    report = build_graph(
        [Path(path) for path in body.node_files],
        Path(body.case_file) if body.case_file else None,
        Path(body.rules),
        destination,
        body.build,
    )
    app.state.build = body.build
    return report.model_dump()


@app.post("/graph/link")
def link(body: LinkBody) -> dict[str, object]:
    selected = body.build or str(app.state.build)
    seeds = link_entities(body.entities, selected)
    return {"seeds": [seed.model_dump() for seed in seeds]}


@app.post("/graph/traverse", response_model=TraversalResult)
def walk(body: TraverseBody) -> TraversalResult:
    selected = body.build or str(app.state.build)
    return traverse(
        body.seeds,
        body.question_type,
        body.hops,
        body.cap,
        selected,
        question=body.question,
    )
