"""`python -m graphrag_poc.app` serves the demonstration page."""

import os

import uvicorn

from graphrag_poc.generate.__main__ import _load_env_file


def main() -> None:
    _load_env_file()
    uvicorn.run(
        "graphrag_poc.app.main:app",
        host="127.0.0.1",
        port=int(os.environ.get("DEMO_PORT", "8080")),
        reload=False,
    )


if __name__ == "__main__":
    main()
