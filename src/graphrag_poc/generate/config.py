"""Model connection settings shared by answering and evaluation."""

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class ModelSettings:
    model: str
    base_url: str
    api_key: str = field(repr=False)
    max_tokens: int
    extra_body: dict[str, object]

    def fingerprint(self) -> str:
        """Track endpoint/model/request changes without storing keys or endpoint URLs."""

        return fingerprint([self.model, self.base_url, self.max_tokens, self.extra_body])


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def load_env_file() -> None:
    """Read simple KEY=value settings; exported values take precedence."""

    path = Path(".env")
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def model_settings(role: Literal["GENERATION", "JUDGE"]) -> ModelSettings:
    model = os.environ.get(f"{role}_MODEL", "").strip()
    base_url = os.environ.get(f"{role}_BASE_URL", "").strip() or os.environ.get(
        "OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"
    )
    api_key = os.environ.get(f"{role}_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    try:
        max_tokens = int(
            os.environ.get(f"{role}_MAX_TOKENS", "1536" if role == "GENERATION" else "4096")
        )
    except ValueError as exc:
        raise RuntimeError(f"{role}_MAX_TOKENS must be a positive integer") from exc
    if max_tokens <= 0:
        raise RuntimeError(f"{role}_MAX_TOKENS must be a positive integer")
    default_extra = (
        '{"chat_template_kwargs":{"enable_thinking":false}}'
        if "qwen3" in model.casefold()
        else "{}"
    )
    try:
        extra = json.loads(os.environ.get(f"{role}_EXTRA_BODY", default_extra))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{role}_EXTRA_BODY must be a JSON object") from exc
    reserved = {"model", "messages", "temperature", "seed", "max_tokens", "response_format"}
    if not isinstance(extra, dict) or reserved.intersection(extra):
        raise RuntimeError(f"{role}_EXTRA_BODY must be an object without standard request fields")
    return ModelSettings(model, base_url, api_key, max_tokens, extra)
