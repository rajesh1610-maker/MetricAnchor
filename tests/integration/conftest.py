"""
Integration test configuration.

Provides a temporary DuckDB engine pre-loaded with the deterministic
retail_sales.csv sample data, and a stub LLM adapter.
No network access or real API key is required.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.query_engine.engine import QueryEngine  # noqa: E402

SAMPLE_DATA = ROOT / "sample_data"


@dataclass
class StubSettings:
    llm_provider: str = "openai"
    llm_api_key: str = "test-key"
    llm_model: str = "stub"
    llm_base_url: str = ""
    llm_max_tokens: int = 512


class StubLLM:
    """Minimal LLM duck-type that forces the stub path in the pipeline."""

    is_stub: bool = True

    async def complete(self, messages, json_mode: bool = False) -> str:
        return ""

    async def complete_json(self, messages) -> dict:
        return {}


def _make_engine(tmp_path_factory, csv_name: str, view_name: str) -> QueryEngine:
    """Build a QueryEngine with a pre-registered CSV view (sync wrapper)."""
    path = SAMPLE_DATA / csv_name
    if not path.exists():
        pytest.skip(
            f"{csv_name} not found — run 'python3 sample_data/generate.py' first"
        )
    db = str(tmp_path_factory.mktemp("dbs") / f"{view_name}_test.duckdb")
    engine = QueryEngine(db)
    asyncio.get_event_loop().run_until_complete(
        engine.register_dataset(view_name, str(path))
    )
    return engine


# ── Engine fixtures ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def retail_engine(tmp_path_factory):
    return _make_engine(tmp_path_factory, "retail_sales.csv", "retail_sales")


@pytest.fixture(scope="session")
def support_engine(tmp_path_factory):
    return _make_engine(tmp_path_factory, "support_tickets.csv", "support_tickets")


@pytest.fixture(scope="session")
def funnel_engine(tmp_path_factory):
    return _make_engine(tmp_path_factory, "saas_funnel.csv", "saas_funnel")


@pytest.fixture(scope="session")
def stub_llm():
    return StubLLM()


@pytest.fixture(scope="session")
def stub_settings():
    return StubSettings()


# ── Semantic model fixtures ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def retail_model_def():
    import yaml
    path = ROOT / "examples" / "retail_sales" / "semantic_model.yml"
    if not path.exists():
        pytest.skip("retail_sales semantic model not found")
    return yaml.safe_load(path.read_text())


@pytest.fixture(scope="session")
def support_model_def():
    import yaml
    path = ROOT / "examples" / "support_tickets" / "semantic_model.yml"
    if not path.exists():
        pytest.skip("support_tickets semantic model not found")
    return yaml.safe_load(path.read_text())


@pytest.fixture(scope="session")
def funnel_model_def():
    import yaml
    path = ROOT / "examples" / "saas_funnel" / "semantic_model.yml"
    if not path.exists():
        pytest.skip("saas_funnel semantic model not found")
    return yaml.safe_load(path.read_text())
