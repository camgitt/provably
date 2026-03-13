"""Pytest fixtures for provably evaluations."""

from __future__ import annotations

import pytest

from provably.compare import CompareResult, compare
from provably.config import load_config
from provably.datasets import Dataset, load_dataset
from provably.providers import get_provider
from provably.result import LLMResult


@pytest.fixture
def provably_config():
    """Load provably configuration."""
    return load_config()


@pytest.fixture
def provably_provider(provably_config):
    """Get a configured LLM provider instance."""
    return get_provider(name=provably_config.get("provider"))


@pytest.fixture
def provably_run(provably_provider, provably_config):
    """Run an LLM completion and return an LLMResult.

    Usage:
        def test_greeting(provably_run):
            result = provably_run("Say hello", model="gpt-4o-mini")
            expect(result).contains("hello")
    """

    def _run(
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> LLMResult:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return provably_provider.complete(
            messages=messages,
            model=model or provably_config.get("model"),
            tools=tools,
            **kwargs,
        )

    return _run


@pytest.fixture
def provably_dataset(request):
    """Load a dataset file and expose it as a ``Dataset`` instance.

    The path to the dataset file must be provided via the ``dataset_path``
    marker or via a ``--dataset`` command-line option::

        @pytest.mark.dataset_path("tests/data/safety.jsonl")
        def test_safety(provably_dataset):
            for case in provably_dataset:
                ...

    The fixture returns a :class:`provably.datasets.Dataset` object.
    """
    marker = request.node.get_closest_marker("dataset_path")
    if marker is not None:
        path = marker.args[0]
    elif hasattr(request, "param"):
        path = request.param
    else:
        path = request.config.getoption("--dataset", default=None)

    if path is None:
        pytest.skip("No dataset path provided (use @pytest.mark.dataset_path)")

    return Dataset.from_file(path)


@pytest.fixture
def provably_compare(provably_config):
    """Compare the same prompt across two models (A vs B testing).

    Usage:
        def test_compare(provably_compare):
            result = provably_compare(
                "Explain gravity",
                model_a="gpt-4o",
                model_b="gpt-4o-mini",
            )
            assert result.result_a.text != ""
    """

    def _compare(
        prompt: str,
        model_a: str,
        model_b: str,
        provider: str | None = None,
        assertions: list | None = None,
        system: str | None = None,
        **kwargs,
    ) -> CompareResult:
        return compare(
            prompt=prompt,
            model_a=model_a,
            model_b=model_b,
            provider=provider or provably_config.get("provider"),
            assertions=assertions,
            system=system,
            **kwargs,
        )

    return _compare
