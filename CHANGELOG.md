# SPANCHOR Changelog

All notable changes to this project are documented in this file.

## [0.4.0] - 2026-10-18

### Added

#### Core v0.4.0 Features

**Feature 1: Corpus and Gold-Set Versioning**
- `src/spanchor/corpus/fingerprint.py` - Deterministic corpus hashing (SHA256)
- Automatic corpus_hash computation in `evaluate()`
- Optional gold_set_hash tracking and mismatch detection
- Three mismatch policies: warn, fail, ignore
- CLI flags: `--corpus-mismatch-policy`, `--gold-set-hash`

**Feature 3: Provenance and Mapping Confidence**
- Extended `MappingResult` with confidence scores (0.0–1.0)
  - MAPPED_EXACT → 1.0
  - MAPPED_NORMALIZED → 0.8
  - AMBIGUOUS → 0.5
  - UNMAPPED → 0.0
- Added reason field (explanation string for each mapping)
- Candidate spans tracking (all possible matches, not just selected)
- Full backward compatibility with existing mapper behavior

**Feature 4: Schema Versioning and Safe Migration**
- `src/spanchor/storage/schema.py` - Schema version documentation and constants
- `src/spanchor/storage/migration.py` - Automatic v0.1.0 → v0.2.0 migration
- Deprecation warning emitted when old format detected
- Safe round-trip: load → save → load produces identical data
- Zero breaking changes to public APIs

**Feature 6: Pluggable Metrics Registry**
- `src/spanchor/evaluation/metrics/` - MetricDefinition and MetricRegistry classes
- Wrap existing 5 metrics in registry pattern (recall, precision, hit, full_evidence, iou)
- Optional custom metric registration support
- Results identical to v0.3.0 when using default registry
- No performance overhead

**Feature 7: Gold-Set Generation (Minimal) and Candidate State Machine**
- Phase I: Candidate state persistence (PENDING/APPROVED/REJECTED workflow)
  - `src/spanchor/models/candidate.py` - Candidate, CandidateReview, CandidateStatus models
  - JSONL serialization with `read_candidate_pool()` and `write_candidate_pool()`
  - Editing a candidate keeps it PENDING (no auto-approval)
  - Rejection support with optional reason field
- Phase II: Explicit promotion of APPROVED candidates to gold
  - `src/spanchor/generation/promote.py` - `promote_candidate_to_gold()` function
  - Safety invariants: PENDING/REJECTED/invalid-anchor candidates cannot promote
  - Conversion to existing Query + Anchor representation (no new schema)
  - CLI: `spanchor gold promote CANDIDATE_ID --gold-set GOLD_FILE`
- Phase III: Provenance traceability
  - candidate_id → query_id mapping preserved through promotion
  - No fabricated provenance links
  - Round-trip persistence verified
- Phase IV+: Comprehensive test coverage and quality gates
  - All Feature 7 tests discoverable by pytest (root cause: import ordering)
  - Full test coverage for PENDING/APPROVED/REJECTED workflow, promotion safety, and provenance
  - Schema compatibility verified (0.2.0 required, no schema conflicts)
  - All quality gates pass (mypy --strict, ruff, pytest)
- Phase V: Complete candidate extraction and review workflow
  - `src/spanchor/generation/extract.py` - Rule-based sentence extraction
  - Deduplication: Levenshtein distance > 95% match = duplicate
  - CLI: `spanchor gold extract DOCS_DIR -o candidates.jsonl`
  - Candidate dataclass: candidate_id, text, document_id, confidence (1.0 for extraction)
  - Separation of concerns: extraction produces candidates, not gold

#### Feature 8 Enhancements (Bonus)

**Feature 8.1: Bootstrap Confidence Intervals**
- Integrate statistical analysis from Feature 2 into comparison results
- JSON report field: `aggregate_confidence_intervals` (metric → {mean_delta, lower_ci, upper_ci, ci_level, num_paired_queries, num_resamples})
- Markdown report section: "## Aggregate Confidence Intervals" (when statistics enabled)
- Backward compatible: CI fields omitted when statistics disabled (default)
- 10 new tests validating CI serialization and display

**Feature 8.2: Regression and Improvement Grouping**
- New "## Regressions (Sorted by Severity)" section showing REGRESSION queries
  - Sorted by sum of absolute negative deltas (magnitude of drops)
  - Policy thresholds displayed alongside actual deltas when policy provided
