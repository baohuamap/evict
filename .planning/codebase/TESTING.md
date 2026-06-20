# Testing Patterns

**Analysis Date:** 2026-06-20

## Test Framework

**Runner:**
- pytest (declared `>=7.0.0` in `evict_pipeline/pyproject.toml:24`; installed
  version in the committed venv is **9.0.3**).
- Config: `evict_pipeline/pyproject.toml` is recognized by pytest as the rootdir
  marker (`configfile: pyproject.toml`), but there is **no `[tool.pytest.ini_options]`
  section** — pytest runs with defaults. No `pytest.ini`, `setup.cfg`, or `tox.ini`.
- No `conftest.py` anywhere in the repo (verified by glob). No shared fixtures.

**Assertion Library:**
- Plain `assert` statements (pytest built-ins). No `hamcrest`, `assertpy`, etc.

**Mocking:**
- `unittest.mock.MagicMock` from the stdlib. No `pytest-mock`, no `responses`,
  no `freezegun`, no `mutmut` (`GEMINI.md` explicitly mandates `unittest.mock` to
  simulate LLM and SMT responses — follow this to avoid API cost and environment
  deps in CI).

**Run Commands:**
```bash
# Run all tests (recommended — discovers both test dirs)
pytest evict_pipeline/tests tests

# Run only the package tests (per GEMINI.md)
pytest evict_pipeline/tests

# Run a single test
pytest evict_pipeline/tests/test_pipeline.py::test_pipeline_tp

# Coverage — NOT configured. No pytest-cov installed, no --cov flags used.
# If needed: pip install pytest-cov && pytest --cov=evict_pipeline --cov-report=term
```

There is no watch-mode config (`pytest-watch` not installed) and no Makefile target.

**Verified run output (2026-06-20, venv Python 3.14.6):**
```
platform darwin -- Python 3.14.6, pytest-9.0.3, pluggy-1.6.0
collected 3 items
evict_pipeline/tests/test_pipeline.py::test_pipeline_tp            PASSED
evict_pipeline/tests/test_pipeline.py::test_pipeline_abstain_and_escalate PASSED
tests/test_extractor_codeql.py::test_codeql_parsing                PASSED
3 passed in 12.71s
```

## Test File Organization

**Location:**
- **Two separate test directories** (not co-located with source):
  - `evict_pipeline/tests/` — package tests, run against the installed package via
    `from evict_pipeline import ...`.
  - `tests/` (repo root) — standalone test that bootstraps the path with
    `sys.path.append` and imports `from evict_pipeline.extractor import Extractor`.
- Source lives under `evict_pipeline/src/evict_pipeline/` (src layout). Tests do NOT
  sit next to the modules they test.

**Naming:**
- `test_<module_or_concept>.py`: `test_pipeline.py` (tests `EvictPipeline`),
  `test_extractor_codeql.py` (tests `Extractor` against a CodeQL SARIF).
- Test functions: `test_<behavior>`: `test_pipeline_tp`,
  `test_pipeline_abstain_and_escalate`, `test_codeql_parsing`. No `Test*` classes
  are used — all tests are module-level functions (pytest style, not unittest).

**Structure:**
```
evict_pipeline/
├── tests/
│   └── test_pipeline.py          # 2 tests, EvictPipeline integration with mocks
├── src/evict_pipeline/           # source under test
└── pyproject.toml                # pytest rootdir marker (no [tool.pytest.ini_options])
tests/
├── test_extractor_codeql.py      # 1 test, real Extractor + sample SARIF fixture
└── sample_codeql.sarif           # test fixture (SARIF 2.1.0, single path-traversal result)
```

## Test Structure

**Suite Organization:**
```python
import pytest
from unittest.mock import MagicMock
from evict_pipeline import (
    Alert, Label, Decision, EvidencePack,
    Extractor, Verifier, Calibrator, Escalator, EvictPipeline
)

@pytest.fixture
def mock_pipeline():
    extractor = Extractor()                       # REAL extractor
    verifier = MagicMock(spec=Verifier)           # mocked LLM stage
    calibrator = Calibrator(threshold=0.5)        # REAL calibrator
    escalator = MagicMock(spec=Escalator)         # mocked symbolic stage

    verifier.get_decision.return_value = Decision(
        alert_id="test-1", label=Label.TP, confidence=0.9,
        rationale="LLM reasoning", stage="LLM"
    )
    return EvictPipeline(extractor, verifier, calibrator, escalator)

def test_pipeline_tp(mock_pipeline):
    mock_pipeline.escalator.escalate.side_effect = lambda a, d: d
    alert = Alert(
        alert_id="test-1", cwe_id="CWE-89", description="SQLi",
        file_path="src/main.py", line_number=10, analyzer_name="CodeQL",
        raw_sarif={}
    )
    decision = mock_pipeline.run(alert, project_root=".")
    assert decision.label == Label.TP
    assert decision.confidence == 0.9
    assert decision.stage == "Calibrated"
```
(`evict_pipeline/tests/test_pipeline.py:1-34`)

