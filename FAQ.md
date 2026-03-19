# FAQ

## What is proofagent?

proofagent is a Python testing framework for AI agents and LLM-powered applications. Think of it as pytest for AI — you write assertions against model outputs to verify correctness, safety, cost, and structure.

## How is it different from Promptfoo or DeepEval?

proofagent is pure Python with a pytest-style API. There is no YAML configuration, no external CLI, and no hosted platform required. You write tests in `.py` files and run them with `pytest`. It is designed to fit into existing Python workflows, not replace them.

## Do I need an API key?

Only if you want to call a live model during testing. You can test entirely offline by passing pre-collected outputs into `LLMResult` and running assertions against those. This is useful for CI pipelines and reproducible test suites.

## What AI providers does it support?

OpenAI, Anthropic, Google Gemini, and Ollama are supported out of the box. Any provider that returns text can be tested by wrapping the output in an `LLMResult`.

## Is it free?

Yes. proofagent is free and open source under the MIT license.

## How do I install it?

```
pip install proofagent
```

## How do I write my first test?

```python
from proofagent import expect

def test_greeting():
    result = expect("Say hello").contains("hello")
```

Save this as `test_example.py` and run it with `pytest`.

## How do I run tests?

Run `pytest` in your terminal. proofagent tests are standard pytest tests — all pytest flags, markers, and plugins work as expected.

## How do I see results in a dashboard?

Run `proofagent dashboard` after your test run. This launches a local web UI showing pass/fail rates, latency, cost, and assertion details across all recorded test runs.

## Can I test without an API key?

Yes. Construct an `LLMResult` directly from a string and run assertions against it. This lets you test against saved outputs, synthetic data, or results from any source without making API calls.

```python
from proofagent import LLMResult, expect

result = LLMResult(text="The capital of France is Paris.")
expect(result).contains("Paris")
```

## How do I load test cases from a file?

proofagent supports CSV and JSONL datasets. Load them into your test with `pytest.mark.parametrize` or use the built-in dataset loader to iterate over rows and run assertions against each one.

## How do I compare two models?

Run the same test suite against different models and compare the dashboard output. You can parameterize tests by model name and assert that both meet the same quality, cost, or latency thresholds.

## How do I add custom assertions?

Write a Python function that takes a result and raises `AssertionError` on failure. You can use this directly in your tests or register it as a reusable assertion with `expect().custom("name", your_function)`.

```python
expect(result).custom("short_output", lambda r: len(r.text) < 500)
```

## How do I use it in CI/CD?

Add `pip install proofagent` and `pytest` to your CI pipeline. Tests exit with a non-zero code on failure, so they integrate with GitHub Actions, GitLab CI, and any other CI system that runs shell commands.

## Why should I test my AI agent?

LLM outputs are non-deterministic. Without automated tests, you have no way to catch regressions in quality, safety, or cost after a prompt change, model upgrade, or config update. Testing makes these failures visible before they reach users.

## What is the EU AI Act and why does it matter?

The EU AI Act requires organizations deploying high-risk AI systems to demonstrate testing, monitoring, and risk management. proofagent can help you build a structured testing practice with auditable pass/fail records, but it is not a substitute for a comprehensive compliance program. Consult legal and compliance professionals for your specific obligations.

## Why not just test manually?

Manual testing does not scale. You cannot re-run 200 prompt variations by hand after every change. Automated tests run in seconds, catch regressions immediately, and produce a record you can review later.

## Who is this for?

Developers building applications on top of LLMs — chatbots, RAG pipelines, AI agents, copilots, content generators. If you ship code that calls a model, you should be testing the outputs.

## Who built this?

proofagent is built and maintained by the team at [github.com/camgitt/proofagent](https://github.com/camgitt/proofagent). Contributions are welcome.

## What is on the roadmap?

Active development areas include expanded provider support, richer dashboard analytics, built-in dataset generators, and deeper CI/CD integrations. Check the GitHub repository for the latest updates and open issues.
