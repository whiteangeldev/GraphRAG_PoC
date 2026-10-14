"""The evaluation set meets the Appendix C counts and cites real passages."""

import json

from graphrag_poc.eval.build import build_questions
from graphrag_poc.eval.check import QUESTIONS_PATH, load_questions, validate


def test_builder_passes_the_exit_check() -> None:
    questions = build_questions()
    assert validate(questions) == []


def test_saved_questions_match_the_builder() -> None:
    assert QUESTIONS_PATH.exists(), "run python -m graphrag_poc.eval first"
    saved = QUESTIONS_PATH.read_text(encoding="utf-8")
    rendered = "\n".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        for record in build_questions()
    )
    assert saved == rendered + "\n"
    assert validate(load_questions()) == []
