# SPANCHOR Changelog

All notable changes to this project are documented in this file.

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
