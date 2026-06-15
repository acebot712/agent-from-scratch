"""Provider-agnostic LLM client.

Implements: V1.2 (a provider-agnostic LLM wrapper).

Exposes two calls the rest of the framework depends on:

  * ``complete(messages, tools=None)`` — chat completion, returns a normalised
    :class:`LLMResponse` regardless of provider.
  * ``embed(texts)`` — embeddings, returns a list of float vectors. Memory
    retrieval (Module 3) needs these, and embedding is a distinct call from
    chat completion.

Provider selection is by env var ``LLM_PROVIDER`` (``openai`` | ``anthropic``).
The HTTP layer is kept deliberately thin and dependency-free (stdlib
``urllib``) so the only third-party runtime dep is numpy.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# --- Normalised response object ------------------------------------------------

@dataclass
class ToolCall:
    """A single tool/function call the model asked for."""

    name: str
    args: dict[str, Any]
    id: str | None = None


@dataclass
class LLMResponse:
    """One normalised shape for every provider's chat completion.

    Whatever the provider returns, downstream code only ever sees this.
    """

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:  # convenience for quick demos
        return self.text


# --- Config --------------------------------------------------------------------

def _provider() -> str:
    return os.environ.get("LLM_PROVIDER", "openai").lower().strip()


def _api_key() -> str:
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise RuntimeError(
            "LLM_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return key


_RETRYABLE = {429, 500, 502, 503, 504}  # transient: rate limit / server hiccups


def _post(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    """Minimal JSON POST using only the standard library, with timeout + retries.

    Tunable via env: ``LLM_TIMEOUT`` (seconds, default 60) and ``LLM_MAX_RETRIES``
    (default 2). Retries use exponential backoff and only fire for transient
    HTTP/network errors — a 400/401 fails fast.
    """
    data = json.dumps(payload).encode("utf-8")
    timeout = float(os.environ.get("LLM_TIMEOUT", "60"))  # never hang forever
    retries = int(os.environ.get("LLM_MAX_RETRIES", "2"))
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # surface the provider's error body
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in _RETRYABLE and attempt < retries:
                last_err = exc
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise RuntimeError(f"LLM HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:  # network/timeout
            if attempt < retries:
                last_err = exc
                time.sleep(0.5 * (2 ** attempt))
                continue
            raise RuntimeError(f"LLM request failed: {exc}") from exc
    raise RuntimeError(f"LLM request failed after {retries} retries: {last_err}")


# --- OpenAI-compatible backend -------------------------------------------------

def _openai_complete(messages, tools, model, **kw) -> LLMResponse:
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    payload: dict[str, Any] = {
        "model": model or os.environ.get("LLM_MODEL", "gpt-4o-mini"),
        "messages": messages,
    }
    if tools:
        payload["tools"] = [{"type": "function", "function": t} for t in tools]
    payload.update(kw)
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    raw = _post(f"{base}/chat/completions", headers, payload)
    choice = raw["choices"][0]
    msg = choice.get("message", {})
    tool_calls = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function", {})
        args = fn.get("arguments") or "{}"
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {"_raw": args}
        tool_calls.append(ToolCall(name=fn.get("name", ""), args=args, id=tc.get("id")))
    return LLMResponse(
        text=msg.get("content") or "",
        tool_calls=tool_calls,
        stop_reason=choice.get("finish_reason"),
        raw=raw,
    )


def _openai_embed(texts, model) -> list[list[float]]:
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or os.environ.get("LLM_EMBED_MODEL", "text-embedding-3-small"),
        "input": texts,
    }
    raw = _post(f"{base}/embeddings", headers, payload)
    return [item["embedding"] for item in raw["data"]]


# --- Anthropic backend ---------------------------------------------------------

def _to_anthropic_messages(messages):
    """Split OpenAI-style messages into (system, messages) for Anthropic."""
    system_parts, conv = [], []
    for m in messages:
        if m["role"] == "system":
            system_parts.append(m["content"])
        else:
            conv.append({"role": m["role"], "content": m["content"]})
    return "\n\n".join(system_parts), conv


def _anthropic_complete(messages, tools, model, **kw) -> LLMResponse:
    base = os.environ.get("LLM_BASE_URL", "https://api.anthropic.com/v1")
    system, conv = _to_anthropic_messages(messages)
    payload: dict[str, Any] = {
        "model": model or os.environ.get("LLM_MODEL", "claude-sonnet-4-6"),
        "messages": conv,
        "max_tokens": kw.pop("max_tokens", 1024),
    }
    if system:
        payload["system"] = system
    if tools:
        payload["tools"] = [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": t.get("parameters", {"type": "object", "properties": {}}),
            }
            for t in tools
        ]
    payload.update(kw)
    headers = {
        "x-api-key": _api_key(),
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    raw = _post(f"{base}/messages", headers, payload)
    text_parts, tool_calls = [], []
    for block in raw.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block["text"])
        elif block.get("type") == "tool_use":
            tool_calls.append(
                ToolCall(name=block["name"], args=block.get("input", {}), id=block.get("id"))
            )
    return LLMResponse(
        text="".join(text_parts),
        tool_calls=tool_calls,
        stop_reason=raw.get("stop_reason"),
        raw=raw,
    )


def _anthropic_embed(texts, model) -> list[list[float]]:
    # Anthropic has no first-party embeddings endpoint; route embeddings through
    # an OpenAI-compatible provider by setting LLM_EMBED_PROVIDER=openai.
    raise RuntimeError(
        "Anthropic has no embeddings endpoint. Set LLM_EMBED_PROVIDER=openai "
        "(and matching LLM_EMBED_BASE_URL / key) to use embed()."
    )


# --- Public API ----------------------------------------------------------------

def complete(messages, tools=None, *, model=None, **kwargs) -> LLMResponse:
    """Chat completion against the configured provider.

    Args:
        messages: list of ``{"role", "content"}`` dicts (OpenAI shape).
        tools: optional list of tool schemas ``{"name", "description", "parameters"}``.
        model: optional model override (else taken from ``LLM_MODEL``).

    Returns:
        A normalised :class:`LLMResponse`.
    """
    provider = _provider()
    if provider in ("openai", "openai-compatible", "compatible"):
        return _openai_complete(messages, tools, model, **kwargs)
    if provider == "anthropic":
        return _anthropic_complete(messages, tools, model, **kwargs)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")


def embed(texts, *, model=None) -> list[list[float]]:
    """Return an embedding vector for each input string.

    Embeddings can be sourced from a different provider than chat completion via
    ``LLM_EMBED_PROVIDER`` (defaults to ``LLM_PROVIDER``).
    """
    if isinstance(texts, str):
        texts = [texts]
    provider = os.environ.get("LLM_EMBED_PROVIDER", _provider()).lower().strip()
    if provider in ("openai", "openai-compatible", "compatible"):
        return _openai_embed(texts, model)
    if provider == "anthropic":
        return _anthropic_embed(texts, model)
    raise ValueError(f"Unknown LLM_EMBED_PROVIDER: {provider!r}")
