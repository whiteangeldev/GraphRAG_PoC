"""`python -m graphrag_poc.ingest` writes the node files and validates them."""

import argparse
import sys

from graphrag_poc.ingest.catalog import DOCUMENTS
from graphrag_poc.ingest.convert import convert_all


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert the approved corpus to JSONL node files.")
    parser.add_argument(
        "--doc",
        action="append",
        choices=[spec.doc_key for spec in DOCUMENTS],
        help="Convert one document. Repeat to convert several. Default: all approved documents.",
    )
    args = parser.parse_args(argv)
    errors = convert_all(args.doc)
    failed = {key: messages for key, messages in errors.items() if messages}
    if failed:
        for key, messages in failed.items():
            print(f"{key}:", file=sys.stderr)
            for message in messages[:20]:
                print(f"  {message}", file=sys.stderr)
        return 1
    print("validator accepted every node file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
