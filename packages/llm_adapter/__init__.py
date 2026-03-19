"""
packages.llm_adapter
~~~~~~~~~~~~~~~~~~~~
Provider-agnostic async LLM client.

Supports OpenAI, Anthropic, and any OpenAI-compatible API (Ollama, LM Studio).
"""

from .adapter import LLMAdapter

__version__ = "0.2.0"
__all__ = ["LLMAdapter"]
