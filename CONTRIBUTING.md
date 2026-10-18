# Contributing to SPANCHOR

Thank you for your interest in contributing to SPANCHOR! This document provides guidelines for setting up a development environment, running tests, and submitting pull requests.

## Development Setup

### Prerequisites

- Python 3.11 or newer (tested on 3.11, 3.12, 3.13)
- Git

### Clone and Install

```bash
git clone https://github.com/Mukeshram-07/spanchor.git
cd spanchor
pip install -e ".[dev]"
```

This installs SPANCHOR in editable mode with all development dependencies (testing, type checking, linting).

## Running Tests

### All Tests

```bash
pytest
```

Run the complete test suite with coverage:

```bash
pytest --cov=spanchor
```

### Specific Tests

Run tests in a specific file:

```bash
pytest tests/unit/test_recall.py
```

Run tests matching a pattern:

```bash
pytest -k "test_recall" -v
```

Skip slow tests (property-based testing with Hypothesis):

```bash
pytest -m "not slow"
```

## Code Quality

All code must pass these checks before being merged.

### Formatting

```bash
ruff format src/spanchor tests
```

Check formatting without modifying:

```bash
ruff format --check src/spanchor tests
```

### Linting

```bash
ruff check src/spanchor
```

### Type Checking

```bash
mypy --strict src/spanchor
```

The project uses `mypy --strict` mode. All functions must have type hints.

### All Checks Together

```bash
# Format
ruff format src/spanchor tests

# Lint
ruff check src/spanchor

# Type check
mypy --strict src/spanchor

# Test
pytest
```

## Code Style Guide

### Type Hints

All public functions require type hints:

```python
def evaluate(
    documents: dict[str, Document],
    queries: list[Query],
    results: dict[str, list[RetrievalResult]],
    k: int = 5,
) -> Run:
    """Evaluate retrieval results against gold anchors."""
```

### Docstrings

Use Google-style docstrings for public APIs:

```python
def locate_text(
    search_text: str,
    documents: dict[str, Document],
) -> list[LocateMatch]:
    """Search for text in canonical documents.

    Args:
        search_text: Text to search for
        documents: Mapping of document_id to Document objects

    Returns:
        List of LocateMatch objects with offsets and context

    Raises:
        ValueError: If search_text is empty
    """
```

### Line Length

Maximum 100 characters per line (configured in `pyproject.toml`).

### Imports

Imports are organized and sorted by `isort` (configured in ruff). The tool runs automatically during formatting.

## Adding Features

### 1. Write Tests First

Add tests in `tests/unit/` for your feature. Use the existing test structure as reference.

```python
class TestMyFeature:
    """Tests for my_feature function."""

    def test_basic_usage(self) -> None:
        """Test basic usage."""
        # Arrange
        # Act
        # Assert
```

### 2. Implement the Feature

Add implementation in the appropriate module under `src/spanchor/`.

### 3. Verify Tests Pass

```bash
pytest tests/unit/test_my_feature.py -v
```

### 4. Run Full Quality Checks

```bash
ruff format src/spanchor tests
ruff check src/spanchor
mypy --strict src/spanchor
pytest
```

### 5. Update Documentation

Update README.md, docstrings, or examples as needed.

## Adding Adapters

Additional framework adapters are welcome as optional dependencies.

### Pattern

1. Create `src/spanchor/adapters/myframework.py`
2. Add optional dependency to `pyproject.toml`
3. Create tests in `tests/unit/test_adapters_myframework.py`
4. Update `src/spanchor/adapters/__init__.py` exports
5. Add example usage in README

### Requirements

- Must not make the dependency mandatory for core SPANCHOR
- Must follow the RetrievalResult conversion pattern
- Must be type-hinted with mypy --strict compliance
- Must include comprehensive tests

## Pull Request Process

### Before Submitting

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run all quality checks (see above)
5. Commit with clear messages: `git commit -m "Add my feature"`

### PR Requirements

- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] `mypy --strict` passes
- [ ] `ruff format` passes
- [ ] `ruff check` passes
- [ ] Docstrings added for public APIs
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] No breaking changes to existing APIs

### Commit Messages

Use clear, descriptive commit messages:

```
Fix Recall@K calculation for overlapping spans

- Handle overlapping spans correctly in interval algebra
- Add 8 test cases for overlapping scenarios
- Update documentation with examples
```

NOT:

```
fix bug
update stuff
```

### Review Process

- PRs are reviewed for correctness, performance, and fit with the project
- Type safety (mypy --strict) is non-negotiable
- Tests are required for all functionality
- Documentation updates are expected

## Architecture Guidelines

### Core Principles

- **Deterministic**: All operations are reproducible with same inputs
- **Local-first**: No external APIs or network requirements (unless adapter)
- **Type-safe**: Full mypy --strict compliance
- **Minimal deps**: Core library dependencies are minimal (typer, rich only)

### Module Organization

- `src/spanchor/models/` - Data models (Anchor, Document, etc.)
- `src/spanchor/evaluation/` - Metrics (Recall, Precision, etc.)
- `src/spanchor/comparison/` - Regression detection
- `src/spanchor/mapping/` - Chunk-to-span mapping
- `src/spanchor/annotation/` - Gold-set tooling
- `src/spanchor/adapters/` - Framework integrations
- `src/spanchor/canonical/` - Canonicalization (hashing, normalization)
- `src/spanchor/storage/` - Serialization (JSON, JSONL)
- `src/spanchor/reporting/` - Report generation

### When to Add Dependencies

- Core: Only if widely needed and actively maintained
- Optional: Any well-maintained framework (configure in pyproject.toml)
- Dev: Testing, linting, type checking, building

## Testing Best Practices

### Unit Tests

Test individual functions in isolation:

```python
def test_recall_perfect_coverage() -> None:
    """Perfect recall when retrieved fully covers gold."""
    gold = [(0, 10)]
    retrieved = [(0, 10)]
    assert recall_at_k(gold, retrieved, k=1) == 1.0
```

### Edge Cases

Include boundary conditions:

```python
def test_empty_retrieved_spans() -> None:
    """Zero recall when no results retrieved."""
    gold = [(0, 10)]
    retrieved = []
    assert recall_at_k(gold, retrieved, k=1) == 0.0
```

### Property-Based Tests

Use Hypothesis for fuzz testing:

```python
@given(st.lists(spans_strategy, min_size=1))
def test_recall_in_range(spans: list[tuple[int, int]]) -> None:
    """Recall is always in [0, 1] range."""
    assert 0 <= recall_at_k(*spans, k=5) <= 1
```

## Reporting Issues

Use GitHub Issues to report bugs or request features.

### Bug Report

Include:
- Python version
- SPANCHOR version
- Exact error message and traceback
- Minimal reproduction steps

### Feature Request

Include:
- Use case motivation
- Proposed API
- Example usage

## Resources

- [Repository](https://github.com/Mukeshram-07/spanchor)
- [PyPI](https://pypi.org/project/spanchor/)
- [README](README.md)
- [Changelog](CHANGELOG.md)

## Contributors

SPANCHOR is built by the open-source community:

- Mukeshram S 
- Kelvin James P (Project maintainer)

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License (same as SPANCHOR).

## Questions?

Open an issue or discussion on GitHub. The maintainers are happy to help!

---

Thank you for contributing to SPANCHOR!
