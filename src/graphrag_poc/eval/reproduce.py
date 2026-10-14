"""Reproduce the cached baseline: index, node files, Japanese sample, and metrics."""

import json
import os
import sys
from pathlib import Path

from graphrag_poc.eval.metrics import REPRODUCTION_TOLERANCE, metric_drifts
from graphrag_poc.eval.score import METRICS_PATH, REPORT_PATH, RESULTS_PATH, run_baseline
from graphrag_poc.index.store import CASE_COLLECTION, PASSAGE_COLLECTION

JAPANESE_SPAN = "適用範囲"
JAPANESE_DOC = "mlit_b052"
_SNAPSHOTS = (METRICS_PATH, REPORT_PATH, RESULTS_PATH)


def main() -> int:
    from graphrag_poc.eval.score import _load_env_file

    _load_env_file()
    if not os.environ.get("EMBEDDING_MODEL", "").strip():
        print(
            "EMBEDDING_MODEL is empty. The cached report names the model to use.",
            file=sys.stderr,
        )
        return 1
    try:
        ensure_index()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if not japanese_sample_indexed():
        print(
            f"{JAPANESE_SPAN} did not return a passage from {JAPANESE_DOC}",
            file=sys.stderr,
        )
        return 1
    print(f"Japanese sample {JAPANESE_DOC} is in the index", flush=True)
    node_errors = _node_errors()
    if node_errors:
        for error in node_errors[:30]:
            print(error, file=sys.stderr)
        return 1
    print("node validator accepted every saved file", flush=True)

    saved = {
        path: path.read_text(encoding="utf-8") if path.exists() else None for path in _SNAPSHOTS
    }
    previous_text = saved[METRICS_PATH]
    previous = json.loads(previous_text) if previous_text else None
    try:
        report = run_baseline()
    except RuntimeError as exc:
        _restore(saved)
        print(str(exc), file=sys.stderr)
        return 1
    current = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    problems: list[str] = []
    if JAPANESE_DOC not in report:
        problems.append(f"the report does not name the Japanese sample {JAPANESE_DOC}")
    if isinstance(previous, dict):
        problems.extend(metric_drifts(previous, current, tolerance=REPRODUCTION_TOLERANCE))
    else:
        print("no cached metrics were present; this run wrote the first report")
    if problems:
        _restore(saved)
        for problem in problems:
            print(problem, file=sys.stderr)
        print("restored the cached report", file=sys.stderr)
        return 1
    print("reproduction check passed; every metric is within 0.02 of the cached report")
    return 0


def ensure_index() -> None:
    """Build the Qdrant collections when they are missing or the vector size differs."""

    from graphrag_poc.index.client import make_client
    from graphrag_poc.index.embed import build_embedder
    from graphrag_poc.index.store import index_is_ready

    embedder = build_embedder()
    client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    if index_is_ready(client, embedder.dimension):
        print(
            f"index present: {PASSAGE_COLLECTION} and {CASE_COLLECTION}, "
            f"{embedder.model_name} ({embedder.dimension} dimensions)",
            flush=True,
        )
        return
    print("index missing or built for a different vector size; building", flush=True)
    from graphrag_poc.index.__main__ import main as index_main

    if index_main() != 0:
        raise RuntimeError("index build failed")


def japanese_sample_indexed() -> bool:
    """The sparse channel returns 別添52 for the sample span."""

    from graphrag_poc.index.client import make_client
    from graphrag_poc.index.store import search_passages

    client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    hits = search_passages(client, JAPANESE_SPAN, limit=5)
    return bool(hits) and hits[0].doc_key == JAPANESE_DOC and JAPANESE_SPAN in hits[0].text


def _node_errors() -> list[str]:
    from graphrag_poc.ingest.convert import validate_saved

    errors: list[str] = []
    for doc_key, messages in validate_saved().items():
        errors.extend(f"{doc_key}: {message}" for message in messages)
    return errors


def _restore(saved: dict[Path, str | None]) -> None:
    for path, text in saved.items():
        if text is not None:
            path.write_text(text, encoding="utf-8")
