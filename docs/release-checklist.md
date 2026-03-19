# Release Checklist

Use this checklist for every versioned release of MetricAnchor.

---

## Pre-release (feature freeze)

### Code quality

- [ ] All tests pass on `main`: `make test`
- [ ] No linter warnings: `make lint`
- [ ] No TODO or FIXME comments in user-facing code paths
- [ ] No hardcoded API keys, credentials, or debug flags left in
- [ ] `API_DEBUG=false` is the documented default for production

### Test coverage

- [ ] `make test-coverage` passes with no regressions from the prior release
- [ ] All eval cases pass: `apps/api/.venv/bin/python3 -m pytest evals/test_evals.py -v`
- [ ] Live eval suite passes (requires running stack): `pytest tests/test_demo_questions.py -v`
- [ ] Playwright smoke tests pass: `make test-e2e`

### Sample data

- [ ] `make generate-data` produces the expected row counts (774 / 256 / 320)
- [ ] `make seed` completes without error against a clean database
- [ ] All three demo datasets produce correct answers for the 13 eval cases

### Semantic models

- [ ] `make validate` passes for all models in `examples/`
- [ ] Example questions in each `examples/*/README.md` still return correct answers

---

## Documentation

- [ ] `CHANGELOG.md` — `[Unreleased]` section promoted to the new version with today's date
- [ ] `README.md` — roadmap table updated; version badges current
- [ ] `docs/architecture.md` — reflects current component structure
- [ ] `docs/api.md` — all new or changed endpoints documented
- [ ] `docs/local-development.md` — setup instructions tested on a clean machine
- [ ] `apps/api/.env.example` — all new env vars documented with defaults
- [ ] OpenAPI docs up to date: start the API and check `http://localhost:8000/api/docs`

---

## Docker and deployment

- [ ] `docker compose build` succeeds from a clean checkout
- [ ] `docker compose up -d && make health` returns `{"status": "ok"}`
- [ ] `make seed` succeeds against the freshly built containers
- [ ] Container images have no known high-severity CVEs (`docker scout quickview`)
- [ ] `docker compose down -v && docker compose up -d` (restart from scratch) works

---

## GitHub release

- [ ] All commits since the last release are squashed or clearly described
- [ ] Release branch or tag created: `git tag -a v<version> -m "v<version>"`
- [ ] GitHub Release draft created with:
  - [ ] Tag: `v<version>`
  - [ ] Target: `main`
  - [ ] Title: `MetricAnchor v<version>`
  - [ ] Body: changelog entries for this version (copy from `CHANGELOG.md`)
  - [ ] "Set as latest release" checked (unless pre-release)
- [ ] CI passes on the tagged commit

---

## Post-release

- [ ] `CHANGELOG.md` — new `[Unreleased]` section added at the top
- [ ] Milestone closed on GitHub; next milestone created
- [ ] Any `good first issue` or `help wanted` labels applied to issues appropriate for new contributors
- [ ] Release announced in GitHub Discussions (optional but encouraged)

---

## Version number guide

MetricAnchor follows [Semantic Versioning](https://semver.org/):

| Change type | Version bump | Example |
|---|---|---|
| Breaking API or semantic model format change | Major | `1.0.0` → `2.0.0` |
| New feature, backwards-compatible | Minor | `1.0.0` → `1.1.0` |
| Bug fix, backwards-compatible | Patch | `1.0.0` → `1.0.1` |
| Pre-release or RC | Pre-release suffix | `1.1.0-rc.1` |

**Breaking changes** in MetricAnchor means:
- A semantic model YAML field is removed or renamed
- An API response shape changes in a non-additive way
- A CLI command or flag is removed or renamed
- A required environment variable is added or renamed
