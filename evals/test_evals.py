"""
pytest entry point for the eval suite.

Runs all eval cases via pytest parametrize so they appear as individual
test items with clean pass/fail output. The eval runner is also available
as a standalone CLI: `python -m evals.runner`
"""

from __future__ import annotations

import asyncio
import math
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.cases import ALL_CASES, EvalCase  # noqa: E402
from evals.runner import _build_engines, _run_assertions, StubLLM, StubSettings  # noqa: E402
from packages.query_engine.pipeline import execute_pipeline  # noqa: E402


# ── Session-scoped engines (loaded once for all parametrized cases) ────────────

@pytest.fixture(scope="session")
def _tmp_db_dir(tmp_path_factory):
    return str(tmp_path_factory.mktemp("eval_dbs"))


@pytest.fixture(scope="session")
def engines(_tmp_db_dir):
    return asyncio.get_event_loop().run_until_complete(_build_engines(_tmp_db_dir))


@pytest.fixture(scope="session")
def stub_llm():
    return StubLLM()


@pytest.fixture(scope="session")
def stub_settings():
    return StubSettings()


# ── Parametrized eval tests ────────────────────────────────────────────────────

@pytest.mark.parametrize("case", ALL_CASES, ids=[c.id for c in ALL_CASES])
def test_eval_case(case: EvalCase, engines, stub_llm, stub_settings):
    if case.dataset not in engines:
        pytest.skip(
            f"Dataset '{case.dataset}' not loaded — "
            "run 'python3 sample_data/generate.py' to generate sample data"
        )

    engine, model_def = engines[case.dataset]

    async def _run():
        return await execute_pipeline(
            question=case.question,
            view_name=case.dataset,
            model_definition=model_def,
            engine=engine,
            llm=stub_llm,
            settings=stub_settings,
        )

    result = asyncio.get_event_loop().run_until_complete(_run())
    failures = _run_assertions(result, case)

    if failures:
        msg = f"\n[{case.id}] Q: {case.question}\n" + "\n".join(f"  - {f}" for f in failures)
        if result.sql:
            msg += f"\nSQL:\n{result.sql}"
        pytest.fail(msg)
