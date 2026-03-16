# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in proofagent, please report it responsibly by opening a **private security advisory** on GitHub:

https://github.com/camgitt/proofagent/security/advisories/new

Do not open a public issue for security vulnerabilities. We will acknowledge your report within 48 hours and work with you to understand and address the issue.

## Data Handling

proofagent is designed with a strict no-transmission architecture:

- **No data is transmitted through proofagent.** All API calls go directly from the user's machine to the provider. proofagent never acts as an intermediary or proxy for your data.
- **API keys are never logged or stored by proofagent.** Keys are used in-memory for the duration of a session and are not written to disk, logs, or any external service.

## Supported Versions

Security updates are applied to the latest release only. We recommend always running the most recent version.

## Scope

This policy covers the proofagent package and its official distribution channels. Third-party forks or modifications are outside the scope of this policy.
