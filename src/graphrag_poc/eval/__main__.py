"""Write and check data/eval/questions.jsonl."""

import sys

from graphrag_poc.eval.build import build_questions, write_questions
from graphrag_poc.eval.check import validate


def main() -> int:
    questions = build_questions()
    path = write_questions(questions)
    errors = validate(questions)
    if errors:
        for error in errors[:30]:
            print(error, file=sys.stderr)
        print(f"{len(errors)} evaluation-set errors", file=sys.stderr)
        return 1
    print(f"wrote {len(questions)} questions to {path}")
    print("evaluation set check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
