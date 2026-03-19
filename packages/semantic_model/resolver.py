"""
Semantic term resolver.

Maps natural language phrases in a user question to concrete SQL
fragments defined in a semantic model. Used by Phase 4's Q&A engine
to ground LLM prompts against the semantic model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TermMapping:
    """A single resolved term found in a user question."""

    term: str
    type: str  # metric | dimension | entity | synonym
    definition: str
    sql_fragment: str
    filters_applied: list[str] = field(default_factory=list)
    caveat: str | None = None


@dataclass
class ResolvedContext:
    """Full resolution result for a question against a semantic model."""

    term_mappings: list[TermMapping]
    relevant_metrics: list[dict]
    relevant_dimensions: list[dict]
    caveats: list[str]
    business_rules: list[dict]

    @property
    def has_matches(self) -> bool:
        return bool(self.term_mappings)

    def to_prompt_fragment(self) -> str:
        """Format this context as a plain-English block for LLM prompts."""
        lines: list[str] = []

        if self.relevant_metrics:
            lines.append("DEFINED METRICS (use these exact SQL expressions):")
            for m in self.relevant_metrics:
                expr = _metric_to_sql(m)
                desc = m.get("description", m["expression"])
                lines.append(f"  - {m['name']}: {expr}")
                lines.append(f"    Definition: {desc}")
                if m.get("aliases"):
                    lines.append(f"    Also called: {', '.join(m['aliases'])}")

        if self.relevant_dimensions:
            lines.append("\nDEFINED DIMENSIONS (use these column names for GROUP BY / filters):")
            for d in self.relevant_dimensions:
                lines.append(f"  - {d['name']} → column: {d['column']}")
                if d.get("values"):
                    lines.append(f"    Known values: {', '.join(str(v) for v in d['values'][:10])}")

        if self.business_rules:
            lines.append("\nBUSINESS RULES (always apply these WHERE conditions):")
            for rule in self.business_rules:
                lines.append(f"  - {rule['name']}: {rule['filter']}")

        if self.caveats:
            lines.append("\nCAVEATS (include in your response):")
            for c in self.caveats:
                lines.append(f"  - {c}")

        return "\n".join(lines)


class SemanticResolver:
    """Resolves business terms in a user question against a semantic model."""

    def __init__(self, model: dict) -> None:
        self._model = model
        self._metric_idx: dict[str, dict] = {}
        self._dimension_idx: dict[str, dict] = {}
        self._entity_idx: dict[str, dict] = {}
        self._build_index()

    # ── Public API ─────────────────────────────────────────────────────────────

    def resolve(self, question: str) -> ResolvedContext:
        """Resolve all business terms found in the question."""
        q = question.lower()
        term_mappings: list[TermMapping] = []
        seen_metrics: dict[str, dict] = {}
        seen_dimensions: dict[str, dict] = {}

        # Match metrics
        for phrase, metric in self._metric_idx.items():
            if phrase in q:
                name = metric["name"]
                if name not in seen_metrics:
                    seen_metrics[name] = metric
                    term_mappings.append(
                        TermMapping(
                            term=phrase,
                            type="metric",
                            definition=metric.get("description", metric["expression"]),
                            sql_fragment=_metric_to_sql(metric),
                            filters_applied=_filter_descriptions(metric.get("filters", [])),
                        )
                    )

        # Match dimensions
        for phrase, dim in self._dimension_idx.items():
            if phrase in q:
                name = dim["name"]
                if name not in seen_dimensions:
                    seen_dimensions[name] = dim
                    term_mappings.append(
                        TermMapping(
                            term=phrase,
                            type="dimension",
                            definition=dim.get("description", dim["column"]),
                            sql_fragment=dim["column"],
                        )
                    )

        # If nothing matched, return all metrics and dimensions as context
        # so the LLM has the full model to work with
        if not seen_metrics and not seen_dimensions:
            seen_metrics = {m["name"]: m for m in self._model.get("metrics", [])}
            seen_dimensions = {d["name"]: d for d in self._model.get("dimensions", [])}

        return ResolvedContext(
            term_mappings=term_mappings,
            relevant_metrics=list(seen_metrics.values()),
            relevant_dimensions=list(seen_dimensions.values()),
            caveats=self._model.get("caveats", []),
            business_rules=self._model.get("business_rules", []),
        )

    def all_metrics(self) -> list[dict]:
        return self._model.get("metrics", [])

    def all_dimensions(self) -> list[dict]:
        return self._model.get("dimensions", [])

    def metric_sql(self, metric_name: str) -> str | None:
        metric = next(
            (m for m in self._model.get("metrics", []) if m["name"] == metric_name),
            None,
        )
        return _metric_to_sql(metric) if metric else None

    # ── Index building ─────────────────────────────────────────────────────────

    def _build_index(self) -> None:
        for metric in self._model.get("metrics", []):
            self._metric_idx[metric["name"].lower()] = metric
            for alias in metric.get("aliases", []):
                self._metric_idx[alias.lower()] = metric

        for dim in self._model.get("dimensions", []):
            self._dimension_idx[dim["name"].lower()] = dim
            for alias in dim.get("aliases", []):
                self._dimension_idx[alias.lower()] = dim

        for entity in self._model.get("entities", []):
            self._entity_idx[entity["name"].lower()] = entity
            for alias in entity.get("aliases", []):
                self._entity_idx[alias.lower()] = entity

        # Synonym overrides
        for syn in self._model.get("synonyms", []):
            phrase = syn["phrase"].lower()
            maps_to: str = syn["maps_to"]

            if maps_to.startswith("metric:"):
                target = maps_to[7:]
                match = next(
                    (m for m in self._model.get("metrics", []) if m["name"] == target),
                    None,
                )
                if match:
                    self._metric_idx[phrase] = match

            elif maps_to.startswith("dimension:"):
                target = maps_to[10:]
                match = next(
                    (d for d in self._model.get("dimensions", []) if d["name"] == target),
                    None,
                )
                if match:
                    self._dimension_idx[phrase] = match


# ── Helpers ────────────────────────────────────────────────────────────────────


def _metric_to_sql(metric: dict) -> str:
    """
    Convert a metric definition to a SQL expression with filters applied.

    Uses DuckDB's FILTER (WHERE ...) aggregate syntax, which is ANSI-compatible
    and produces correct results even when multiple metrics share the same table.
    """
    expr = metric["expression"]
    filters = metric.get("filters", [])
    if not filters:
        return expr

    conditions = _filters_to_sql(filters)
    return f"{expr} FILTER(WHERE {conditions})"


def _filters_to_sql(filters: list[dict]) -> str:
    parts = []
    for f in filters:
        col = f["column"]
        op = f["operator"]
        val = f.get("value")

        if op in ("IS NULL", "IS NOT NULL"):
            parts.append(f"{col} {op}")
        elif op in ("IN", "NOT IN"):
            if isinstance(val, list):
                quoted = ", ".join(f"'{v}'" if isinstance(v, str) else str(v) for v in val)
            else:
                quoted = f"'{val}'"
            parts.append(f"{col} {op} ({quoted})")
        elif isinstance(val, str):
            parts.append(f"{col} {op} '{val}'")
        else:
            parts.append(f"{col} {op} {val}")

    return " AND ".join(parts)


def _filter_descriptions(filters: list[dict]) -> list[str]:
    return [f"{f['column']} {f['operator']} {f.get('value', '')}" for f in filters]
