# Contributing to Provably

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/camgitt/proofagent.git
cd provably
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,all]"
```

## Run tests

```bash
pytest tests/ -v
pytest examples/ -v -k "not live"
```

## Adding assertions

New assertions go in `src/provably/expect.py` as methods on the `Expectation` class. Every assertion should:

1. Return `self` for chaining
2. Raise `AssertionError` with a clear message on failure
3. Have a corresponding test in `tests/test_expect.py`

## Adding providers

New providers go in `src/provably/providers/`. Implement the `Provider` base class from `base.py` and register in `__init__.py`.

## Pull requests

- Keep PRs focused on a single change
- Add tests for new features
- All tests must pass
