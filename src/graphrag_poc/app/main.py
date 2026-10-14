"""One page: question, answer, citations, and the fused ranking."""

import html
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

from graphrag_poc.generate.__main__ import LOOKUP, PROCEDURE, UNKNOWN, ask_with_hits
from graphrag_poc.generate.answer import Answer
from graphrag_poc.index.client import make_client
from graphrag_poc.index.embed import build_embedder
from graphrag_poc.retrieve.fusion import FusedHit

EXAMPLES = (
    ("Charging lookup", LOOKUP),
    ("Oil-cooler procedure", PROCEDURE),
    ("Unknown code", UNKNOWN),
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.embedder = build_embedder()
    app.state.client = make_client(api_key=os.environ.get("QDRANT_API_KEY") or None)
    yield


app = FastAPI(title="Graph RAG demonstration", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def show_form() -> str:
    return _page("")


@app.post("/", response_class=HTMLResponse)
def ask_question(request: Request, question: str = Form()) -> str:
    cleaned = " ".join(question.split())
    if not cleaned:
        return _page("", notice="Enter a question.")
    answer, hits = ask_with_hits(
        cleaned,
        client=request.app.state.client,
        embedder=request.app.state.embedder,
    )
    return _page(cleaned, answer=answer, hits=hits)


def _page(
    question: str,
    *,
    answer: Answer | None = None,
    hits: list[FusedHit] | None = None,
    notice: str = "",
) -> str:
    examples = "\n".join(
        "<form method=\"post\" action=\"/\">"
        f"<input type=\"hidden\" name=\"question\" value=\"{html.escape(text, quote=True)}\">"
        f"<button type=\"submit\">{html.escape(label)}</button>"
        "</form>"
        for label, text in EXAMPLES
    )
    body = ""
    if notice:
        body += f"<p class=\"notice\">{html.escape(notice)}</p>"
    if answer is not None and hits is not None:
        body += _result(answer, hits)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Graph RAG demonstration</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 2rem auto; max-width: 52rem; line-height: 1.45; }}
    textarea {{ width: 100%; min-height: 6rem; font: inherit; }}
    button {{ font: inherit; margin: 0.25rem 0.5rem 0.25rem 0; }}
    .examples {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0; }}
    .answer {{ white-space: pre-wrap; background: #f6f4ef; padding: 1rem; }}
    .refused {{ border-left: 4px solid #8a3b2b; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{
      text-align: left; vertical-align: top;
      border-top: 1px solid #ccc; padding: 0.4rem;
    }}
    .tag {{
      display: inline-block; border: 1px solid #444;
      padding: 0 0.3rem; margin-right: 0.2rem; font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <h1>Graph RAG demonstration</h1>
  <p>Ask a question. The answer, citations, and fused ranking
  come from the same retrieval code as the command line.</p>
  <form method="post" action="/">
    <label for="question">Question</label>
    <textarea id="question" name="question" required>{html.escape(question)}</textarea>
    <button type="submit">Ask</button>
  </form>
  <div class="examples">{examples}</div>
  {body}
</body>
</html>
"""


def _result(answer: Answer, hits: list[FusedHit]) -> str:
    kind = "answer refused" if answer.refused else "answer"
    citations = "\n".join(
        "<li>"
        f"<span class=\"document\">{html.escape(_document(citation.node_id))}</span>, "
        f"page {citation.page} "
        f"(<code>{html.escape(citation.node_id)}</code>)"
        "</li>"
        for citation in answer.citations
    )
    if not citations:
        citations = "<li>None</li>"
    rows = "\n".join(_rank_row(index, hit) for index, hit in enumerate(hits, start=1))
    return f"""
<section id="result">
  <h2 class="{kind}">{html.escape(kind.capitalize())}</h2>
  <div class="answer {kind}">{html.escape(answer.text)}</div>
  <h2>Citations</h2>
  <ul id="citations">{citations}</ul>
  <h2>Fused ranking</h2>
  <table id="ranking">
    <thead><tr><th>Rank</th><th>Channels</th><th>Document</th><th>Page</th><th>Passage</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>
"""


def _rank_row(rank: int, hit: FusedHit) -> str:
    tags = "".join(f"<span class=\"tag\">{html.escape(channel)}</span>" for channel in hit.channels)
    snippet = hit.text if len(hit.text) <= 180 else hit.text[:177] + "..."
    return (
        "<tr>"
        f"<td>{rank}</td>"
        f"<td class=\"channels\">{tags}</td>"
        f"<td>{html.escape(hit.doc_key)}</td>"
        f"<td>{hit.page_start}</td>"
        f"<td><code>{html.escape(hit.node_id)}</code> {html.escape(snippet)}</td>"
        "</tr>"
    )


def _document(node_id: str) -> str:
    return node_id.split(":", 1)[0]
