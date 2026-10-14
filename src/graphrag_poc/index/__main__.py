"""`python -m graphrag_poc.index` loads passages and cases into Qdrant."""

import os
import sys

from qdrant_client import QdrantClient

from graphrag_poc.index.client import make_client
from graphrag_poc.index.embed import build_embedder
from graphrag_poc.index.records import CasePoint, Passage, load_cases, load_passages
from graphrag_poc.index.store import (
    CASE_COLLECTION,
    PASSAGE_COLLECTION,
    find_cases,
    index_corpus,
    search_passages,
)


def main() -> int:
    _load_env_file()
    embedder = build_embedder()
    passages = load_passages()
    cases = load_cases()
    print(
        f"indexing {len(passages)} passages and {len(cases)} cases "
        f"with {embedder.model_name} ({embedder.dimension} dimensions)",
        flush=True,
    )
    client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    index_corpus(client, embedder, passages, cases, batch_size=64)
    problems = verify(client, passages, cases)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print("index check passed")
    return 0


def verify(client: QdrantClient, passages: list[Passage], cases: list[CasePoint]) -> list[str]:
    """The Step 5 exit check against the loaded collections."""

    problems: list[str] = []
    sample = next(case for case in cases if case.error_codes and case.parts)
    code = sample.error_codes[0]
    part = sample.parts[0]
    japanese = "適用範囲"

    code_hits = search_passages(client, code, collection=PASSAGE_COLLECTION, limit=5)
    if not code_hits or code.lower() not in code_hits[0].text.lower():
        problems.append(f"code string did not return its passage: {code}")
    part_hits = search_passages(client, part, collection=PASSAGE_COLLECTION, limit=5)
    if not any(part in hit.text for hit in part_hits[:3]):
        problems.append(f"part number did not return its passage: {part}")
    japanese_hits = search_passages(client, japanese, collection=PASSAGE_COLLECTION, limit=5)
    if not japanese_hits or japanese_hits[0].lang != "ja" or japanese not in japanese_hits[0].text:
        problems.append("Japanese span 適用範囲 did not return the sample passage")
    matched_cases = find_cases(client, error_code=code, part=part, collection=CASE_COLLECTION)
    found = [
        row
        for row in matched_cases
        if code in _strings(row.get("error_codes")) and part in _strings(row.get("parts"))
    ]
    if not found:
        problems.append("case exact match did not return the sample case")

    info = client.get_collection(PASSAGE_COLLECTION)
    vector_names = set(info.config.params.vectors or {})
    sparse_names = set(info.config.params.sparse_vectors or {})
    if "dense" not in vector_names or "sparse" not in sparse_names:
        problems.append("passage collection is missing named dense or sparse vectors")
    if not any(passage.text for passage in passages):
        problems.append("no passages were offered to the index")
    return problems


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _load_env_file() -> None:
    from pathlib import Path

    path = Path(".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if __name__ == "__main__":
    raise SystemExit(main())
