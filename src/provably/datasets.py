"""Dataset loading utilities for provably evaluations.

Load test cases from CSV or JSONL files and work with them as structured
datasets that can be filtered, sampled, and passed into parametrized tests.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any


def load_dataset(path: str | Path) -> list[dict[str, Any]]:
    """Load test cases from a CSV or JSONL file.

    Each row becomes a dict with at minimum an ``input`` key (the prompt).
    Optional keys include ``expected``, ``tags``, and ``metadata``.

    For CSV files the first row is treated as column headers.
    For JSONL files each line is a JSON object.

    Args:
        path: Path to a ``.csv`` or ``.jsonl`` file.

    Returns:
        A list of dicts, one per test case.

    Raises:
        ValueError: If the file extension is unsupported or a row lacks ``input``.
    """
    path = Path(path)

    if path.suffix == ".csv":
        rows = _load_csv(path)
    elif path.suffix == ".jsonl":
        rows = _load_jsonl(path)
    else:
        raise ValueError(
            f"Unsupported file extension '{path.suffix}'. Use .csv or .jsonl."
        )

    # Normalise each row
    for i, row in enumerate(rows):
        if "input" not in row:
            raise ValueError(f"Row {i} is missing required 'input' field: {row}")

        # Ensure tags is a list
        if "tags" in row and isinstance(row["tags"], str):
            row["tags"] = [t.strip() for t in row["tags"].split(",") if t.strip()]

        # Ensure metadata is a dict
        if "metadata" in row and isinstance(row["metadata"], str):
            try:
                row["metadata"] = json.loads(row["metadata"])
            except json.JSONDecodeError:
                row["metadata"] = {"raw": row["metadata"]}

    return rows


def _load_csv(path: Path) -> list[dict[str, Any]]:
    """Load rows from a CSV file using the first row as headers."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load rows from a JSONL file (one JSON object per line)."""
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_no} of {path}: {exc}"
                ) from exc
            rows.append(obj)
    return rows


class Dataset:
    """A thin wrapper around a list of test-case dicts.

    Provides convenience helpers for filtering and sampling while still
    behaving like a regular sequence (iteration, indexing, ``len``).

    Usage::

        ds = Dataset.from_file("safety_prompts.jsonl")
        subset = ds.filter(tag="injection").sample(n=3)
        for case in subset:
            result = run(case["input"])
    """

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = list(rows)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | Path) -> Dataset:
        """Create a Dataset by loading a CSV or JSONL file."""
        return cls(load_dataset(path))

    # ------------------------------------------------------------------
    # Sequence protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self._rows[index]

    def __iter__(self):
        return iter(self._rows)

    def __repr__(self) -> str:
        return f"Dataset(rows={len(self._rows)})"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def filter(self, tag: str | None = None, **kwargs: Any) -> Dataset:
        """Return a new Dataset containing only matching rows.

        Args:
            tag: If given, keep rows whose ``tags`` list contains this value.
            **kwargs: Arbitrary key/value pairs; a row must match *all* of
                them to be included.
        """
        rows = self._rows

        if tag is not None:
            rows = [r for r in rows if tag in r.get("tags", [])]

        for key, value in kwargs.items():
            rows = [r for r in rows if r.get(key) == value]

        return Dataset(rows)

    def sample(self, n: int, seed: int | None = None) -> Dataset:
        """Return a new Dataset with *n* randomly-sampled rows.

        If *n* >= the number of available rows, returns all rows (shuffled).
        """
        rng = random.Random(seed)
        n = min(n, len(self._rows))
        return Dataset(rng.sample(self._rows, n))

    @property
    def rows(self) -> list[dict[str, Any]]:
        """Return the underlying list of dicts (read-only copy)."""
        return list(self._rows)
