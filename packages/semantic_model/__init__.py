"""
packages.semantic_model
~~~~~~~~~~~~~~~~~~~~~~~
YAML semantic model format, JSON schema validation, and business-term resolution.
"""

from .resolver import ResolvedContext, SemanticResolver, TermMapping
from .validator import SemanticModelValidator, ValidationResult

__version__ = "0.3.0"
__all__ = [
    "SemanticModelValidator",
    "ValidationResult",
    "SemanticResolver",
    "ResolvedContext",
    "TermMapping",
]
