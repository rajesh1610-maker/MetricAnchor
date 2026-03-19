"""Shared dataclasses for the query pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParsedIntent:
    """Structured intent extracted from a natural language question."""

    raw_question: str
    question_type: str  # metric_lookup | breakdown | trend | comparison | ranking
    candidate_terms: list[str]
    time_expression: str | None
    explicit_group_by: list[str]
    limit: int | None
    sort_direction: str  # asc | desc


@dataclass
class TimeRange:
    """A resolved date range with a human-readable assumption note."""

    start: str  # ISO date YYYY-MM-DD (inclusive)
    end: str  # ISO date YYYY-MM-DD (exclusive)
    label: str  # e.g. "last month"
    assumption: str  # e.g. "Interpreted 'last month' as 2026-02-01 to 2026-02-28"


@dataclass
class TermMapping:
    """A single resolved business term."""

    phrase: str  # what the user said (or the term name)
    resolved_name: str  # canonical model name
    resolved_type: str  # metric | dimension | entity
    resolved_to: str  # metric:revenue | dimension:product_category
    via: str  # exact | alias | synonym | default
    confidence: float  # 0.0 to 1.0


@dataclass
class MappingResult:
    """Result of mapping a parsed intent to semantic model concepts."""

    resolved_metrics: list[TermMapping]
    resolved_dimensions: list[TermMapping]
    unmapped: list[str]
    assumptions: list[str]
    overall_confidence: float
    needs_clarification: bool
    clarifying_question: str | None


@dataclass
class PipelineResult:
    """Full output of the analytics pipeline — everything shown to the user."""

    question: str
    answer: str
    sql: str
    columns: list[str]
    rows: list[list]
    row_count: int
    chart_type: str
    semantic_mappings: list[dict]
    assumptions: list[str]
    caveats: list[str]
    confidence: str  # high | medium | low | clarification_needed
    confidence_note: str
    clarifying_question: str | None
    provenance: dict
    execution_ms: int
    error: str | None = None

    @classmethod
    def clarification(
        cls,
        question: str,
        clarifying_question: str,
        provenance: dict,
    ) -> PipelineResult:
        return cls(
            question=question,
            answer="",
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            chart_type="none",
            semantic_mappings=[],
            assumptions=[],
            caveats=[],
            confidence="clarification_needed",
            confidence_note="The question is ambiguous. Please clarify.",
            clarifying_question=clarifying_question,
            provenance=provenance,
            execution_ms=0,
            error=None,
        )

    @classmethod
    def error(  # noqa: F811
        cls,
        question: str,
        error: str,
        sql: str = "",
        provenance: dict | None = None,
    ) -> PipelineResult:
        return cls(
            question=question,
            answer="",
            sql=sql,
            columns=[],
            rows=[],
            row_count=0,
            chart_type="none",
            semantic_mappings=[],
            assumptions=[],
            caveats=[],
            confidence="low",
            confidence_note="An error occurred during query processing.",
            clarifying_question=None,
            provenance=provenance or {},
            execution_ms=0,
            error=error,
        )

    @classmethod
    def no_model(cls, dataset_name: str) -> PipelineResult:
        return cls(
            question="",
            answer="",
            sql="",
            columns=[],
            rows=[],
            row_count=0,
            chart_type="none",
            semantic_mappings=[],
            assumptions=[],
            caveats=[],
            confidence="low",
            confidence_note="No semantic model defined for this dataset.",
            clarifying_question=None,
            provenance={},
            execution_ms=0,
            error=(
                f"No semantic model found for dataset '{dataset_name}'. "
                "Create one at /semantic-models/new before asking questions."
            ),
        )
