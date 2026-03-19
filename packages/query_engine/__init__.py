"""
packages.query_engine
~~~~~~~~~~~~~~~~~~~~~
DuckDB-backed query execution, data profiling, and analytics pipeline.
"""

from .engine import QueryEngine, sanitize_view_name
from .pipeline import execute_pipeline
from .pipeline_types import MappingResult, ParsedIntent, PipelineResult, TermMapping, TimeRange
from .profiler import ColumnProfile, DatasetProfile, profile_dataset

__version__ = "0.3.0"
__all__ = [
    "QueryEngine",
    "sanitize_view_name",
    "ColumnProfile",
    "DatasetProfile",
    "profile_dataset",
    "execute_pipeline",
    "PipelineResult",
    "ParsedIntent",
    "MappingResult",
    "TermMapping",
    "TimeRange",
]
