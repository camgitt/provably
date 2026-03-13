# Provably Launch Copy

---

## 1. Hacker News (Show HN)

**Title:** Show HN: Provably -- Open-source LLM testing in Python (independent Promptfoo alternative)

**Post:**

Promptfoo got acquired by OpenAI. We built the independent alternative. In Python.

Provably is a Python-native LLM testing framework. No YAML configs, no telemetry, no lock-in. Just write tests the way you already write Python.

It ships as a pytest plugin, so it slots into your existing CI pipeline with zero ceremony. Define assertions in plain Python -- semantic similarity, regex, JSON schema, custom validators -- and run them with `pytest`.

Why we built this: after the Promptfoo acquisition, there was no serious independent option for teams that care about eval independence. If the company that makes the model also owns your eval tool, you have a conflict of interest problem. Provably is MIT-licensed, vendor-neutral, and sends nothing home.

Works with OpenAI, Anthropic, local models, or anything with an HTTP endpoint. Install with `pip install provably` and write your first test in under a minute.

GitHub: https://github.com/camgitt/proofagent
PyPI: https://pypi.org/project/provably/

---

## 2. Reddit r/MachineLearning

**Title:** Promptfoo got acquired by OpenAI. We built an independent, Python-native LLM testing framework.

**Body:**

When your eval tooling is owned by a model provider, your benchmarks have a conflict of interest. After the Promptfoo acquisition, we built Provably as the independent alternative -- fully open-source, MIT-licensed, zero telemetry.

Provably is designed for rigorous LLM evaluation in Python. No YAML, no config files, no DSLs. Everything is expressed as plain Python code using a pytest plugin.

Core capabilities:

- 10 built-in assertion types: exact match, contains, regex, JSON schema validation, semantic similarity, cost/latency thresholds, custom Python validators, and more.
- Tool call testing: verify your model selects the right tools with the right arguments, in the right order.
- Trajectory evaluation: test multi-step agent workflows end-to-end, asserting on intermediate reasoning and final outputs.
- Multi-provider support: run the same eval suite against OpenAI, Anthropic, local models, or any custom endpoint. Compare outputs side by side.
- CI-native: runs as a standard pytest plugin. No separate eval server, no dashboard you need to host. Results go to your terminal and your existing test reports.

The architecture is deliberately simple. A test file is a Python file. An assertion is a function call. A provider is a class you can subclass. There is no hidden state and no background network calls.

If you are evaluating LLMs in production or research and want tooling that is not owned by the companies you are evaluating, take a look.

GitHub: https://github.com/camgitt/proofagent
PyPI: https://pypi.org/project/provably/

---

## 3. Reddit r/Python

**Title:** Provably: LLM testing as a pytest plugin -- no YAML, no config files, just Python

**Body:**

We built Provably because every LLM eval tool we found wanted us to write YAML, spin up a server, or install a framework with its own CLI. We just wanted pytest.

Provably is a pytest plugin for testing LLM outputs. Install it with `pip install provably`, write assertion functions in plain Python, and run them with `pytest`. That is the entire workflow.

It supports semantic similarity checks, JSON schema validation, regex matching, cost and latency thresholds, tool call verification, and custom validators -- all as Python function calls. No config files, no DSLs, no telemetry.

Works with any LLM provider. Integrates with your existing CI. Nothing to configure beyond the test file itself.

We built this after Promptfoo was acquired by OpenAI. Provably is independent, MIT-licensed, and will stay that way.

GitHub: https://github.com/camgitt/proofagent
PyPI: https://pypi.org/project/provably/

---

## 4. Twitter/X (3 Drafts)

**Draft 1:**

Promptfoo got acquired by OpenAI. So we built the independent alternative. In Python.

Provably: open-source LLM testing as a pytest plugin. No YAML, no telemetry, no conflict of interest.

pip install provably

https://github.com/camgitt/proofagent

**Draft 2:**

Your LLM eval tool should not be owned by the company whose model you are evaluating.

Provably is an independent, Python-native LLM testing framework. 10 assertion types, tool call testing, multi-provider support. Ships as a pytest plugin.

https://pypi.org/project/provably/

**Draft 3:**

LLM testing should be this simple:

pip install provably
write a Python function
run pytest

No YAML. No config server. No telemetry. Independent and open-source.

https://github.com/camgitt/proofagent
