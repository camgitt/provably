# Provably vs Promptfoo vs DeepEval -- AI Agent Eval Frameworks Compared (2026)

Choosing an AI evaluation framework matters more than ever. After OpenAI acquired Promptfoo in late 2025, teams relying on it for unbiased LLM testing face a conflict of interest: your eval tool is now owned by the model vendor you are evaluating. This guide compares the three most popular frameworks so you can make an informed decision.

## Feature Comparison

| Feature | Promptfoo | DeepEval | Provably |
|---|---|---|---|
| **Language** | TypeScript | Python | Python |
| **Config format** | YAML + JS | Python + JSON | Python (pure pytest) |
| **Install size** | ~180 MB (node_modules) | ~90 MB (pip) | ~2 MB core (pip) |
| **Agent-native** | Bolted on | Limited | First-class |
| **Tool call testing** | No | No | Yes |
| **Trajectory eval** | No | No | Yes |
| **Cost tracking** | Manual / external | No | Built-in per-assertion |
| **Telemetry** | On by default | Yes | Zero -- no telemetry |
| **Vendor lock-in** | OpenAI-owned since 2025 | No | No |
| **CI/CD gate** | Yes (CLI) | Yes (CLI) | Yes (CLI + pytest exit code) |
| **License** | MIT (pre-acquisition) | Apache 2.0 | MIT |
| **Active development** | Unclear post-acquisition | Active | Active |

## Framework Summaries

### Promptfoo

Promptfoo was the original open-source eval framework, popular for its YAML-driven prompt testing and broad model support. It introduced the concept of running structured test suites against LLM outputs and built a strong community around it. However, OpenAI's acquisition in late 2025 raised questions about neutrality, and development priorities have since shifted toward OpenAI-native integrations. Teams evaluating non-OpenAI models now report that Promptfoo's maintenance of third-party providers has slowed.

### DeepEval

DeepEval is a Python-native framework with a focus on metric-driven evaluation, offering built-in metrics like G-Eval, faithfulness, and answer relevancy. It integrates well with LangChain and LlamaIndex, making it a solid choice for RAG pipeline testing. Its weaknesses include a lack of first-class agent and tool-call testing, an opinionated metric system that can be difficult to customize, and default telemetry that requires explicit opt-out.

### Provably

Provably takes the approach that LLM evals should work like regular software tests. It is a pytest plugin with 10 chainable assertions, built-in cost and latency tracking, and first-class support for agent tool calls and multi-step trajectories. The tradeoff is that it is newer and has a smaller ecosystem -- there is no hosted dashboard yet, and the dataset loader and model comparison features are still on the roadmap. Its zero-telemetry, zero-config philosophy appeals to teams that want full control.

## When to Use Each

**Choose Promptfoo if:**
- Your stack is TypeScript/Node.js end to end
- You are already invested in the OpenAI ecosystem and comfortable with vendor alignment
- You need YAML-based prompt test suites that non-engineers can edit

**Choose DeepEval if:**
- You are building RAG pipelines with LangChain or LlamaIndex
- You need research-grade metrics (G-Eval, faithfulness, hallucination scoring)
- You prefer a metric-centric approach over assertion-centric testing

**Choose Provably if:**
- You are building AI agents with tool use and multi-step workflows
- You want evals to live alongside your existing pytest suite
- You need cost tracking and CI/CD gating without external services
- You want zero telemetry and no vendor lock-in

## Migrating from Promptfoo

If you are moving from Promptfoo to Provably, here is what the transition looks like.

**1. Replace YAML config with Python tests**

Before (Promptfoo `promptfooconfig.yaml`):
```yaml
prompts:
  - "Answer the question: {{question}}"
providers:
  - openai:gpt-4o-mini
tests:
  - vars:
      question: "What is 2+2?"
    assert:
      - type: contains
        value: "4"
```

After (Provably `test_math.py`):
```python
from provably import expect

def test_math(provably_run):
    result = provably_run("What is 2+2?", model="gpt-4o-mini")
    expect(result).contains("4")
```

**2. Replace JavaScript assertion functions with chainable expects**

Before (Promptfoo custom assertion):
```javascript
module.exports = (output) => {
  const parsed = JSON.parse(output);
  return parsed.score > 0.8 && output.includes("success");
};
```

After (Provably):
```python
from provably import expect

def test_json_output(provably_run):
    result = provably_run("Rate this response", model="gpt-4o-mini")
    expect(result).contains("success").valid_json()
```

**3. Replace cost tracking scripts with built-in assertions**

Before (Promptfoo -- manual cost check in CI):
```bash
promptfoo eval && node scripts/check_costs.js --max 1.00
```

After (Provably -- cost is a first-class assertion):
```python
def test_cost(provably_run):
    result = provably_run("Summarize this", model="gpt-4o-mini")
    expect(result).total_cost_under(0.01)
```

**4. Replace CLI eval with pytest**

Before:
```bash
npx promptfoo eval
```

After:
```bash
pip install provably
pytest tests/ -v
provably gate --min-score 0.85 --block-on-fail
```

## Links

- GitHub: [https://github.com/camgitt/provably](https://github.com/camgitt/provably)
- PyPI: [https://pypi.org/project/provably/](https://pypi.org/project/provably/)
- Install: `pip install provably`
