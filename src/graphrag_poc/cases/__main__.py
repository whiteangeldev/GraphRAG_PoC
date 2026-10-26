"""`python -m graphrag_poc.cases` writes data/cases/cases.jsonl."""

import sys

from graphrag_poc.cases.generate import (
    consistent_with_source,
    generate_cases,
    missing_references,
    write_cases,
)
from graphrag_poc.cases.report import write_quality_report
from graphrag_poc.cases.rules import load_rules
from graphrag_poc.cases.sources import load_faults


def main() -> int:
    rules = load_rules()
    first = generate_cases(rules)
    second = generate_cases(rules)
    if [case.model_dump(mode="json") for case in first] != [
        case.model_dump(mode="json") for case in second
    ]:
        print("two runs did not match", file=sys.stderr)
        return 1
    if len(first) < 2000:
        print(f"expected at least 2000 cases, wrote {len(first)}", file=sys.stderr)
        return 1
    missing = missing_references(first)
    inconsistent = consistent_with_source(first, load_faults(rules))
    problems = missing + inconsistent
    if problems:
        for problem in problems[:20]:
            print(problem, file=sys.stderr)
        return 1
    path = write_cases(first)
    write_quality_report(first, rules)
    print(f"wrote {len(first)} cases to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
