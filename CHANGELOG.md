# Changelog

All notable changes to MetricAnchor are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Phase 1: Repository scaffold — Docker, CI, Makefile, community files, package structure
- Phase 0: Product specification, personas, and roadmap docs

---

## [0.1.0] - Planned

### Added
- File upload for CSV and Parquet via REST API and web UI
- Schema profiler: column types, null rates, distinct counts, sample values
- DuckDB registration of uploaded datasets
- Dataset list and detail endpoints
- CLI: `metricanchor upload`

---

## [0.2.0] - Planned

### Added
- YAML semantic model format with JSON schema validation
- CLI: `metricanchor validate`
- Basic metric editor in the web UI
- Business term resolver

---

## [0.3.0] - Planned

### Added
- Natural language Q&A against uploaded datasets
- Provider-agnostic LLM adapter (OpenAI, Anthropic, OpenAI-compatible)
- Trust output: SQL, term mappings, assumptions, confidence level
- Question history and feedback endpoint

---

## [1.0.0] - Planned

### Added
- Full UI: charts, developer view, feedback flow, question history
- Playwright end-to-end smoke tests
- Complete documentation and CONTRIBUTING guide
- v1.0 release with three demo datasets and semantic models
