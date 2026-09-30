# Tech decisions (final, do not re-litigate)

- Python 3.11, 3.12, 3.13. Source layout: src/spanchor.
- Build: hatchling. Env/deps: uv. License: Apache-2.0.
- Models: frozen, slotted stdlib dataclasses with explicit validators (dependency-light).
  Every serialized file carries `schema_version`.
- CLI: Typer + Rich. Tests: pytest + Hypothesis + coverage (target >= 90% on core).
- Lint/type: ruff, mypy --strict on src. pre-commit.
- Runtime deps: typer, rich only (numpy allowed for bootstrap in the `stats` extra).
  Optional extras: stats, langchain, llamaindex, annotation.
- Span math uses sorted-interval merging (O(n log n)); never per-character sets.
- All offsets are Unicode code-point offsets into CANONICAL text
  (NFC + \r\n and \r -> \n). Half-open intervals [start, end).
- Errors are typed (InvalidSchemaError, DocumentNotFoundError, HashMismatchError,
  AnchorResolutionError, OrphanedAnchorError, InvalidRetrievalResultError,
  EvaluationError, ComparisonError) and every message includes what happened,
  the values involved, and a suggested action.
- Exit codes: 0 pass, 1 regression policy failed, 2 usage/schema error, 3 unmapped-rate
  threshold exceeded.