**Patterns:**
- **Setup:** `@pytest.fixture` returns a wired `EvictPipeline` with the expensive
  stages mocked and the deterministic stages real. This is the canonical setup
  pattern for new pipeline-level tests.
- **Teardown:** None — no yield fixtures, no cleanup. Tests are stateless.
- **Assertion:** Plain `assert decision.label == Label.TP`. No soft asserts, no
  parameterized cases (`pytest.mark.parametrize` is not used anywhere).
- **Stub behavior via `side_effect`:**
  `mock_pipeline.escalator.escalate.side_effect = lambda a, d: d` makes the
  escalator a pass-through (`evict_pipeline/tests/test_pipeline.py:23`). Use
  `side_effect` for stateless stubs and `return_value` for fixed responses.
- **Test the calibration threshold logic by swapping the mock's `return_value`
  between tests** (`test_pipeline_abstain_and_escalate` sets
  `confidence=0.2` to trigger ABSTAIN, then a separate `escalate.return_value`
  with `label=Label.FP, stage="Symbolic"` to simulate symbolic correction —
  `evict_pipeline/tests/test_pipeline.py:36-54`).

## Mocking

**Framework:** `unittest.mock` (stdlib). Specifically `MagicMock`.

**Patterns:**
```python
# Mock an entire class, preserving its spec (attributes/methods exist as MagicMock):
verifier = MagicMock(spec=Verifier)
escalator = MagicMock(spec=Escalator)

# Stub a method's return value:
verifier.get_decision.return_value = Decision(...)

# Stub a method's behavior with a lambda:
mock_pipeline.escalator.escalate.side_effect = lambda a, d: d
```
(`evict_pipeline/tests/test_pipeline.py:11-13`, `:16-18`, `:23`)

**What to Mock:**
- `Verifier` — always mock in pipeline tests. It makes real LLM API calls (OpenAI /
  Anthropic / Gemini) costing money and requiring network + `OPENAI_API_KEY` /
  `GEMINI_API_KEY` / `ANTHROPIC_API_KEY`. `GEMINI.md` mandates this.
- `Escalator` — mock to avoid the Z3 dependency path and the stubbed
  `_solve_smt` "UNKNOWN" behavior.
- Any new stage that calls an external service or a slow solver.

**What NOT to Mock:**
- `Extractor` — uses pure Python SARIF parsing and local file reads; cheap and
  deterministic. The tests use a real `Extractor()`.
- `Calibrator` — pure arithmetic on `Decision.confidence`; trivial and deterministic.
  The tests use a real `Calibrator(threshold=0.5)`.
- `Alert` / `EvidencePack` / `Decision` / `Label` — Pydantic models, no I/O. Always
  instantiate real ones.

**No partial mocking / `patch` is used.** There are no `with mock.patch(...)`
blocks anywhere. If you need to patch a method on a real object, prefer
`MagicMock(spec=Class)` with `return_value` over `patch` — that matches the
existing style.

## Fixtures and Factories

**Test Data:**
- Inline Pydantic construction in the test body:
  ```python
  alert = Alert(
      alert_id="test-1", cwe_id="CWE-89", description="SQLi",
      file_path="src/main.py", line_number=10, analyzer_name="CodeQL",
      raw_sarif={}
  )
  ```
  (`evict_pipeline/tests/test_pipeline.py:24-28`, `:44-48`). No factory functions,
  no builder helpers, no `@pytest.fixture` for `Alert`.

- File-based SARIF fixture: `tests/sample_codeql.sarif` — a 79-line SARIF 2.1.0
  document with one `java/path-traversal` result and a 3-step `codeFlows` trace
  (App.java:10 → Utils.java:25 → App.java:50). Loaded with:
  ```python
  with open(sarif_path, "r") as f:
      sarif_data = json.load(f)
  alerts = extractor.extract_from_sarif(sarif_data)
  ```
  (`tests/test_extractor_codeql.py:13-17`).

**Location:**
- Fixtures live next to the test that uses them: `tests/sample_codeql.sarif` sits
  beside `tests/test_extractor_codeql.py` and is referenced by relative path
  `"tests/sample_codeql.sarif"` (`tests/test_extractor_codeql.py:12`).
- No `tests/fixtures/` or `tests/data/` directory. No shared fixture pool.
- Additional demo SARIF + Java sources exist in `evict_pipeline/demo_data/`
  (`juliet_alerts.sarif`, `JulietCWE22.java`, `JulietCWE78.java`, `JulietCWE89.java`)
  but these are NOT wired into the test suite — they back the manual
  `evict_pipeline/evaluate.py` CLI demo captured in `evict_pipeline/test1.md`.

**Factories:** None. Do not introduce factory functions unless a phase needs many
variants of a model — the project style is inline `Alert(...)` / `Decision(...)`
literals.

## Coverage

**Requirements:** None enforced. No `--cov` flag, no `pytest-cov` in dev deps, no
coverage gate in any CI (there is no CI — see below). GEMINI.md does not mention
coverage targets.

**View Coverage:**
```bash
# Not currently configured. To enable ad-hoc:
pip install pytest-cov
pytest --cov=evict_pipeline --cov-report=term-missing evict_pipeline/tests tests
```

