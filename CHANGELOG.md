# SPANCHOR Changelog

All notable changes to this project are documented in this file.

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
