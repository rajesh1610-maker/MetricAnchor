"""
packages.query_engine
~~~~~~~~~~~~~~~~~~~~~
DuckDB-backed query execution and data profiling.
"""

from .engine import QueryEngine, sanitize_view_name
from .profiler import ColumnProfile, DatasetProfile, profile_dataset

__version__ = "0.2.0"
__all__ = [
    "QueryEngine",
    "sanitize_view_name",
    "ColumnProfile",
    "DatasetProfile",
    "profile_dataset",
]
