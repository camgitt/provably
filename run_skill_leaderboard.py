"""Run skill evaluations against real models to populate the skill leaderboard.

Usage: python3 run_skill_leaderboard.py
Requires API keys as environment variables:
  - ANTHROPIC_API_KEY (for Anthropic models)
  - OPENAI_API_KEY (for OpenAI models)
  - GEMINI_API_KEY (for Gemini models)

Models without a valid API key will be skipped gracefully.
"""

import json
import sys
import traceback

from proofagent.skills import run_skill_report, save_skill_report, SKILL_PACKS

# ---------------------------------------------------------------------------
# Models to evaluate
# ---------------------------------------------------------------------------

MODELS = [
    ("claude-sonnet-4-6", "anthropic"),
    ("claude-haiku-4-5", "anthropic"),
    ("gpt-4.1-mini", "openai"),
    ("gemini-2.5-flash", "gemini"),
]

SKILLS = ["coding", "reasoning", "math", "writing", "summarization"]


def main():
    all_results = []
    all_entries = []

    print("=" * 60)
    print("  Skill Leaderboard Runner")
    print(f"  Testing {len(MODELS)} models across {len(SKILLS)} skills")
    print("=" * 60)

    for model, provider in MODELS:
        print(f"\n{'─' * 50}")
        print(f"  Testing: {model} (provider: {provider})")
        print(f"{'─' * 50}")

        try:
            report = run_skill_report(
                model=model,
                skills=SKILLS,
                provider=provider,
            )
        except Exception as e:
            err_msg = str(e)
            # Detect missing API key errors
            if "API" in err_msg.upper() or "KEY" in err_msg.upper() or "AUTH" in err_msg.upper():
                print(f"  SKIPPED: Missing or invalid API key for {provider}")
                print(f"           {err_msg}")
            else:
                print(f"  ERROR: {err_msg}")
                traceback.print_exc()
            continue

        # Save the report
        try:
            output_path = save_skill_report(report)
            print(f"  Saved: {output_path}")
        except Exception as e:
            print(f"  Warning: Could not save report file: {e}")

        # Print summary
        print(f"\n  Model: {model}")
        print(f"  {'Skill':<18} {'Score':>8}  {'Grade':>6}")
        print(f"  {'─' * 34}")

        skill_scores = {}
        for proof in report.proofs:
            avg = round(proof.avg_score, 1)
            skill_scores[proof.skill] = avg
            print(f"  {proof.skill_name:<18} {avg:>6.1f}/10  {proof.grade:>6}")

        overall = round(report.overall_score, 1)
        print(f"\n  Overall: {overall}/10 -- Grade: {report.overall_grade}")
        print(f"  Fingerprint: {report.fingerprint}")

        # Build result dict
        result_dict = report.to_dict()
        result_dict["fingerprint"] = report.fingerprint
        all_results.append(result_dict)

        # Build JS entry
        entry = {
            "model": model,
            "coding": skill_scores.get("coding", 0),
            "reasoning": skill_scores.get("reasoning", 0),
            "math": skill_scores.get("math", 0),
            "writing": skill_scores.get("writing", 0),
            "summarization": skill_scores.get("summarization", 0),
            "verified": False,
            "fingerprint": report.fingerprint,
        }
        all_entries.append(entry)

    if not all_entries:
        print("\n  No models were successfully tested. Check your API keys.")
        sys.exit(1)

    # Save all results to JSON
    with open("skill_leaderboard_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved detailed results to skill_leaderboard_results.json")

    # Output JavaScript array for skills.html
    print("\n\n=== PASTE INTO site/skills.html ===\n")
    print("const entries = [")
    for entry in all_entries:
        parts = [
            f"model: '{entry['model']}'",
            f"coding: {entry['coding']}",
            f"reasoning: {entry['reasoning']}",
            f"math: {entry['math']}",
            f"writing: {entry['writing']}",
            f"summarization: {entry['summarization']}",
            f"verified: false",
            f"fingerprint: '{entry['fingerprint']}'",
        ]
        print(f"  {{ {', '.join(parts)} }},")
    print("];")


if __name__ == "__main__":
    main()
