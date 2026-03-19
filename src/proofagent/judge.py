"""LLM-as-judge for semantic and skill evaluation."""

from __future__ import annotations

import json
import re

from proofagent.providers import get_provider

_SKILL_JUDGE_PROMPT = """You are a skill evaluator grading an AI agent's output against a rubric.

RUBRIC (what a good answer looks like):
{rubric}

AI OUTPUT:
{output}

Grade the output on a scale of 0 to 10:
- 10: Exceptional — exceeds rubric, flawless
- 8-9: Strong — meets all criteria with minor imperfections
- 6-7: Competent — meets most criteria, some gaps
- 4-5: Partial — addresses the task but misses key criteria
- 2-3: Weak — attempt is present but significantly wrong or incomplete
- 0-1: Failed — wrong, off-topic, or no meaningful attempt

Respond with ONLY a JSON object: {{"score": <integer 0-10>, "reason": "<brief explanation>"}}"""

_JUDGE_PROMPT = """You are an evaluation judge. Score how well the AI output matches the given description.

Description: {description}

AI Output:
{output}

Respond with ONLY a JSON object: {{"score": <float between 0.0 and 1.0>, "reason": "<brief explanation>"}}

Scoring guide:
- 1.0: Perfect match — output fully satisfies the description
- 0.7-0.9: Good match — mostly satisfies with minor gaps
- 0.4-0.6: Partial match — some relevant content but significant gaps
- 0.1-0.3: Poor match — barely related
- 0.0: No match — completely unrelated or contradictory"""


def evaluate_semantic_match(
    output: str,
    description: str,
    model: str = "openai/gpt-4o-mini",
) -> float:
    """Use an LLM to score semantic similarity between output and description.

    Args:
        output: The AI-generated text to evaluate.
        description: What the output should convey.
        model: Judge model in "provider/model" format.

    Returns:
        Float score between 0.0 and 1.0.
    """
    # Parse provider/model format
    if "/" in model:
        provider_name, model_name = model.split("/", 1)
    else:
        provider_name = None
        model_name = model

    provider = get_provider(provider_name)

    prompt = _JUDGE_PROMPT.format(
        description=description,
        output=output[:2000],  # truncate to avoid excessive cost
    )

    result = provider.complete(
        messages=[{"role": "user", "content": prompt}],
        model=model_name,
        temperature=0,
    )

    # Parse score from response
    try:
        text = result.text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return float(data.get("score", 0.0))
    except (json.JSONDecodeError, ValueError, TypeError):
        # Try to extract a number
        match = re.search(r'"score"\s*:\s*([\d.]+)', result.text)
        if match:
            return float(match.group(1))
        return 0.0


def evaluate_skill_score(
    output: str,
    rubric: str,
    model: str = "openai/gpt-4o-mini",
) -> tuple[int, str]:
    """Use an LLM judge to score an output against a skill rubric.

    Args:
        output: The AI-generated text to evaluate.
        rubric: Description of what a good answer looks like.
        model: Judge model in "provider/model" format.

    Returns:
        Tuple of (score: int 0-10, reason: str).
    """
    if "/" in model:
        provider_name, model_name = model.split("/", 1)
    else:
        provider_name = None
        model_name = model

    provider = get_provider(provider_name)

    prompt = _SKILL_JUDGE_PROMPT.format(
        rubric=rubric,
        output=output[:3000],
    )

    result = provider.complete(
        messages=[{"role": "user", "content": prompt}],
        model=model_name,
        temperature=0,
    )

    try:
        text = result.text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        score = int(data.get("score", 0))
        score = max(0, min(10, score))
        reason = data.get("reason", "")
        return score, reason
    except (json.JSONDecodeError, ValueError, TypeError):
        match = re.search(r'"score"\s*:\s*(\d+)', result.text)
        if match:
            return max(0, min(10, int(match.group(1)))), ""
        return 0, "Could not parse judge response"
