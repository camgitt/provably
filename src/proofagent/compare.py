"""Model comparison (A vs B testing) for evaluating LLM outputs side by side.

Usage:
    from proofagent import compare, CompareResult

    result = compare("Explain gravity", model_a="gpt-4o", model_b="claude-sonnet-4-20250514")
    print(result.winner)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from proofagent.providers import get_provider
from proofagent.result import LLMResult


@dataclass
class CompareResult:
    """Side-by-side results from running the same prompt on two models."""

    model_a: str
    model_b: str
    result_a: LLMResult
    result_b: LLMResult
    winner: str | None = None
    assertion_results: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "model_a": self.model_a,
            "model_b": self.model_b,
            "result_a": self.result_a.to_dict(),
            "result_b": self.result_b.to_dict(),
            "winner": self.winner,
            "assertion_results": self.assertion_results,
        }


def compare(
    prompt: str,
    model_a: str,
    model_b: str,
    provider: str | None = None,
    provider_a: str | None = None,
    provider_b: str | None = None,
    assertions: list[Callable[[LLMResult], bool]] | None = None,
    system: str | None = None,
    **kwargs,
) -> CompareResult:
    """Run the same prompt on two models and compare results.

    Args:
        prompt: The user prompt to send to both models.
        model_a: First model identifier.
        model_b: Second model identifier.
        provider: Provider name used for both models (auto-detected if None).
        provider_a: Provider name for model_a (overrides provider).
        provider_b: Provider name for model_b (overrides provider).
        assertions: Optional list of assertion functions. Each takes an LLMResult
                    and returns True if the assertion passes, False otherwise.
        system: Optional system message.
        **kwargs: Additional keyword arguments passed to provider.complete().

    Returns:
        A CompareResult with both outputs and an optional winner.
    """
    llm_a = get_provider(name=provider_a or provider)
    llm_b = get_provider(name=provider_b or provider)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    result_a = llm_a.complete(messages=messages, model=model_a, **kwargs)
    result_b = llm_b.complete(messages=messages, model=model_b, **kwargs)

    winner = None
    assertion_results: dict = {"a": {}, "b": {}}

    if assertions:
        a_pass = 0
        b_pass = 0
        for i, assertion_fn in enumerate(assertions):
            name = getattr(assertion_fn, "__name__", f"assertion_{i}")
            try:
                a_ok = bool(assertion_fn(result_a))
            except Exception:
                a_ok = False
            try:
                b_ok = bool(assertion_fn(result_b))
            except Exception:
                b_ok = False

            assertion_results["a"][name] = a_ok
            assertion_results["b"][name] = b_ok
            a_pass += int(a_ok)
            b_pass += int(b_ok)

        if a_pass > b_pass:
            winner = model_a
        elif b_pass > a_pass:
            winner = model_b

    return CompareResult(
        model_a=model_a,
        model_b=model_b,
        result_a=result_a,
        result_b=result_b,
        winner=winner,
        assertion_results=assertion_results,
    )


def compare_batch(
    prompts: list[str],
    model_a: str,
    model_b: str,
    provider: str | None = None,
    assertions: list[Callable[[LLMResult], bool]] | None = None,
    system: str | None = None,
    **kwargs,
) -> list[CompareResult]:
    """Run multiple prompts on two models and compare results for each.

    Args:
        prompts: List of user prompts to evaluate.
        model_a: First model identifier.
        model_b: Second model identifier.
        provider: Provider name (auto-detected if None).
        assertions: Optional list of assertion functions.
        system: Optional system message.
        **kwargs: Additional keyword arguments passed to provider.complete().

    Returns:
        A list of CompareResult objects, one per prompt.
    """
    return [
        compare(
            prompt=prompt,
            model_a=model_a,
            model_b=model_b,
            provider=provider,
            assertions=assertions,
            system=system,
            **kwargs,
        )
        for prompt in prompts
    ]
