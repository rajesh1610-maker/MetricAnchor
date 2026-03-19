"""
packages.llm_adapter
~~~~~~~~~~~~~~~~~~~~
Provider-agnostic LLM abstraction layer.

Supports OpenAI, Anthropic, and any OpenAI-compatible API (Ollama, LM Studio).
Implemented fully in Phase 4.
"""

from abc import ABC, abstractmethod

__version__ = "0.1.0"


class LLMAdapter(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a prompt and return the raw text response."""
        ...


class LLMAdapterFactory:
    """Create the correct adapter from application settings."""

    @staticmethod
    def from_settings(settings) -> LLMAdapter:
        provider = settings.llm_provider
        if provider == "openai":
            from .openai_adapter import OpenAIAdapter
            return OpenAIAdapter(settings)
        if provider == "anthropic":
            from .anthropic_adapter import AnthropicAdapter
            return AnthropicAdapter(settings)
        if provider == "openai_compatible":
            from .openai_adapter import OpenAIAdapter
            return OpenAIAdapter(settings, base_url=settings.llm_base_url)
        raise ValueError(f"Unknown LLM provider: {provider!r}. Choose openai, anthropic, or openai_compatible.")
