"""Pytest fixtures for proofagent evaluations."""

from __future__ import annotations

import pytest

from proofagent.compare import CompareResult, compare
from proofagent.config import load_config
from proofagent.datasets import Dataset, load_dataset
from proofagent.providers import get_provider
from proofagent.result import LLMResult


@pytest.fixture
def proofagent_config():
    """Load proofagent configuration."""
    return load_config()


@pytest.fixture
def proofagent_provider(proofagent_config):
    """Get a configured LLM provider instance."""
    return get_provider(name=proofagent_config.get("provider"))


@pytest.fixture
def proofagent_run(proofagent_provider, proofagent_config):
    """Run an LLM completion and return an LLMResult.

    Usage:
        def test_greeting(proofagent_run):
            result = proofagent_run("Say hello", model="gpt-4o-mini")
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

        return proofagent_provider.complete(
            messages=messages,
            model=model or proofagent_config.get("model"),
            tools=tools,
            **kwargs,
        )

    return _run


@pytest.fixture
def proofagent_dataset(request):
    """Load a dataset file and expose it as a ``Dataset`` instance.

    The path to the dataset file must be provided via the ``dataset_path``
    marker or via a ``--dataset`` command-line option::

        @pytest.mark.dataset_path("tests/data/safety.jsonl")
        def test_safety(proofagent_dataset):
            for case in proofagent_dataset:
                ...

    The fixture returns a :class:`proofagent.datasets.Dataset` object.
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
def proofagent_compare(proofagent_config):
    """Compare the same prompt across two models (A vs B testing).

    Usage:
        def test_compare(proofagent_compare):
            result = proofagent_compare(
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
            provider=provider or proofagent_config.get("provider"),
            assertions=assertions,
            system=system,
            **kwargs,
        )

    return _compare
