"""Provably — pytest for AI agents.

Evaluate, test, and certify AI agents with cryptographic compliance proofs.

Usage:
    from provably import expect, LLMResult

    result = LLMResult(text="Hello!")
    expect(result).contains("Hello")
"""

from provably.__version__ import __version__
from provably.compare import CompareResult, compare, compare_batch
from provably.datasets import Dataset, load_dataset
from provably.expect import Expectation, expect, register_assertion
from provably.result import LLMResult, ToolCall, TrajectoryStep

__all__ = [
    "__version__",
    "compare",
    "compare_batch",
    "CompareResult",
    "Dataset",
    "expect",
    "Expectation",
    "load_dataset",
    "register_assertion",
    "LLMResult",
    "ToolCall",
    "TrajectoryStep",
]
