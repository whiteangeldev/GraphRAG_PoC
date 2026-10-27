"""Cost-free model preflight for both baseline and graph evaluation."""

import os
import re
import sys
from pathlib import Path

from graphrag_poc.generate.config import fingerprint, load_env_file, model_settings
from graphrag_poc.graph.config import GRAPH_WEIGHT, HOP_DEPTH, NODE_CAP, REFERENCE_HOP_DEPTH

EVALUATION_PROTOCOL = "model-json-citations-v1-judge-quotes-v3-explicit-manual-graph-v2"
_QWEN_SIZE = re.compile(r"qwen3[:-](\d+(?:\.\d+)?)b(?:\b|_)")


def configure_evaluation() -> None:
    """Apply the same defaults to every CLI process, after reading local overrides."""

    load_env_file()
    defaults = {
        "EMBEDDING_BACKEND": "fastembed",
        "EMBEDDING_MODEL": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "GENERATION_MODEL": "Qwen/Qwen3-8B",
        "JUDGE_MODEL": "Qwen/Qwen3-14B",
        "GENERATION_CACHE_DIR": str(Path(__file__).resolve().parents[3] / "data/eval/answers"),
    }
    for name, value in defaults.items():
        os.environ.setdefault(name, value)


def validate_evaluation_models() -> None:
    """Fail before retrieval/inference rather than silently use rules or self-judging."""

    generation = model_settings("GENERATION")
    judge = model_settings("JUDGE")
    if not generation.model or not judge.model or judge.model.casefold() == "quote":
        raise RuntimeError("Evaluation requires GENERATION_MODEL and a separate JUDGE_MODEL")
    generator_id = generation.model.rsplit("/", 1)[-1].casefold()
    judge_id = judge.model.rsplit("/", 1)[-1].casefold()
    generator_size = _QWEN_SIZE.search(generator_id)
    judge_size = _QWEN_SIZE.search(judge_id)
    if generator_id == judge_id or (
        generator_size and judge_size and float(generator_size[1]) == float(judge_size[1])
    ):
        raise RuntimeError("Evaluation requires different generator and judge models")
    if generator_size and float(generator_size[1]) < 8:
        raise RuntimeError("The feedback requires Qwen3-8B or larger, or a suitable hosted model")
    try:
        temperature = float(os.environ.get("GENERATION_TEMPERATURE", "0"))
        int(os.environ.get("GENERATION_SEED", "0"))
    except ValueError as exc:
        raise RuntimeError("Evaluation temperature and seed must be numeric") from exc
    if temperature != 0:
        raise RuntimeError("Evaluation requires GENERATION_TEMPERATURE=0")


def evaluation_fingerprint() -> str:
    return fingerprint(
        [
            EVALUATION_PROTOCOL,
            [GRAPH_WEIGHT, HOP_DEPTH, REFERENCE_HOP_DEPTH, NODE_CAP],
            model_settings("GENERATION").fingerprint(),
            model_settings("JUDGE").fingerprint(),
            os.environ.get("GENERATION_TEMPERATURE", "0"),
            os.environ.get("GENERATION_SEED", "0"),
            os.environ.get("EMBEDDING_BACKEND", ""),
            os.environ.get("EMBEDDING_MODEL", ""),
        ]
    )


def main() -> int:
    configure_evaluation()
    try:
        validate_evaluation_models()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        f"Model configuration valid: generator={os.environ['GENERATION_MODEL']}, "
        f"judge={os.environ['JUDGE_MODEL']}. No endpoint calls made."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
