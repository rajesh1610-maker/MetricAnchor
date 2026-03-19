"""
packages.shared
~~~~~~~~~~~~~~~
Common types, exceptions, and utilities shared across all packages.
"""

__version__ = "0.1.0"


class MetricAnchorError(Exception):
    """Base exception for all MetricAnchor errors."""


class UploadError(MetricAnchorError):
    """Raised when a file upload fails validation."""


class QueryError(MetricAnchorError):
    """Raised when SQL execution fails."""


class LLMError(MetricAnchorError):
    """Raised when the LLM call fails or returns unparseable output."""


class SemanticModelError(MetricAnchorError):
    """Raised when a semantic model fails validation."""


class DatasetNotFoundError(MetricAnchorError):
    """Raised when a referenced dataset does not exist."""
