"""
packages.semantic_model
~~~~~~~~~~~~~~~~~~~~~~~
YAML semantic model format, JSON schema validation, and business-term resolution.

Implemented fully in Phase 3. This stub exports the public interface
so other packages can import against stable names from Phase 1 onward.
"""

__version__ = "0.1.0"


class SemanticModelValidator:
    """Validates a parsed semantic model dict against the JSON schema."""

    def validate(self, model_dict: dict) -> "ValidationResult":
        raise NotImplementedError("Implemented in Phase 3.")


class SemanticResolver:
    """Maps business terms in a question to SQL fragments from a semantic model."""

    def resolve_terms(self, question: str, model: dict) -> list[dict]:
        raise NotImplementedError("Implemented in Phase 3.")

    def to_sql_fragments(self, model: dict) -> list[str]:
        raise NotImplementedError("Implemented in Phase 3.")


class ValidationResult:
    def __init__(self, valid: bool, errors: list[str] | None = None):
        self.valid = valid
        self.errors = errors or []

    def __bool__(self):
        return self.valid