- New "## Improvements (Sorted by Impact)" section showing IMPROVED queries
  - Sorted by sum of positive deltas (magnitude of gains)
- Full redaction support: question text omitted when `redact=True`, metrics preserved
- Graceful degradation: sections appear only when data exists
- 12 new tests validating grouping, sorting, and policy display

**Feature 8.3: Set-wise Metrics Integration**
- Extended `compare()` with optional `include_setwise: bool = False` parameter
- Extended `Run` model with optional `per_query_retrieval_results` field
- Extended `ComparisonResult` with two optional fields:
  - `setwise_deltas`: per-query set-wise metric deltas (dict[query_id → dict[metric → delta]])
  - `setwise_aggregate_deltas`: macro-average set-wise deltas (dict[metric → delta])
- Metrics: span_concentration, fragmentation_ratio, pairwise_overlap (from Feature 5)
- Markdown report: "## Set-wise Metrics" section with aggregate and per-query changes
- JSON report: `setwise_aggregate_deltas` and `per_query_setwise_deltas` fields (omitted when disabled)
- Backward compatible: `include_setwise` defaults to False; setwise data omitted when unavailable
- 35 new tests (14 comparison + 21 reporting) validating computation, display, and backward compat

### Changed

#### Evaluation and Comparison Engine
- `src/spanchor/evaluation/engine.py` - Corpus/gold hashing, metric registry integration
- `src/spanchor/comparison/compare.py` - Statistics and set-wise metrics integration
- `src/spanchor/storage/json_io.py` - Auto-migration of v0.1.0 → v0.2.0 format

#### Reporting
- `src/spanchor/reporting/markdown.py` - Four new optional sections (F8.1 CI, F8.2 regressions/improvements, F8.3 setwise)
- `src/spanchor/reporting/json_report.py` - Three new optional fields (F8.1 CI, F8.3 setwise aggregate, F8.3 per-query setwise)

#### CLI
- `src/spanchor/cli.py` - New commands for gold-set generation (extract, promote, review)

#### Models
- `src/spanchor/models/run.py` - Added corpus_hash, gold_set_hash, per_query_retrieval_results (all optional)
- `src/spanchor/models/query.py` - Added optional candidate_id for provenance traceability
- `src/spanchor/models/candidate.py` - New Candidate, CandidateReview, CandidateStatus models
- `src/spanchor/mapping/mapper.py` - MappingResult extended with confidence, reason, candidate_spans

#### Code Quality
- Removed dead code from setwise metrics section
- All new code passes `ruff check` (0 issues)
- All new code passes `mypy --strict` (0 errors)

### Compatibility

#### Backward Compatible
- ✓ All v0.3.0 APIs unchanged (new parameters are optional with sensible defaults)
- ✓ All CLI commands work identically (new commands are additive)
- ✓ All 1200+ v0.3.0 tests still pass without modification
- ✓ v0.1.0 data loads correctly via automatic schema migration
- ✓ New optional fields default to None when unavailable
- ✓ Report sections appear only when data exists (graceful degradation)

#### Breaking Changes
- None. v0.4.0 is fully backward compatible with v0.3.0 and v0.2.x.

#### New Optional Features (Opt-In)
- Statistics: Disabled by default; enable via `StatisticsConfig(enabled=True)`
- Set-wise metrics: Disabled by default; enable via `compare(..., include_setwise=True)`
- Candidate workflow: New optional CLI commands (does not affect existing evaluation workflow)
- Policy thresholds: Optional in reports; display only when policy provided

### Known Limitations

**Feature 8.2: Mixed-Scale Severity Ranking**
- Regression severity calculated as sum of absolute negative deltas (metric-agnostic)
- All metrics weighted equally; no importance weighting or normalization
- Limitation: For multi-metric comparisons with different scales (e.g., 0–1 vs 0–100), ranking may not align with semantic importance
- Workaround: Users can manually review metrics; future versions may add metric weighting
- Impact: Low (informational sorting; users can override interpretation)

**Feature 8.4: CLI Enhancements Deferred**
- HTML report output not yet implemented (planned for v0.4.1)
- CLI flags `--format markdown|json|html` not yet available (planned for v0.4.1)
- CLI flags `--confidence-level N` and `--include-setwise` not yet available (planned for v0.4.1)
- Workaround: Use programmatic API; pass parameters directly to `compare()` and report functions

