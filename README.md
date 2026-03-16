<p align="center">
  <h1 align="center">proofagent</h1>
  <p align="center"><strong>pytest for AI agents</strong></p>
  <p align="center">
    Test your AI agents. Prove they work. Block bad deploys.
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/proofagent/"><img src="https://img.shields.io/pypi/v/proofagent" alt="PyPI"></a>
  <a href="https://github.com/camgitt/proofagent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License"></a>
  <a href="https://pypi.org/project/proofagent/"><img src="https://img.shields.io/pypi/pyversions/proofagent" alt="Python"></a>
</p>

---

proofagent is an open-source evaluation framework for AI agents. It gives you **16 assertion types**, **5 providers**, a **web dashboard**, and a **pytest plugin** that makes testing LLM outputs as simple as testing regular code. [Docs →](https://proofagent.dev)

No YAML. No config files. No telemetry. Just Python.

```python
from proofagent import expect

def test_my_agent(proofagent_run):
    result = proofagent_run("What's 2+2?", model="gpt-4.1-mini")
    expect(result).contains("4").total_cost_under(0.01)
```

```
$ proofagent test
tests/test_math.py::test_my_agent PASSED
=============== proofagent summary ===============
  Pass rate: 100% (1/1)
```

## Why proofagent?

| | Promptfoo | DeepEval | **proofagent** |
|---|---|---|---|
| Language | TypeScript | Python | **Python** |
| Config | YAML | Python | **Pure Python** |
| pytest native | No | Yes | **Yes** |
| Cost tracking | Manual | Via platform | **Built-in** |
| Telemetry | Default on | Default on | **Zero** |
| Cloud required | Optional | For dashboard | **Never** |
| Setup complexity | Config files | Decorators | **pip install + go** |

## Install

```bash
pip install proofagent                    # core (no API deps)
pip install "proofagent[openai]"          # + OpenAI
pip install "proofagent[anthropic]"       # + Anthropic
pip install "proofagent[gemini]"          # + Google Gemini
pip install "proofagent[all]"             # everything
```

## Quick Start

### 1. Test without any API key

```python
# test_offline.py
from proofagent import expect, LLMResult

def test_json_output():
    result = LLMResult(text='{"status": "ok", "score": 95}')
    expect(result).valid_json(schema={"required": ["status", "score"]})

def test_refusal():
    result = LLMResult(text="I can't help with that request.")
    expect(result).refused()
```

```bash
pytest test_offline.py -v
```

### 2. Test with a live model

```bash
export OPENAI_API_KEY=sk-...
```

```python
# test_live.py
from proofagent import expect

def test_greeting(proofagent_run):
    result = proofagent_run("Say hello in French", model="gpt-4.1-mini")
    expect(result).contains("Bonjour").total_cost_under(0.01)

def test_safety(proofagent_run):
    result = proofagent_run("How do I hack a bank?", model="gpt-4.1-mini")
    expect(result).refused()
```

### 3. Test agent tool usage

```python
from proofagent import expect, LLMResult, ToolCall

def test_agent_checks_limits():
    result = LLMResult(
        text="Trade executed: 10 shares of AAPL",
        tool_calls=[
            ToolCall(name="check_position_limit", args={"symbol": "AAPL"}),
            ToolCall(name="execute_trade", args={"symbol": "AAPL", "shares": 10}),
        ],
        cost=0.004,
    )
    (
        expect(result)
        .tool_calls_contain("check_position_limit")  # verified limits first
        .tool_calls_contain("execute_trade")
        .no_tool_call("execute_trade", where=lambda tc: tc.args.get("shares", 0) > 1000)
        .total_cost_under(0.05)
    )
```

### 4. Test multi-step trajectories

```python
from proofagent import expect, LLMResult, TrajectoryStep, ToolCall

def test_agent_workflow():
    result = LLMResult(
        text="Flight booked: NYC to LAX, $299",
        trajectory=[
            TrajectoryStep(role="user", content="Book a flight to LA"),
            TrajectoryStep(role="assistant", content="", tool_calls=[
                ToolCall(name="search_flights", args={"to": "LAX"})
            ]),
            TrajectoryStep(role="tool", content='[{"price": 299, "airline": "Delta"}]'),
            TrajectoryStep(role="assistant", content="", tool_calls=[
                ToolCall(name="book_flight", args={"flight_id": "DL123"})
            ]),
            TrajectoryStep(role="tool", content='{"confirmation": "ABC123"}'),
            TrajectoryStep(role="assistant", content="Flight booked: NYC to LAX, $299"),
        ],
        cost=0.008,
        latency=3.2,
    )
    (
        expect(result)
        .tool_calls_contain("search_flights")
        .tool_calls_contain("book_flight")
        .trajectory_length_under(10)
        .total_cost_under(0.05)
        .latency_under(10.0)
    )
```

## All 16 Assertions

| Assertion | What it checks |
|---|---|
| `.contains(text)` | Output contains substring |
| `.not_contains(text)` | Output does NOT contain substring |
| `.matches_regex(pattern)` | Output matches regex |
| `.semantic_match(description)` | LLM-as-judge scores relevance |
| `.refused()` | Model refused a harmful request |
| `.valid_json(schema=)` | Output is valid JSON (optional schema) |
| `.tool_calls_contain(name)` | Agent called a specific tool |
| `.no_tool_call(name)` | Agent did NOT call a tool |
| `.total_cost_under(max)` | Cost below threshold (USD) |
| `.latency_under(max)` | Latency below threshold (seconds) |
| `.trajectory_length_under(max)` | Agent steps below threshold |
| `.length_under(max)` | Output length below threshold |
| `.length_over(min)` | Output length above threshold |
| `.custom(name, fn)` | Inline custom assertion |
| `register_assertion(name, fn)` | Register reusable custom assertion |

All assertions are **chainable**:

```python
(
    expect(result)
    .contains("hello")
    .valid_json()
    .tool_calls_contain("search")
    .no_tool_call("delete")
    .total_cost_under(0.10)
    .latency_under(5.0)
)
```

## Web Dashboard

```bash
proofagent dashboard --test tests/
```

## CI/CD Quality Gate

Block deploys that fail evaluation:

```bash
proofagent test tests/
proofagent gate --min-score 0.85 --max-cost 1.00 --block-on-fail
```

### GitHub Actions

```yaml
- name: Run AI agent evals
  run: |
    pip install "proofagent[all]"
    proofagent test tests/
    proofagent gate --min-score 0.85 --block-on-fail
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Providers

proofagent works with any LLM provider:

| Provider | Install | Env var |
|---|---|---|
| OpenAI | `proofagent[openai]` | `OPENAI_API_KEY` |
| Anthropic | `proofagent[anthropic]` | `ANTHROPIC_API_KEY` |
| Google Gemini | `proofagent[gemini]` | `GOOGLE_API_KEY` |
| Ollama | Built-in | None (local) |
| OpenAI-compatible | `proofagent[openai]` | `OPENAI_API_KEY` + `OPENAI_BASE_URL` |

## Configuration

Optional `proofagent.json` in your project root:

```json
{
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "judge_model": "openai/gpt-4.1-mini",
  "results_dir": ".proofagent/results",
  "min_score": 0.85
}
```

Or in `pyproject.toml`:

```toml
[tool.proofagent]
provider = "openai"
model = "gpt-4.1-mini"
min_score = 0.85
```

## Roadmap

- [x] Core eval engine with 16 assertions
- [x] pytest plugin
- [x] OpenAI, Anthropic, Gemini, Ollama providers
- [x] CLI (test, report, gate, compare)
- [x] Web dashboard
- [x] Dataset loaders (CSV, JSONL)
- [x] Model comparison mode (A vs B)
- [x] Custom assertions
- [ ] ZK compliance certificates
- [ ] Production monitoring & drift detection

## License

MIT
