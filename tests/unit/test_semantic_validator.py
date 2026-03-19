"""
Unit tests for SemanticModelValidator.validate().

Each test targets a specific validation rule so failures are easy to diagnose.
"""

import pytest

from packages.semantic_model.validator import SemanticModelValidator

VALIDATOR = SemanticModelValidator()


def _base_model(**overrides) -> dict:
    """Minimal valid model dict. Pass keyword overrides to mutate specific keys."""
    m = {
        "name": "orders",
        "dataset": "orders",
        "description": "Order analytics",
        "grain": "one row per order",
        "time_column": "order_date",
        "metrics": [
            {
                "name": "revenue",
                "description": "Total revenue",
                "expression": "SUM(order_total)",
                "aliases": ["sales"],
                "format": "currency",
            }
        ],
        "dimensions": [
            {
                "name": "region",
                "column": "region",
                "description": "Sales region",
            }
        ],
    }
    m.update(overrides)
    return m


# ── Valid model passes ─────────────────────────────────────────────────────────

def test_valid_model_passes(minimal_model):
    result = VALIDATOR.validate(minimal_model)
    assert result.valid, result.errors


def test_base_model_passes():
    result = VALIDATOR.validate(_base_model())
    assert result.valid, result.errors


# ── Required fields ────────────────────────────────────────────────────────────

def test_missing_name_fails():
    m = _base_model()
    del m["name"]
    result = VALIDATOR.validate(m)
    assert not result.valid
    assert any("name" in e.lower() for e in result.errors)


def test_missing_metrics_fails():
    m = _base_model()
    del m["metrics"]
    result = VALIDATOR.validate(m)
    assert not result.valid


def test_empty_metrics_fails():
    m = _base_model(metrics=[])
    result = VALIDATOR.validate(m)
    assert not result.valid


def test_metric_missing_expression_fails():
    m = _base_model(metrics=[{"name": "revenue", "description": "desc"}])
    result = VALIDATOR.validate(m)
    assert not result.valid


# ── Duplicate name checks ──────────────────────────────────────────────────────

def test_duplicate_metric_names_fails():
    m = _base_model(metrics=[
        {"name": "revenue", "description": "d", "expression": "SUM(x)", "aliases": ["r"]},
        {"name": "revenue", "description": "d2", "expression": "COUNT(*)", "aliases": ["rc"]},
    ])
    result = VALIDATOR.validate(m)
    assert not result.valid
    assert any("duplicate" in e.lower() or "revenue" in e for e in result.errors)


def test_metric_and_dimension_same_name_fails():
    m = _base_model(
        metrics=[{"name": "region", "description": "d", "expression": "SUM(x)", "aliases": ["r"]}],
        dimensions=[{"name": "region", "column": "region", "description": "d"}],
    )
    result = VALIDATOR.validate(m)
    assert not result.valid


# ── Synonym target validation ──────────────────────────────────────────────────

def test_synonym_valid_metric_target():
    m = _base_model(synonyms=[{"phrase": "best selling", "maps_to": "metric:revenue"}])
    result = VALIDATOR.validate(m)
    assert result.valid, result.errors


def test_synonym_unknown_metric_target_fails():
    m = _base_model(synonyms=[{"phrase": "best selling", "maps_to": "metric:nonexistent"}])
    result = VALIDATOR.validate(m)
    assert not result.valid
    assert any("nonexistent" in e for e in result.errors)


def test_synonym_invalid_format_fails():
    m = _base_model(synonyms=[{"phrase": "foo", "maps_to": "just_a_name"}])
    result = VALIDATOR.validate(m)
    assert not result.valid


# ── Metric name safety ─────────────────────────────────────────────────────────

def test_metric_name_with_space_fails():
    m = _base_model(metrics=[
        {"name": "total revenue", "description": "d", "expression": "SUM(x)", "aliases": ["r"]}
    ])
    result = VALIDATOR.validate(m)
    assert not result.valid


def test_metric_name_with_hyphen_fails():
    m = _base_model(metrics=[
        {"name": "revenue-usd", "description": "d", "expression": "SUM(x)", "aliases": ["r"]}
    ])
    result = VALIDATOR.validate(m)
    assert not result.valid


# ── Warnings (not errors) ──────────────────────────────────────────────────────

def test_missing_description_is_warning_not_error():
    m = _base_model(metrics=[
        {"name": "revenue", "expression": "SUM(x)", "aliases": ["r"]}
    ])
    result = VALIDATOR.validate(m)
    assert result.valid  # should still be valid
    assert any("description" in w.lower() for w in result.warnings)


def test_missing_aliases_is_warning_not_error():
    m = _base_model(metrics=[
        {"name": "revenue", "description": "Total revenue", "expression": "SUM(x)"}
    ])
    result = VALIDATOR.validate(m)
    assert result.valid
    assert any("aliases" in w.lower() for w in result.warnings)
