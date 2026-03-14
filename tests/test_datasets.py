"""Tests for dataset loading and the Dataset class."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from proofagent.datasets import Dataset, load_dataset


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(tmp_path: str, content: str) -> str:
    path = os.path.join(tmp_path, "data.csv")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _write_jsonl(tmp_path: str, rows: list[dict]) -> str:
    path = os.path.join(tmp_path, "data.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return path


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

class TestCSVLoading:
    def test_basic_csv(self, tmp_path):
        path = _write_csv(str(tmp_path), "input,expected\nHello,World\nFoo,Bar\n")
        rows = load_dataset(path)
        assert len(rows) == 2
        assert rows[0]["input"] == "Hello"
        assert rows[0]["expected"] == "World"
        assert rows[1]["input"] == "Foo"

    def test_csv_with_tags(self, tmp_path):
        path = _write_csv(
            str(tmp_path), "input,expected,tags\nPrompt,Answer,\"safety,math\"\n"
        )
        rows = load_dataset(path)
        assert rows[0]["tags"] == ["safety", "math"]

    def test_csv_missing_input_raises(self, tmp_path):
        path = _write_csv(str(tmp_path), "prompt,expected\nHello,World\n")
        with pytest.raises(ValueError, match="missing required 'input' field"):
            load_dataset(path)

    def test_example_math_csv(self):
        """Verify the bundled math example loads correctly."""
        example = os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "datasets",
            "math_prompts.csv",
        )
        rows = load_dataset(example)
        assert len(rows) == 5
        assert all("input" in r for r in rows)


# ---------------------------------------------------------------------------
# JSONL loading
# ---------------------------------------------------------------------------

class TestJSONLLoading:
    def test_basic_jsonl(self, tmp_path):
        rows_in = [
            {"input": "Say hi", "expected": "hi"},
            {"input": "Say bye", "expected": "bye"},
        ]
        path = _write_jsonl(str(tmp_path), rows_in)
        rows = load_dataset(path)
        assert len(rows) == 2
        assert rows[0]["input"] == "Say hi"

    def test_jsonl_with_tags_list(self, tmp_path):
        rows_in = [{"input": "test", "tags": ["a", "b"]}]
        path = _write_jsonl(str(tmp_path), rows_in)
        rows = load_dataset(path)
        assert rows[0]["tags"] == ["a", "b"]

    def test_jsonl_skips_blank_lines(self, tmp_path):
        path = os.path.join(str(tmp_path), "data.jsonl")
        with open(path, "w") as f:
            f.write('{"input": "one"}\n\n{"input": "two"}\n')
        rows = load_dataset(path)
        assert len(rows) == 2

    def test_jsonl_invalid_json_raises(self, tmp_path):
        path = os.path.join(str(tmp_path), "bad.jsonl")
        with open(path, "w") as f:
            f.write("not json\n")
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_dataset(path)

    def test_example_safety_jsonl(self):
        """Verify the bundled safety example loads correctly."""
        example = os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "datasets",
            "safety_prompts.jsonl",
        )
        rows = load_dataset(example)
        assert len(rows) == 5
        assert all("input" in r for r in rows)


# ---------------------------------------------------------------------------
# Unsupported extension
# ---------------------------------------------------------------------------

def test_unsupported_extension(tmp_path):
    path = os.path.join(str(tmp_path), "data.txt")
    with open(path, "w") as f:
        f.write("hello")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        load_dataset(path)


# ---------------------------------------------------------------------------
# Dataset class
# ---------------------------------------------------------------------------

class TestDataset:
    @pytest.fixture()
    def sample_ds(self, tmp_path):
        rows = [
            {"input": "p1", "tags": ["safety", "math"]},
            {"input": "p2", "tags": ["safety"]},
            {"input": "p3", "tags": ["math"]},
            {"input": "p4", "tags": []},
        ]
        path = _write_jsonl(str(tmp_path), rows)
        return Dataset.from_file(path)

    def test_len(self, sample_ds):
        assert len(sample_ds) == 4

    def test_iter(self, sample_ds):
        items = list(sample_ds)
        assert len(items) == 4

    def test_getitem(self, sample_ds):
        assert sample_ds[0]["input"] == "p1"

    def test_filter_by_tag(self, sample_ds):
        safety = sample_ds.filter(tag="safety")
        assert len(safety) == 2
        assert all("safety" in r["tags"] for r in safety)

    def test_filter_by_tag_no_match(self, sample_ds):
        result = sample_ds.filter(tag="nonexistent")
        assert len(result) == 0

    def test_filter_by_kwarg(self, sample_ds):
        result = sample_ds.filter(input="p3")
        assert len(result) == 1
        assert result[0]["input"] == "p3"

    def test_sample(self, sample_ds):
        sampled = sample_ds.sample(n=2, seed=42)
        assert len(sampled) == 2

    def test_sample_larger_than_dataset(self, sample_ds):
        sampled = sample_ds.sample(n=100, seed=42)
        assert len(sampled) == 4

    def test_sample_deterministic(self, sample_ds):
        a = sample_ds.sample(n=2, seed=7)
        b = sample_ds.sample(n=2, seed=7)
        assert list(a) == list(b)

    def test_repr(self, sample_ds):
        assert "Dataset(rows=4)" in repr(sample_ds)

    def test_rows_property(self, sample_ds):
        rows = sample_ds.rows
        assert isinstance(rows, list)
        assert len(rows) == 4
        # Verify it is a copy
        rows.pop()
        assert len(sample_ds) == 4
