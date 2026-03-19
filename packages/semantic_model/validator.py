"""
Semantic model validator.

Validates a YAML or dict semantic model against the JSON schema
and runs additional structural checks that JSON schema can't express.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

_SCHEMA_PATH = Path(__file__).parent / "schema.json"


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


class SemanticModelValidator:
    """Validates semantic models against the JSON schema plus semantic rules."""

    def __init__(self) -> None:
        with _SCHEMA_PATH.open() as f:
            self._schema = json.load(f)
        self._validator = jsonschema.Draft202012Validator(self._schema)

    # ── Public API ─────────────────────────────────────────────────────────────

    def validate(self, model: dict) -> ValidationResult:
        """Validate a parsed model dict. Returns a ValidationResult."""
        errors: list[str] = []
        warnings: list[str] = []

        # JSON schema validation
        for error in self._validator.iter_errors(model):
            path = " → ".join(str(p) for p in error.absolute_path)
            location = f" (at {path})" if path else ""
            errors.append(f"{error.message}{location}")

        if errors:
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # Additional semantic checks
        errors.extend(self._check_no_duplicate_names(model))
        errors.extend(self._check_synonym_targets(model))
        errors.extend(self._check_metric_names_safe(model))
        warnings.extend(self._check_descriptions_present(model))
        warnings.extend(self._check_aliases_present(model))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_file(self, path: str) -> ValidationResult:
        """Load a YAML file and validate it."""
        try:
            with open(path) as f:
                model = yaml.safe_load(f)
        except FileNotFoundError:
            return ValidationResult(valid=False, errors=[f"File not found: {path}"])
        except yaml.YAMLError as e:
            return ValidationResult(valid=False, errors=[f"YAML parse error: {e}"])

        if not isinstance(model, dict):
            return ValidationResult(
                valid=False, errors=["Model must be a YAML mapping at the top level."]
            )

        return self.validate(model)

    # ── Semantic checks ────────────────────────────────────────────────────────

    def _check_no_duplicate_names(self, model: dict) -> list[str]:
        errors = []
        metric_names = [m["name"] for m in model.get("metrics", [])]
        dimension_names = [d["name"] for d in model.get("dimensions", [])]

        dups = _duplicates(metric_names)
        if dups:
            errors.append(f"Duplicate metric names: {', '.join(dups)}")

        dups = _duplicates(dimension_names)
        if dups:
            errors.append(f"Duplicate dimension names: {', '.join(dups)}")

        overlap = set(metric_names) & set(dimension_names)
        if overlap:
            errors.append(f"Names appear in both metrics and dimensions: {', '.join(overlap)}")

        return errors

    def _check_synonym_targets(self, model: dict) -> list[str]:
        errors = []
        metric_names = {m["name"] for m in model.get("metrics", [])}
        dimension_names = {d["name"] for d in model.get("dimensions", [])}
        entity_names = {e["name"] for e in model.get("entities", [])}

        for syn in model.get("synonyms", []):
            maps_to: str = syn.get("maps_to", "")
            if maps_to.startswith("metric:"):
                target = maps_to[7:]
                if target not in metric_names:
                    errors.append(f"Synonym '{syn['phrase']}' maps to unknown metric '{target}'.")
            elif maps_to.startswith("dimension:"):
                target = maps_to[10:]
                if target not in dimension_names:
                    errors.append(
                        f"Synonym '{syn['phrase']}' maps to unknown dimension '{target}'."
                    )
            elif maps_to.startswith("entity:"):
                target = maps_to[7:]
                if target not in entity_names:
                    errors.append(f"Synonym '{syn['phrase']}' maps to unknown entity '{target}'.")
            else:
                errors.append(
                    f"Synonym '{syn['phrase']}' has invalid maps_to format '{maps_to}'. "
                    "Use metric:<name>, dimension:<name>, or entity:<name>."
                )

        return errors

    def _check_metric_names_safe(self, model: dict) -> list[str]:
        errors = []
        for metric in model.get("metrics", []):
            name = metric.get("name", "")
            if not name.isidentifier():
                errors.append(
                    f"Metric name '{name}' is not a valid SQL identifier. "
                    "Use lowercase letters, numbers, and underscores only."
                )
        return errors

    def _check_descriptions_present(self, model: dict) -> list[str]:
        warnings = []
        for metric in model.get("metrics", []):
            if not metric.get("description"):
                warnings.append(
                    f"Metric '{metric['name']}' has no description. "
                    "Descriptions appear in trust output — add one for better user experience."
                )
        return warnings

    def _check_aliases_present(self, model: dict) -> list[str]:
        warnings = []
        for metric in model.get("metrics", []):
            if not metric.get("aliases"):
                warnings.append(
                    f"Metric '{metric['name']}' has no aliases. "
                    "Add common synonyms so users can ask about it naturally."
                )
        return warnings


# ── Helpers ────────────────────────────────────────────────────────────────────


def _duplicates(names: list[str]) -> list[str]:
    seen: set[str] = set()
    dups: list[str] = []
    for n in names:
        if n in seen:
            dups.append(n)
        seen.add(n)
    return dups


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m packages.semantic_model.validator <file.yml>")
        sys.exit(1)

    validator = SemanticModelValidator()
    result = validator.validate_file(sys.argv[1])

    if result.valid:
        print(f"  {sys.argv[1]}")
        for w in result.warnings:
            print(f"  warning: {w}")
    else:
        print(f"  {sys.argv[1]}")
        for e in result.errors:
            print(f"  error: {e}")
        for w in result.warnings:
            print(f"  warning: {w}")
        sys.exit(1)
