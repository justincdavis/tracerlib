"""
Library for tracing module calls in Python.

Classes
-------
TraceEntry
    Dataclass for a trace entry.
Trace
    Type alias for a list of trace entries.
TracedModule
    Context manager for tracing module calls in Python.
"""
from __future__ import annotations

from ._tracedmodule import TracedModule
from ._types import Trace, TraceEntry

__version__ = "0.0.0"

__all__ = [
    "TracedModule",
    "TraceEntry",
    "Trace",
]
