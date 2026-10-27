# Model evaluation revision — 26 October 2026

Feedback item 3 is implemented in code. End-to-end model scoring remains pending; no
LLM downloads, generation calls, judging calls, or production index/graph rebuilds were
performed for this step. Validation used local tests and mocked LLM responses; earlier
reported scores remain historical.

## Answer behaviour

With `GENERATION_MODEL` set, the generator receives the supplied passages directly.
The regex title reader, passage-quoting answer, procedure selector, automatic part
append, and fallback citations are bypassed. The model decides whether the evidence
answers the question, including natural wording and unmatched numbered titles.

The response must be JSON with `answer`, a Boolean `refused`, and `citations` containing
`node_id` and integer `page`. Only supplied IDs with their supplied first page are kept;
duplicate citations are collapsed. Missing citations stay missing and cannot earn
support credit. Citation validation establishes source identity, not entailment; the
separate judge checks support. Graph frames are explicitly labelled unverified hints,
and the model is told not to infer a repair link from a keyword match.

Invalid JSON or truncated output stops evaluation instead of substituting a rule answer.
The old no-model quote helper remains available for offline retrieval demonstrations;
evaluation rejects that mode.

## Models and setup

Evaluation defaults to `Qwen/Qwen3-8B` for answers and `Qwen/Qwen3-14B` for the judge.
Both baseline and graph CLI processes load the same `.env`/exported settings. A blank
role, identical model IDs (including a provider-prefix variant), the legacy sub-8B Qwen3
generator, or nonzero evaluation temperature fails preflight. Arbitrary server aliases
cannot establish model size or independence; the operator must verify their actual
weights. Hosted alternatives must support the configured chat/JSON request parameters.

The generator and judge can use different endpoints and credentials. Role-specific
`GENERATION_BASE_URL`/`GENERATION_API_KEY` and `JUDGE_BASE_URL`/`JUDGE_API_KEY` override
the shared `OPENAI_BASE_URL`/`OPENAI_API_KEY`. Copy `.env.example` and adjust the served
IDs to match your servers. Do not use the same weights under different aliases.

For a suitable local vLLM deployment, start the two servers separately:

```bash
vllm serve Qwen/Qwen3-8B --port 8000
vllm serve Qwen/Qwen3-14B --port 8001
```

The example environment points the judge at port 8001. Without that override, both roles
use the shared endpoint, which must serve both model IDs. Docker Compose does not start
model servers. Qwen's [official deployment guide](https://qwen.readthedocs.io/en/stable/deployment/vllm.html)
documents the compatible client, JSON output, and framework-specific non-thinking
extension. This code sends that extension for Qwen3 names by default; set the respective
`GENERATION_EXTRA_BODY={}` or `JUDGE_EXTRA_BODY={}` when the server does not support it.
Other model names receive no framework-specific extras by default.

```bash
make model-check
```

This checks configuration only, without contacting endpoints. It does not establish
server availability or model quality. An actual smoke run and fresh scoring are still
needed after the gold and written target scope are ready.

## Judge and usage controls

The judge sees answer sentences, required facts, and the cited passages. Positive
judgments require a literal Boolean true, the correct fact/sentence identity, and an
exact quote from a passage shown to the judge. Missing or mismatched rows receive no
credit. Missing citations skip the judge request and receive no support credit.

The `judge-quotes-v3` prompt explicitly requires character-for-character evidence,
including OCR punctuation and quotation marks. A local smoke failure exposed a judge
that marked an oil-level sentence supported but corrected punctuation inside its quote;
the exact-match validator correctly rejected that quote. The stricter instruction keeps
the validation rule unchanged. The judge cache key and evaluation protocol were bumped
so earlier judgments and baseline configurations cannot silently carry over. The failed
smoke result and a raw diagnostic judgment are retained under `data/eval/model_smoke/`.

Output limits default to 1,536 generator tokens and 4,096 judge tokens. The existing
1,500-character passage limit is retained. Temperature is zero with a fixed seed;
SDK automatic retries are disabled. Truncation requires an explicit configuration
adjustment rather than a hidden retry. Seeds do not guarantee identical server output.

Evaluation caches answers by prompt version, model/endpoint/settings, question, clipped
passages, and graph hints. The default directory is `data/eval/answers`; an explicitly
empty `GENERATION_CACHE_DIR` disables it. Repeated identical inputs reuse an answer.
Judge caches now also fingerprint required facts, cited text, judge endpoint/settings,
seed, and protocol version. Old caches cannot silently score the new protocol. API keys
are excluded from fingerprints and are not written to reports or caches.

## Fresh evaluation

`make baseline`, `make m3`, and `make eval` check gold/scope readiness and model
configuration before starting services. Once those approvals exist, rebuild the
corrected node/case indexes and establish a new baseline before comparing the graph:

```bash
make up
make index
make graph
make baseline
make m3
make eval
```

`make eval` reproduces this new baseline and graph result. It refuses incompatible
question/model-protocol fingerprints before indexing or inference. `make m3` checks
that its baseline uses the same questions and model configuration before graph/model
work. Raw answers and citation/evidence IDs are retained in new run results.

The 50 keyword-derived questions are still exploratory. This implementation does not
approve gold, change the +15/+10 thresholds, or claim that M3/M4 acceptance has passed.

Validation: 155 tests passed, including 22 new mocked-model checks. `make lint` passed
(lint and formatting), `make typecheck` passed on 69 source files, and `make model-check`
passed without endpoint calls. Live model availability and output quality remain unverified.
