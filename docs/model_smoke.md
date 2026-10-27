# Model readiness and live smoke test

These checks can proceed while client scope/gold review is pending. They exercise model
availability, JSON compatibility, citation handling, refusal and judge support checks.
They do not measure retrieval, graph quality, M3 gains or acceptance. They do not start
Docker, rebuild indexes, create embeddings or download model weights.

## Local inspection for this revision

The inspected machine is an Apple M2 Mac with 16 GiB of memory. No `llama-server`,
`ollama`, `mlx_lm.server` or `vllm` executable was found on PATH. No model server was
listening on ports 8000 or 8001. The inspected Hugging Face cache contains a Qwen3
embedding model, not either configured Qwen3 answer/judge model. This is a bounded
inspection, not a search of every possible model location.

At the initial inspection there was no `.env`. With no overrides, both model roles fall back to the shared
`http://127.0.0.1:8000/v1` endpoint. The live metadata probe recorded both roles as
unavailable. The current snapshot is [readiness.json](../data/eval/model_smoke/readiness.json).
No inference was attempted. This snapshot records an observation; rerun the probe after
configuring or starting servers.

## Configure the actual host

Use existing model servers if available. First determine the generator and judge base
URLs, exact served model IDs and any required credentials. The models must actually be
different weights, not the same model behind different aliases. This code checks IDs;
it cannot attest to the weights loaded by a server.

If `.env` does not exist, copy `.env.example`; otherwise edit the existing file. For
two local servers matching the example, the relevant settings are:

```dotenv
GENERATION_MODEL=Qwen/Qwen3-8B
GENERATION_BASE_URL=http://127.0.0.1:8000/v1
JUDGE_MODEL=Qwen/Qwen3-14B
JUDGE_BASE_URL=http://127.0.0.1:8001/v1
GENERATION_TEMPERATURE=0
GENERATION_SEED=0
```

These lines configure clients; they do not start servers or establish hardware capacity.
For remote hosting, replace localhost with the actual reachable addresses and use the
server's exact model IDs. The endpoints must expose the compatible `/models` and
`/chat/completions` routes beneath their configured base URL. Role-specific API-key
settings are documented in `.env.example`.

## Inspect without inference

```bash
make model-check
make model-smoke-plan
make model-probe
```

`model-check` validates configuration only. `model-smoke-plan` loads source nodes,
verifies the required facts are inside the clipped model context, and writes
[plan.json](../data/eval/model_smoke/plan.json) without contacting endpoints.

`model-probe` performs model-list GET requests and writes `readiness.json`. It reuses one
listing when both roles share the same endpoint and credential. Each request has a
five-second timeout and no SDK automatic retries. It verifies that the configured model
IDs are listed. Authentication, connection or missing-model failures return a nonzero
exit status. A blocked probe is not a failed benchmark, and listing a model does not
prove that generation works.

Reports omit API keys and strip user-info/query parameters from displayed endpoint URLs.
Provider error bodies are not copied into the readiness report.

## Run the bounded live test

After both endpoints are available, start with the cheapest live check:

```bash
.venv/bin/python -m graphrag_poc.eval.smoke --run --limit 1
```

This makes at most three chat requests: one judge calibration, one generator answer and
one answer judgment. It uses a supplied oil-servicing passage, without retrieval.

Then run the complete small suite:

```bash
make model-smoke
```

The full suite makes at most three generator and three judge requests. These are live
inference requests; hosted providers can charge for them. Existing configured token
limits apply. The suite stops at its first failed check, and SDK automatic retries are
disabled. Every live run bypasses generator and judge caches so a previous answer cannot
make an unavailable server look ready.

The judge first receives a supported paraphrase and an invented purple-oil claim against
an oil-level passage. It must accept the supported content and reject the invented
content. This single diagnostic catches obvious unsupported positive judgments; it is
not a general judge-quality evaluation.

The generator cases are:

| Case | Supplied material | Required behaviour |
|---|---|---|
| Oil level | Operator oil-level note | Answer engine-off question with a valid source citation and supported fact |
| Bulb warning | Fault row and bulb-replacement warning | Answer the natural question with the shutdown warning, citing supporting supplied evidence |
| Insufficient evidence | Oil-level note | Refuse an unrelated missing-part torque question and return no citations |

The separate judge checks positive answers against only their cited passages. A missing
citation, missing required fact, unsupported claim, wrong refusal decision, invalid JSON
or truncated response fails the smoke test. Endpoint probes must pass before any chat
request. Earlier completed case outputs remain in the report if a later case fails.

The latest live attempt writes `data/eval/model_smoke/results.json`, including its input
plan/fingerprints, raw answer fields, citations and verified judgments. `--output-dir PATH`
can preserve separate runs. Existing baseline/M3 reports, gold and approval contracts are
not overwritten.

Latest live verification, 26 October 2026 (America/New_York): local Ollama serves
`qwen3:8b` and `qwen3:14b` at `http://127.0.0.1:11434/v1`. The complete six-request
smoke suite passed: supported/refuted judge calibration, oil-level answer, bulb shutdown
warning and the insufficient-evidence refusal. Both positive answers passed cited-fact
and claim checks. This establishes only the supplied-evidence smoke behavior, not
retrieval quality or M3 acceptance.

An earlier run failed because a diagnostic judge response changed source punctuation in
its evidence quote. The exact-match validator rejected it. The `judge-quotes-v3` prompt
now explicitly preserves source punctuation; matching and acceptance rules are unchanged.
The failed result is preserved in `history/oil_judgment_failure_before_diagnosis.json`
under `data/eval/model_smoke/`, with the raw recheck in `oil_judge_diagnostic.json`.
The revised code passed 47 focused tests, lint/formatting and type checking.

Validation for this revision: 176 tests passed, including ten new mock-HTTP smoke tests.
`make lint` (including formatting) and `make typecheck` passed on 71 source files. The
initial model-list probe returned `blocked`; no live LLM inference or model downloads were
performed during that implementation step. See the later live verification above.
Successful mocked protocol tests do not replace a real endpoint smoke test.

## After a passing smoke test

Keep scope/gold work separate. A smoke pass does not approve the 25 review candidates or
fill the 50-question gap. Once the actual benchmark and client agreement are complete,
make any required traversal changes, rebuild the corrected indexes/graph, and run the
fresh baseline and graph comparison described in the README.
