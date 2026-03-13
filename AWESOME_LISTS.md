# Awesome List Submissions for Provably

Repo: https://github.com/camgitt/provably

---

## 1. awesome-python (vinta/awesome-python)

- **List name**: awesome-python
- **Repo URL**: https://github.com/vinta/awesome-python
- **Section**: Testing > Testing Frameworks
- **Entry**:
  ```
  - [provably](https://github.com/camgitt/provably) - A pytest-based evaluation framework for testing AI agents with 10 assertion types.
  ```
- **Notes**:
  - Submit as a single-project PR. Do not bundle with other submissions.
  - Project must be >50% Python, >1 month old, active in the past year, and well-documented.
  - Acceptance paths: "Industry Standard" (dominant tool), "Rising Star" (5000+ stars in <2 years), or "Hidden Gem" (100-500 stars, 6+ months old, solves a specialized problem). Hidden Gem is the most realistic path; requires documented real-world usage.
  - Projects with <100 stars are auto-rejected unless submitted as Hidden Gem with justification.
  - Archived repos or repos <3 months old are auto-rejected.
  - Read full rules: https://github.com/vinta/awesome-python/blob/master/CONTRIBUTING.md

---

## 2. Awesome-LLM (Hannibal046/Awesome-LLM)

- **List name**: Awesome-LLM
- **Repo URL**: https://github.com/Hannibal046/Awesome-LLM
- **Section**: LLM Evaluation (closest fit; there is no dedicated "Tools" section -- tools are spread across topical sections)
- **Entry**:
  ```
  - [provably](https://github.com/camgitt/provably) - A pytest plugin for evaluating LLM agents with chainable assertions, multi-provider support, and CI/CD gating.
  ```
- **Notes**:
  - The repo says "your contributions are always welcome" via PR.
  - Some PRs are kept open for community voting (thumbs-up reactions).
  - No strict star threshold mentioned. Keep the description concise and one line.

---

## 3. awesome-generative-ai-guide (aishwaryanr/awesome-generative-ai-guide)

- **List name**: awesome-generative-ai-guide
- **Repo URL**: https://github.com/aishwaryanr/awesome-generative-ai-guide
- **Section**: Free Courses > Evaluation (under the course/resource listings)
- **Entry**:
  ```
  [provably: pytest for AI agents](https://github.com/camgitt/provably) - Open-source evaluation framework with 10 assertion types, multi-provider support, and CI/CD quality gates
  ```
- **Notes**:
  - This list is structured as a learning guide, not a pure tool list. Entries are courses, tutorials, and resources.
  - Provably fits best under the Evaluation subsection or as a tool reference. The "Top AI Tools List" section links to a separate file for tools.
  - Check the tools sub-page at `free_courses/` or linked tool documents for the exact insertion point.
  - No formal contributing guidelines found; submit a PR with a brief rationale.

---

## 4. awesome-ai-agents (e2b-dev/awesome-ai-agents)

- **List name**: awesome-ai-agents
- **Repo URL**: https://github.com/e2b-dev/awesome-ai-agents (26k+ stars, most popular "awesome-ai-agents" list)
- **Section**: Open-source projects (alphabetical order)
- **Entry**:
  ```markdown
  ## [provably](https://github.com/camgitt/provably)
  pytest for AI agents -- test your agents, prove they work, block bad deploys

  <details>

  ### Category
  Developer tools, Testing

  ### Description
  - Open-source evaluation framework for AI agents with 10 chainable assertion types
  - pytest plugin that makes testing LLM outputs as simple as testing regular code
  - Supports OpenAI, Anthropic, and Ollama providers out of the box
  - CI/CD quality gate to block deploys that fail evaluation
  - Tool call testing and multi-step trajectory evaluation
  - Zero telemetry, no YAML, no vendor lock-in

  ### Links
  - [GitHub](https://github.com/camgitt/provably)
  - [PyPI](https://pypi.org/project/provably/)
  </details>
  ```
- **Notes**:
  - Entries must be in alphabetical order within their section.
  - Also fill out their submission form: https://forms.gle/UXQFCogLYrPFvfoUA
  - SDKs and frameworks may be redirected to their sibling list "Awesome SDKs for AI Agents" instead. Provably is an eval/testing tool (not an SDK), so it should qualify for the main list.
  - The list focuses on AI agents themselves; position provably as a tool that validates agents rather than a framework for building them.
