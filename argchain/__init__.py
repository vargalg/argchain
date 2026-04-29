"""
argchain - Chain Python operations together

A library for composing operations that flow data through a pipeline,
where each operation receives a dictionary of keyword arguments and
produces a dictionary as output for the next operation in the chain.
"""

from .pipeline import Pipeline, CallGraph
from .decorators import operation

__version__ = "0.1.0"
__all__ = ["Pipeline", "CallGraph", "operation"]
