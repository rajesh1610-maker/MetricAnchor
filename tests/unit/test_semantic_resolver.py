"""
Unit tests for SemanticResolver.

Validates index building, metric/dimension resolution by name and alias,
synonym resolution, metric_sql generation, and fallback to full model
when no terms match.
"""

import pytest

from packages.semantic_model.resolver import SemanticResolver


# ── Index / construction ───────────────────────────────────────────────────────

def test_resolver_builds_without_error(minimal_model):
    resolver = SemanticResolver(minimal_model)
    assert resolver.all_metrics()
    assert resolver.all_dimensions()


def test_all_metrics_returns_list(minimal_model):
    resolver = SemanticResolver(minimal_model)
    names = [m["name"] for m in resolver.all_metrics()]
    assert "revenue" in names
    assert "order_count" in names


def test_all_dimensions_returns_list(minimal_model):
    resolver = SemanticResolver(minimal_model)
    names = [d["name"] for d in resolver.all_dimensions()]
    assert "product_category" in names
    assert "order_date" in names


# ── metric_sql ─────────────────────────────────────────────────────────────────

def test_metric_sql_exact_name(minimal_model):
    resolver = SemanticResolver(minimal_model)
    sql = resolver.metric_sql("revenue")
    assert sql is not None
    # revenue has a filter, so should use FILTER(WHERE ...) syntax
    assert "SUM" in sql or "sum" in sql.lower()


def test_metric_sql_with_filter(minimal_model):
    resolver = SemanticResolver(minimal_model)
    sql = resolver.metric_sql("revenue")
    # Should apply the status='completed' filter
    assert "FILTER" in sql and "completed" in sql


def test_metric_sql_unknown_returns_none(minimal_model):
    resolver = SemanticResolver(minimal_model)
    assert resolver.metric_sql("nonexistent_metric") is None


# ── resolve() — term matching ──────────────────────────────────────────────────

def test_resolve_by_metric_name(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("What is revenue last month?")
    metric_names = [m["name"] for m in ctx.relevant_metrics]
    assert "revenue" in metric_names


def test_resolve_by_metric_alias(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("Show me total sales")
    # "sales" is an alias for revenue
    metric_names = [m["name"] for m in ctx.relevant_metrics]
    assert "revenue" in metric_names


def test_resolve_by_dimension_name(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue by product_category")
    dim_names = [d["name"] for d in ctx.relevant_dimensions]
    assert "product_category" in dim_names


def test_resolve_by_dimension_alias(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue by category")
    dim_names = [d["name"] for d in ctx.relevant_dimensions]
    assert "product_category" in dim_names


def test_resolve_synonym_maps_to_metric(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("best selling products")
    # "best selling" is a synonym for metric:revenue
    metric_names = [m["name"] for m in ctx.relevant_metrics]
    assert "revenue" in metric_names


def test_resolve_no_match_returns_full_model(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("completely unrelated phrase xyz")
    # Fallback: returns all metrics and dimensions
    assert len(ctx.relevant_metrics) == len(minimal_model["metrics"])
    assert len(ctx.relevant_dimensions) == len(minimal_model["dimensions"])


# ── resolve() — caveats and business rules ─────────────────────────────────────

def test_resolve_returns_caveats(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue")
    assert ctx.caveats == minimal_model.get("caveats", [])


def test_resolve_returns_business_rules(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue")
    assert ctx.business_rules == minimal_model.get("business_rules", [])


# ── has_matches ────────────────────────────────────────────────────────────────

def test_has_matches_true_when_term_found(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue by category")
    assert ctx.has_matches


def test_has_matches_false_when_no_terms(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("completely unrelated phrase xyz")
    assert not ctx.has_matches


# ── to_prompt_fragment ─────────────────────────────────────────────────────────

def test_prompt_fragment_contains_metric_name(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue")
    fragment = ctx.to_prompt_fragment()
    assert "revenue" in fragment


def test_prompt_fragment_contains_business_rules(minimal_model):
    resolver = SemanticResolver(minimal_model)
    ctx = resolver.resolve("revenue")
    fragment = ctx.to_prompt_fragment()
    # minimal_model has a business rule
    assert "BUSINESS RULES" in fragment or "business_rules" in fragment or "completed" in fragment
