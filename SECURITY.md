# Security Policy

## Supported Versions

MetricAnchor is pre-1.0. Security fixes are applied to the `main` branch only.

| Version | Supported |
|---|---|
| main (pre-release) | Yes |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues by opening a GitHub issue with the title prefixed `[security]` and marked as **confidential** (GitHub private vulnerability reporting). If you are unsure how to use private reporting, email the maintainer address listed in the repository's GitHub profile.

Include:
- A description of the vulnerability
- Steps to reproduce it
- Your assessment of impact and severity
- Any suggested mitigations

You can expect an initial response within 72 hours and a resolution timeline within 14 days for confirmed issues.

## Security Design Notes

MetricAnchor is designed local-first with the following defaults:

- **No data exfiltration:** Uploaded files are stored only on the local filesystem. They are not sent to any external service unless you configure an external LLM provider.
- **LLM data handling:** When using an external LLM (OpenAI, Anthropic), the schema profile and semantic model definitions are included in prompts. Raw row data is never sent to the LLM by default. Configure `LLM_SEND_SAMPLE_ROWS=false` to confirm this.
- **Read-only query execution:** The query engine runs all user-generated SQL in read-only mode against DuckDB. It cannot write to, modify, or delete source files.
- **No authentication in V1:** MetricAnchor V1 is designed for local, single-user use. Do not expose the API port publicly without adding an authentication layer.
- **SQL injection prevention:** User questions are sent to the LLM as natural language. The LLM generates SQL, which is then validated and executed in a sandboxed DuckDB context. Direct SQL input from users is not supported or executed.

## Out of Scope

The following are known limitations, not vulnerabilities, in V1:

- No RBAC or multi-user isolation
- No TLS between services in the default Docker setup
- No rate limiting on the API