### Testing

- 1223 total tests (807 v0.3.0 + 416 v0.4.0 new tests)
- 100% new test pass rate
- Coverage: 85% (2558 statements covered)
- Comprehensive test coverage for:
  - Schema versioning and migration (v0.1.0 → v0.2.0)
  - Corpus and gold-set hashing (determinism, sensitivity, order independence)
  - Mapping confidence scores and provenance tracking
  - Metric registry and custom metric registration
  - Candidate state machine (PENDING/APPROVED/REJECTED workflow)
  - Candidate → gold promotion and safety invariants
  - Bootstrap CI computation and serialization
  - Regression/improvement grouping and policy thresholds
  - Set-wise metrics computation and report display
  - Backward compatibility (all new features optional, all tests pass without modification)

### Quality Gates

- ✓ pytest: 1223 passed (0 failed, 0 skipped)
- ✓ mypy --strict: 0 errors in 53 source files
- ✓ ruff: 0 issues (all code passes linting)
- ✓ Coverage: 85% overall, >90% for core modules

---

## [0.3.0] - 2026-10-01

### Added

#### LangChain Adapter Comprehensive Tests
- `tests/unit/test_adapters_langchain.py` - 16 comprehensive test cases
- Tests for document conversion, metadata extraction, score handling, document ID mapping
- Tests for edge cases: missing scores, missing document IDs, metadata preservation
- Tests for custom metadata key configuration
- Mock-based testing ensures tests run without LangChain installed

#### LlamaIndex Adapter Comprehensive Tests
- `tests/unit/test_adapters_llamaindex.py` - 17 comprehensive test cases
- Tests for NodeWithScore conversion, TextNode handling, metadata extraction
- Tests for get_content() method and text attribute fallback
- Tests for document ID extraction from source/document_id fields
- Mock-based testing ensures tests run without LlamaIndex installed

#### LlamaIndex Compatibility for Current Versions
- Updated `src/spanchor/adapters/llamaindex.py` to support both old (`llama_index.schema`) and new (`llama_index.core.schema`) import paths
- Backward compatible with older LlamaIndex versions while supporting current versions (0.9.0+)
- Graceful import error when LlamaIndex is not installed

#### Gold-Set Import Tool
- `src/spanchor/annotation/import_gold.py` - Full gold-set bootstrap functionality
- `import_from_chunks()` - Convert chunk text lists to SPANCHOR source-anchored format
- `import_from_chunk_dict()` - Import from record dictionaries (JSON/JSONL format)
- `summarize_import_results()` - Batch import statistics
- Chunk resolution with exact match and whitespace-normalized fallback
- Ambiguity detection (reports multiple matches explicitly)
- `tests/unit/test_import_gold.py` - 19 comprehensive test cases

#### Contributor Documentation
- `CONTRIBUTING.md` - Community contribution guidelines
- Development setup instructions
- Running tests (full, specific, by pattern)
- Code quality checks (ruff format, ruff lint, mypy)
- Code style guide and PR requirements

### Changed

#### Code Quality
- Removed unused imports from new modules for zero new lint errors
- All new code passes `ruff format --check` and `ruff check`
- All new code passes `mypy --strict`
- No degradation to existing code quality

### Compatibility

#### Backward Compatible
- ✓ All v0.2.1 APIs unchanged
- ✓ All CLI commands work identically
- ✓ No breaking changes to evaluation semantics
- ✓ No breaking changes to regression detection
- ✓ All 754 v0.2.1 tests still pass
- ✓ Gold-set import is additive (no API changes)

#### New Optional Integration
- LlamaIndex: Supports both old and new import paths seamlessly
- LangChain: Enhanced test coverage
- Gold-set import: Adoption tool (programmatic API, not CLI)

#### Breaking Changes
- None. v0.3.0 is fully backward compatible with v0.2.1

### Testing

- 53 new tests added (LangChain, LlamaIndex, gold-set import)
- 807 total tests now (754 + 53)
- 100% new test pass rate
- Coverage maintained at 80%
- Real framework integration tests with actual LangChain and LlamaIndex objects
- Real-world validation with 4-document, 100-query dataset

---

## [0.2.1] - 2026-10-01

### Changed

