# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-30

### Added

#### Core Architecture
- **Source-Anchored Evaluation**: Gold labels anchor to character spans in canonical documents (NFC-normalized, hash-verified)
- **Per-Query Regression Detection**: Classification of individual queries as IMPROVED/REGRESSION/UNCHANGED based on per-query metric deltas
- **Aggregate Metric Reporting**: Macro-averaged metrics for diagnostics and trending (not used for gating)

#### Evaluation Metrics
- **Recall@K**: Proportion of gold character spans covered by top-K retrieved spans
- **Precision@K**: Proportion of retrieved characters overlapping with any gold span
- **Hit@K**: Whether at least one gold span has minimum overlap threshold (default 50%)
- **FullEvidence@K**: Whether ALL gold spans meet minimum overlap threshold
- **IoU**: Intersection-over-union diagnostic metric for span overlap analysis
- **Retrieved Character Count**: Diagnostic metric showing total characters in top-K results

#### Mapping Engine
- **Chunk-to-Span Mapper**: Automatically maps chunk-text retrieval results back to source spans
- **Policy Handling**: EXACT, NORMALIZED, PARTIAL, AMBIGUOUS, UNMAPPED mapping policies
- **Span Merging**: O(n log n) sorted-interval merging algorithm (no per-character sets)
- **Whitespace Normalization**: Handles varied whitespace and newline formats

#### Comparison & Regression Detection
- **Run Comparison**: Compare baseline vs candidate evaluation runs
- **Per-Query Deltas**: Independent metric change computation for each query
- **Policy Thresholds**: Configurable max_drop thresholds per metric
- **Regression Gating**: Detects when ANY query exceeds policy threshold (prevents aggregate masking)
- **Exit Codes**: 0 (pass), 1 (regression detected), 2 (usage error), 3 (unmapped-rate exceeded)

#### Reporting
- **Markdown Reports**: Human-readable per-query and aggregate results with formatting
- **JSON Export**: Full run metrics and comparison results for CI/CD integration
- **Redaction**: Optional redaction of question text and chunk content in reports
- **Schema Versioning**: All serialized data carries schema_version for compatibility

#### CLI Commands
- `spanchor validate`: Validate gold set against canonical documents
- `spanchor evaluate`: Evaluate retriever results against gold anchors
- `spanchor compare`: Compare baseline vs candidate runs with regression detection
- `spanchor locate`: Find text spans in documents for anchor creation
- `spanchor anchor-add`: Create anchors from document text and spans
- `spanchor check-corpus`: Check corpus integrity and mapping health

#### Public API
- **Anchor**: Frozen dataclass with document_id, [start:end), expected_text_hash, validation
- **Document**: Canonical text with SHA256 hash, NFC normalization, from_text() factory
- **Query**: Query with ID, question text, and tuple of gold anchors
- **RetrievalResult**: Span-form (document_id, start, end) or chunk-text form with scoring
- **Run**: Evaluation run with per-query and aggregate metrics, mapper statistics, config
- **evaluate()**: Evaluate retriever results against gold set, compute all metrics
- **compare()**: Compare two runs, detect regressions, classify queries
- **check_corpus()**: Validate corpus documents and gold set consistency

#### Data Models
- **Frozen, Slotted Dataclasses**: Immutable, memory-efficient models with explicit validators
- **Type Hints**: Full strict mypy compliance across all modules
- **Explicit Validators**: Input validation with typed error messages
- **Schema Versioning**: All models and serialized data carry schema_version

#### Error Handling
- **Typed Exceptions**: InvalidSchemaError, DocumentNotFoundError, HashMismatchError, AnchorResolutionError, OrphanedAnchorError, InvalidRetrievalResultError, EvaluationError, ComparisonError
- **Actionable Messages**: Every error includes what happened, values involved, and suggested action
- **Structured Error Data**: Error context with relevant metadata for debugging

#### Real-World Validation
- **CloudSync Documentation Corpus**: 4 technical documents (17.4 KB canonical text)
- **100 Gold Questions**: Validated source-anchored evaluation questions with real anchors
- **Baseline/Candidate Scenarios**: Regression scenario (exit 1) and passing scenario (exit 0)
- **Per-Query Regression Detection Verified**: Correct semantics validated with 16 comprehensive tests

#### Testing
- **751 Unit Tests**: 100% passing, zero flakes, comprehensive edge case coverage
- **82% Overall Coverage**: >90% coverage on core modules (exceeds target)
- **Hypothesis-Based Testing**: Property-based tests for robustness
- **Regression Gate Tests**: 16 tests validating per-query detection semantics
- **Integration Scenarios**: Real-world validation with complete pipeline

#### Build & Deployment
- **Hatchling Build System**: Clean, modern Python build configuration
- **uv Package Manager**: Dependency management and virtual environment
- **Pre-commit Hooks**: Automatic ruff format/lint, mypy --strict, pytest on pre-push
- **Development Dependencies**: pytest, hypothesis, mypy, ruff, pre-commit

#### Documentation
- **README.md**: Core concepts, installation, quick start, CLI reference
- **Real-World Validation Guide**: End-to-end validation pipeline documentation
- **CHANGELOG.md**: This file
- **API Docstrings**: Comprehensive docstrings on all public APIs

### Technical Details

#### Architecture
- **Local-First**: No network calls, no telemetry, no external dependencies for core
- **Deterministic**: Same inputs produce identical outputs, suitable for CI/CD
- **Dependency-Light**: Runtime deps: typer (CLI), rich (formatting) only
- **Python 3.11+**: Strict mypy compliance, dataclass slots, modern Python features

#### Span Math
- **Unicode Code-Points**: All offsets are code-point offsets into canonical text (not byte offsets)
- **Half-Open Intervals**: Spans use [start, end) semantics
- **Sorted-Interval Merging**: O(n log n) algorithm for efficient span union/intersection
- **No Per-Character Sets**: Memory-efficient, scales to large documents

#### Normalization
- **NFC Canonical Form**: All text normalized to NFC for consistency
- **Newline Normalization**: \r\n and \r converted to \n
- **Hash Verification**: SHA256 of canonical text for integrity checks

#### Per-Query Regression Semantics
- **Policy Keys Match Per-Query Metrics**: Configuration uses per-query names (e.g., "recall@5", not "mean_recall@5")
- **Per-Query Classification**: Each query independently evaluated
- **Regression Gate**: Triggered by ANY query exceeding threshold (not aggregate)
- **Prevents Masking**: Aggregate improvements cannot hide individual regressions

### Known Limitations

- **v0.1.0 Alpha Release**: This is the initial public release. Architecture is stable, but minor API changes may occur based on feedback.
- **No ML Models**: Retriever implementations are user-provided (library handles evaluation, not retrieval itself)
- **No Vector Embeddings**: Use spanchor as a component in your RAG pipeline, not as the retriever
- **No PDF/OCR**: Documents must be provided as text (use your own parser/OCR)
- **No Dashboard**: Reports are markdown/JSON for CI/CD integration, not interactive UI
- **No LLM Integration**: Gold labels must be created outside spanchor (manually or via your own process)

### Non-Goals

Spanchor intentionally does NOT provide:
- RAG framework (document loading, vector indexing, chat interface)
- Embedding models or vector databases
- Document parsing or OCR
- LLM provider integrations
- Answer quality evaluation (only retrieval quality)
- Interactive dashboards or web UI
- Cloud services or hosted evaluation

### Contributing

This is the v0.1.0 alpha release. For issues, feature requests, or contributions, please refer to project guidelines.

---

[0.1.0]: https://github.com/spanchor/spanchor/releases/tag/0.1.0
