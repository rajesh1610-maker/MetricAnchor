"""
Unit tests for _compute_confidence().

Covers all four confidence levels: high, medium, low,
and clarification_needed.
"""

import pytest

from packages.query_engine.pipeline import _compute_confidence
from packages.query_engine.pipeline_types import MappingResult, TermMapping


def _metric(name: str, via: str = "exact", confidence: float = 1.0) -> TermMapping:
    return TermMapping(
        phrase=name,
        resolved_name=name,
        resolved_type="metric",
        resolved_to=f"metric:{name}",
        via=via,
        confidence=confidence,
    )


def _dim(name: str, via: str = "exact", confidence: float = 1.0) -> TermMapping:
    return TermMapping(
        phrase=name,
        resolved_name=name,
        resolved_type="dimension",
        resolved_to=f"dimension:{name}",
        via=via,
        confidence=confidence,
    )


def _mapping(
    metrics=None,
    dims=None,
    unmapped=None,
    needs_clarification=False,
) -> MappingResult:
    return MappingResult(
        resolved_metrics=metrics or [],
        resolved_dimensions=dims or [],
        unmapped=unmapped or [],
        assumptions=[],
        overall_confidence=1.0,
        needs_clarification=needs_clarification,
        clarifying_question=None,
    )


# ── Clarification needed ───────────────────────────────────────────────────────

def test_clarification_needed():
    m = _mapping(needs_clarification=True)
    level, note = _compute_confidence(m)
    assert level == "clarification_needed"
    assert "ambiguous" in note.lower() or "clarification" in note.lower()


# ── Low confidence ─────────────────────────────────────────────────────────────

def test_low_no_resolved_metrics():
    m = _mapping(metrics=[], needs_clarification=False)
    level, note = _compute_confidence(m)
    assert level == "low"


# ── High confidence ────────────────────────────────────────────────────────────

def test_high_exact_match():
    m = _mapping(metrics=[_metric("revenue", via="exact", confidence=1.0)])
    level, note = _compute_confidence(m)
    assert level == "high"
    assert "exact" in note.lower()


def test_high_exact_metric_and_dimension():
    m = _mapping(
        metrics=[_metric("revenue", via="exact", confidence=1.0)],
        dims=[_dim("region", via="exact", confidence=1.0)],
    )
    level, note = _compute_confidence(m)
    assert level == "high"


# ── Medium confidence ──────────────────────────────────────────────────────────

def test_medium_alias_match():
    m = _mapping(metrics=[_metric("revenue", via="alias", confidence=0.8)])
    level, note = _compute_confidence(m)
    assert level == "medium"
    assert "alias" in note.lower() or "synonym" in note.lower()


def test_medium_default_metric():
    m = _mapping(metrics=[_metric("revenue", via="default", confidence=0.5)])
    level, note = _compute_confidence(m)
    assert level == "medium"
    assert "default" in note.lower()


def test_medium_with_unmapped_terms():
    m = _mapping(
        metrics=[_metric("revenue", via="exact", confidence=1.0)],
        unmapped=["foobar"],
    )
    level, note = _compute_confidence(m)
    assert level == "medium"
    assert "foobar" in note


def test_medium_low_confidence_mapping():
    m = _mapping(metrics=[_metric("revenue", via="alias", confidence=0.6)])
    level, note = _compute_confidence(m)
    assert level == "medium"
