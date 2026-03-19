"""
Async, provider-agnostic LLM adapter.

Supports OpenAI, Anthropic, and any OpenAI-compatible API (Ollama, LM Studio).
Uses httpx for async HTTP — no heavyweight SDK dependencies.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    pass  # avoid circular import at runtime


_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"

# Timeout for LLM calls
_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class LLMAdapter:
    """
    Async LLM client that speaks to OpenAI, Anthropic, or OpenAI-compatible
    endpoints. Falls back to a stub when the API key is 'test-key'.
    """

    def __init__(self, settings) -> None:
        self.provider: str = settings.llm_provider
        self.api_key: str = settings.llm_api_key
        self.model: str = settings.llm_model
        self.base_url: str = settings.llm_base_url or ""
        self.max_tokens: int = settings.llm_max_tokens

    @property
    def is_stub(self) -> bool:
        return not self.api_key or self.api_key == "test-key"

    # ── Public API ─────────────────────────────────────────────────────────────

    async def complete(self, messages: list[dict], json_mode: bool = False) -> str:
        """Send a chat completion request and return the response text."""
        if self.is_stub:
            return ""  # caller should use stub path before calling here

        if self.provider == "anthropic":
            return await self._anthropic(messages)
        else:
            # openai or openai_compatible
            return await self._openai(messages, json_mode=json_mode)

    async def complete_json(self, messages: list[dict]) -> dict:
        """Send a request expecting JSON back; parse and return the dict."""
        raw = await self.complete(messages, json_mode=True)
        return _parse_json(raw)

    # ── OpenAI ─────────────────────────────────────────────────────────────────

    async def _openai(self, messages: list[dict], json_mode: bool = False) -> str:
        url = (
            f"{self.base_url.rstrip('/')}/chat/completions"
            if self.base_url
            else _OPENAI_URL
        )
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    # ── Anthropic ──────────────────────────────────────────────────────────────

    async def _anthropic(self, messages: list[dict]) -> str:
        # Anthropic requires system message to be a separate field
        system = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        payload: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": chat_messages,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                _ANTHROPIC_URL,
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": _ANTHROPIC_VERSION,
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]


# ── JSON parsing helper ────────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """
    Parse JSON from LLM output. Handles markdown fences like ```json ... ```.
    """
    text = text.strip()
    # Strip markdown fences
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    return json.loads(text)