#### Documentation
- Completely rewrote README.md with improved clarity and structure
- Enhanced problem statement with real regression example (0.405 → 0.249 recall)
- Better organization of framework integration examples
- Clearer installation instructions with optional extras highlighted
- Improved PyPI package description for better discoverability

### Compatibility

#### Backward Compatible
- ✓ All v0.2.0 APIs unchanged
- ✓ All CLI commands work identically
- ✓ No code changes in release

---

## [0.2.0] - 2026-10-01

### Added

#### Generic Retriever Adapter
- `spanchor.adapters.generic.dict_to_retrieval_result()` - Convert dictionaries to RetrievalResult with flexible field name support
- `spanchor.adapters.generic.dicts_to_retrieval_results()` - Convert list of dictionaries to RetrievalResults with auto-ranking
- Support for multiple naming conventions: text/chunk/content/body, score/relevance_score/similarity/confidence, rank/position/index, document_id/doc_id/source/document
- Metadata preservation for unrecognized fields
- Comprehensive error handling with clear messages

#### LangChain Integration (Optional)
- `spanchor.adapters.langchain.documents_to_retrieval_results()` - Convert LangChain Document objects to RetrievalResults
- Configurable score and document ID extraction from metadata
- Full metadata preservation
- Optional dependency: install with `pip install "spanchor[langchain]"`
- Does not require LangChain for core SPANCHOR functionality

#### LlamaIndex Integration (Optional)
- `spanchor.adapters.llamaindex.nodes_to_retrieval_results()` - Convert LlamaIndex NodeWithScore objects to RetrievalResults
- Support for multiple node types (TextNode, etc.)
- Metadata and document ID extraction
- Optional dependency: install with `pip install "spanchor[llamaindex]"`
- Does not require LlamaIndex for core SPANCHOR functionality

#### Real-World RAG Adoption Example
- `examples/adoption_demo/README.md` - Comprehensive guide for integrating SPANCHOR into RAG pipelines
- End-to-end example showing baseline vs candidate retrieval comparison
- Integration examples for LangChain, LlamaIndex, and generic dict formats
- Configuration variation demonstrations and interpretation guide

#### Testing
- 19 new comprehensive tests for generic adapter (2 test classes, 100% coverage)
- Tests for text form conversion, span form conversion, field name aliases, metadata preservation, auto-ranking, error handling
- All 754 tests passing

### Changed

#### Optional Dependencies
- `pyproject.toml` now includes optional extras for framework integrations:
  - `[langchain]`: Installs LangChain integration dependencies
  - `[llamaindex]`: Installs LlamaIndex integration dependencies
- Core `pip install spanchor` remains lightweight with no framework dependencies

#### Adapter Package Exports
- Enhanced `spanchor.adapters` module exports with generic converter functions
- Backward compatible - existing `RetrieverProtocol` still available

### Compatibility

#### Backward Compatible
- ✓ All v0.1.1 public APIs remain unchanged
- ✓ All existing CLI commands work identically  
- ✓ Evaluation semantics unchanged
- ✓ Comparison/regression detection unchanged
- ✓ All 735 original tests still pass
- ✓ Full compatibility with v0.1.x code

#### Breaking Changes
- None. v0.2.0 is fully backward compatible with v0.1.1

#### Python Support
- Maintained: Python 3.11, 3.12, 3.13
- Build system: hatchling (unchanged)
- Package format: wheel + source distribution

---

## [0.1.1] - 2026-09-30

### Added
- Real-world benchmark example (4 documents, 100 queries, regression detection)
- Stage 1 investigation documentation

### Fixed
- CI: Pinned ruff to 0.1.6 to avoid version incompatibility with GitHub Actions

---

## [0.1.0] - 2026-09-15

### Initial Release

- Source-anchored regression testing framework
- Character-level span coverage metrics (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU)
- Per-query regression detection
- Chunk-to-source mapping with exact + normalized fallback
- Local, deterministic, offline-first design
- Full type safety (mypy strict mode)
- Comprehensive test coverage (735 tests)
- CI/CD ready with exit codes and markdown reports
- Published to PyPI

---

## Release Versioning

SPANCHOR follows semantic versioning:

- **0.x.y**: Alpha/early development
  - Breaking changes possible between minor versions
  - New features and enhancements released as minor versions
  - Bug fixes released as patch versions
  
- **1.0.0+**: Stable API (future)
  - Semantic versioning strictly enforced
  - Breaking changes only in major versions