## Test Types

**Unit Tests:**
- Effectively only `test_codeql_parsing` (`tests/test_extractor_codeql.py`) is a
  true unit test — it exercises `Extractor.extract_from_sarif` and
  `Extractor.populate_evidence` against a fixed SARIF and asserts on
  `source_location`, `sink_location`, `flow_path` length and membership
  (`tests/test_extractor_codeql.py:18-31`).

**Integration Tests:**
- `test_pipeline_tp` and `test_pipeline_abstain_and_escalate`
  (`evict_pipeline/tests/test_pipeline.py`) are integration tests: they wire the
  real `Extractor` + real `Calibrator` + mocked `Verifier` + mocked `Escalator`
  through the real `EvictPipeline.run` and assert on the end-to-end `Decision`
  label/stage. This is the highest-fidelity level used.

**E2E Tests:**
- Not used. The closest thing to E2E is the benchmark scripts
  (`scripts/benchmark_juliet_sampling.py`, `scripts/benchmark_cwe_bench.py`,
  `scripts/run_juliet_poc.py`) which run the full pipeline against real SARIF
  datasets and write CSV results to `artifacts/exports/`. These are NOT pytest
  tests and are NOT run in CI; they require API keys and external datasets.

**Regression Tests:** None. No tests assert on specific CWE hints, prompt
structure, or the Z3 escalation path (which is currently a stub returning
`"UNKNOWN"`).

## Common Patterns

**Async Testing:** Not applicable — the pipeline is synchronous throughout. No
`asyncio`, no `pytest-asyncio`.

**Error Testing:**
- No test currently asserts on error/ABSTAIN paths through the real `Verifier`
  (those paths are exercised only via the mocked verifier's `return_value`).
- No test asserts that `Verifier._sample_llm` converts an API exception into an
  `ABSTAIN` vote — this is a coverage gap (see CONCERNS).
- No test asserts that `Escalator.escalate` returns the input decision unchanged
  when `evidence_pack.path_constraints` is empty/None
  (`evict_pipeline/src/evict_pipeline/escalator.py:13-14`).

**Print-debugging in tests:** `test_codeql_parsing` prints
`f"Source: {evidence.source_location}"` etc. and `"Test passed!"`
(`tests/test_extractor_codeql.py:24-32`). pytest captures these by default; they
show with `-s`. New tests should use `assert` only and avoid `print` — the prints
here are a leftover manual-run artifact (the file also has
`if __name__ == "__main__": test_codeql_parsing()` at `:34-35` for running without
pytest).

**Path bootstrap for out-of-package tests:**
```python
sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))
from evict_pipeline.extractor import Extractor
```
(`tests/test_extractor_codeql.py:6-8`). This is the pattern for any new test file
placed in the repo-root `tests/` dir. Prefer placing new tests inside
`evict_pipeline/tests/` with `from evict_pipeline import ...` instead — the path
bootstrap is fragile.

## CI & Automation

**No CI configured.** There is no `.github/workflows/`, no `.gitlab-ci.yml`, no
`.circleci/`, no Jenkinsfile, no `Makefile`, no `tox.ini`. Tests run only locally
or via the bash orchestration scripts in `scripts/` (e.g.
`scripts/run_full_cwe_bench.sh` runs `pytest` indirectly via
`scripts/benchmark_cwe_bench.py`, not as a test suite).

The dev deps (pytest, black, isort, mypy) are declared in
`evict_pipeline/pyproject.toml:22-28` but nothing invokes them automatically.
`GEMINI.md` says tests "should use `unittest.mock` to simulate LLM and SMT solver
responses to avoid API cost and environment dependencies during CI" — implying CI
was planned but never wired up.

**Pre-commit:** No `.pre-commit-config.yaml`. Black/isort/mypy must be run manually.

## Adding New Tests — Where to Put Them

- **Pipeline-level integration test** (exercises `EvictPipeline.run` with mocked
  LLM/escalator): add to `evict_pipeline/tests/test_pipeline.py` using the existing
  `mock_pipeline` fixture as a template.
- **Extractor / SARIF parsing test**: add a new `test_extractor_<analyzer>.py` in
  `evict_pipeline/tests/` with a co-located `sample_<analyzer>.sarif` fixture,
  following `tests/test_extractor_codeql.py` as the template. Use
  `from evict_pipeline import Extractor` (not the `sys.path` hack).
- **Verifier / Calibrator unit test**: add `test_verifier.py` /
  `test_calibrator.py` in `evict_pipeline/tests/`. Mock the LLM client with
  `MagicMock(spec=openai.OpenAI)` (or pass a fake `provider` and stub the client
  attribute) — do NOT make real API calls.
- **Escalator test**: add `test_escalator.py` in `evict_pipeline/tests/`. Test the
  empty-constraints early-return and the SAT/UNSAT/UNKNOWN label mapping by
  monkey-patching `_solve_smt` (real Z3 is not wired up yet).
- **Shared fixtures**: if a fixture is reused across files, create
  `evict_pipeline/tests/conftest.py` (none exists today). Keep fixtures minimal.

---

*Testing analysis: 2026-06-20*
