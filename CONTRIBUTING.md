# Contributing to proofagent

We want contributors. Here is everything you need to get started.

## Quick setup

```bash
git clone https://github.com/camgitt/proofagent.git
cd proofagent
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,all]"
pytest
```

That last command should pass. If it does not, open an issue.

## Adding a new assertion

Assertions live in `src/proofagent/expect.py` on the `Expectation` class.

To add one:

1. Add a method to `Expectation`. It receives `self` and whatever parameters make sense.
2. Return `self` so assertions can be chained (e.g., `expect(result).contains("x").is_json()`).
3. Raise `AssertionError` with a clear message on failure.
4. Add a test in `tests/test_expect.py`.

Look at an existing method like `contains` or `matches_regex` for the pattern.

## Adding a new provider

Providers live in `src/proofagent/providers/`. Each one wraps an LLM SDK and returns `LLMResult` objects.

To add one:

1. Create a new file in `src/proofagent/providers/` (e.g., `mistral.py`).
2. Subclass `Provider` from `base.py`.
3. Implement `complete()` and `name()`.
4. Register it in `src/proofagent/providers/__init__.py`.

See `openai.py` or `anthropic.py` for reference implementations.

## Adding a new prompt pack

Prompt packs live in `src/proofagent/packs.py`. A pack is a list of prompts plus metadata.

To add one:

1. Define your prompt list as a module-level constant.
2. Add an entry to the `PACKS` dict with `name`, `description`, `prompts`, and `assertion` keys.

That is it. The CLI and plugin pick up packs from the `PACKS` dict automatically.

## Pull requests

- One feature or fix per PR.
- All tests must pass (`pytest`).
- Add tests for new functionality.
- Keep the diff small. If your change touches many files, consider splitting it.

## Code style

There is no strict formatter enforced. Just keep your code consistent with what is already in the file you are editing. If you are unsure, match the style of the nearest function.

## Questions

Open an issue. We are happy to help.
