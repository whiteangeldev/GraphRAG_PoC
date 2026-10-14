"""The demonstration page uses the same three questions as the command-line check."""

import pytest
from fastapi.testclient import TestClient

from graphrag_poc.generate.__main__ import HOT_OIL, LOOKUP, PROCEDURE, UNKNOWN
from graphrag_poc.index.client import make_client


def _qdrant_ready() -> bool:
    try:
        return make_client(timeout=5).get_collections() is not None
    except Exception:
        return False


@pytest.mark.skipif(not _qdrant_ready(), reason="Qdrant is not running")
def test_demo_page_answers_the_three_questions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_BACKEND", "fastembed")
    monkeypatch.setenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    monkeypatch.delenv("GENERATION_MODEL", raising=False)
    from graphrag_poc.app.main import app

    with TestClient(app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert "Question" in home.text

        lookup = client.post("/", data={"question": LOOKUP})
        assert lookup.status_code == 200
        assert "Check battery cable connections" in lookup.text
        assert "tm280_10:table:3-1:2:r4" in lookup.text
        assert "page 281" in lookup.text
        assert 'class="tag"' in lookup.text

        procedure = client.post("/", data={"question": PROCEDURE})
        assert procedure.status_code == 200
        assert "Disconnect two engine oil cooler" in procedure.text
        assert HOT_OIL in procedure.text
        warning = procedure.text.find(HOT_OIL)
        disconnect = procedure.text.find("1. Disconnect two engine oil cooler")
        assert warning < disconnect
        assert "tm280_20_2" in procedure.text
        assert "page 32" in procedure.text

        unknown = client.post("/", data={"question": UNKNOWN})
        assert unknown.status_code == 200
        assert "No retrieved passage contains the requested material" in unknown.text
        assert UNKNOWN in unknown.text
        assert "<li>None</li>" in unknown.text
