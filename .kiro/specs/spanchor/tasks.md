\
]'={?:
\=op
\'={]\}
  # Implementation Plan: Spanchor

## Overview

This plan implements a Python library and CLI for regression-testing RAG retrieval pipelines using stable source-document anchors. The implementation follows a layered architecture with frozen dataclasses, explicit validation, and comprehensive property-based testing using Hypothesis.

## Tasks

- [x] 1. Set up project structure and error types
  - Create src/spanchor directory structure following the defined layout
  - Implement error hierarchy in src/spanchor/errors.py with typed exceptions
  - Set up pyproject.toml with hatchling, uv, Python 3.11+ support
  - Configure mypy --strict, ruff linting in pyproject.toml
  - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5, 25.6, 25.7, 25.8, 25.9_

- [x] 2. Implement canonical layer
  - [x] 2.1 Create text normalization and hashing functions
    - Implement normalize_text() with NFC Unicode normalization and newline normalization in src/spanchor/canonical/normalize.py
    - Implement compute_hash() using SHA256 in src/spanchor/canonical/normalize.py
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 Write property test for document canonicalization idempotence
    - **Property 1: Document Canonicalization Idempotence**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

- [x] 3. Implement core data models
  - [x] 3.1 Create Document model with validation
    - Implement frozen slotted Document dataclass in src/spanchor/models/document.py
    - Add from_text() factory method using canonical layer
    - Implement schema versioning (0.1.0)
    - _Requirements: 1.4, 1.5_

  - [x] 3.2 Write property test for document serialization round-trip
    - **Property 2: Document Serialization Round-Trip**
    - **Validates: Requirements 1.5**

  - [x] 3.3 Create Anchor model with validation
    - Implement frozen slotted Anchor dataclass in src/spanchor/models/anchor.py
    - Implement validate() method with hash, bounds, and text verification
    - Raise typed errors for validation failures
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

  - [x] 3.4 Write property tests for anchor validation
    - **Property 3: Anchor Offset Slice Semantics**
    - **Validates: Requirements 2.2**

  - [x] 3.5 Write property test for anchor invalid offset detection
    - **Property 4: Anchor Validation Detects Invalid Offsets**
    - **Validates: Requirements 2.5**

  - [x] 3.6 Write property test for anchor hash mismatch detection
    - **Property 5: Anchor Validation Detects Hash Mismatches**
    - **Validates: Requirements 2.4**

  - [x] 3.7 Create Query and RetrievalResult models
    - Implement frozen slotted Query dataclass with tuple[Anchor, ...] in src/spanchor/models/query.py
    - Implement frozen slotted RetrievalResult dataclass with span/chunk-text dual form in src/spanchor/models/retrieval.py
    - Add needs_mapping() method to RetrievalResult
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 3.8 Write property tests for query and retrieval models
    - **Property 7: Query Serialization Round-Trip**
    - **Validates: Requirements 3.2, 3.4**

  - [x] 3.9 Write property test for retrieval result classification
    - **Property 8: Retrieval Result Classification**
    - **Validates: Requirements 4.5**

  - [x] 3.10 Write property test for retrieval result rank validation
    - **Property 9: Retrieval Result Rank Validation**
    - **Validates: Requirements 4.6**

  - [x] 3.11 Create Run model
    - Implement frozen slotted Run dataclass in src/spanchor/models/run.py
    - Include timestamp, queries, metrics, config, mapper_stats fields
    - _Requirements: 11.1, 11.2_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement storage layer
  - [x] 5.1 Create JSONL reader/writer with schema validation
    - Implement read_gold_set() with line-by-line parsing in src/spanchor/storage/jsonl.py
    - Implement write_gold_set() for JSONL output
    - Add schema_version validation and duplicate query_id detection
    - Provide actionable error messages with file path, line number, and field details
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 14.1, 14.3, 14.4, 14.5, 14.6, 14.7_

  - [x] 5.2 Write property test for query set duplicate detection
    - **Property 6: Query Set Duplicate Detection**
    - **Validates: Requirements 3.5, 3.7**

  - [x] 5.3 Create JSON reader/writer for runs
    - Implement read_run() and write_run() in src/spanchor/storage/json_io.py
    - Add redaction support to omit source text when requested
    - Validate schema version and required fields
    - _Requirements: 14.2, 14.3, 14.4, 14.5, 14.8, 14.9_

- [x] 6. Implement interval algebra utilities
  - [x] 6.1 Create interval operations module
    - Implement union() using sorted-interval merging O(n log n) in src/spanchor/evaluation/intervals.py
    - Implement intersection() for two interval sets
    - Implement length() to sum non-overlapping interval lengths
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.2 Write property test for interval union idempotence
    - **Property 16: Interval Union Idempotence**
    - **Validates: Requirements 6.6**

  - [x] 6.3 Write property test for interval intersection symmetry
    - **Property 17: Interval Intersection Symmetry**
    - **Validates: Requirements 6.7**

  - [x] 6.4 Write property test for interval union merging overlaps
    - **Property 18: Interval Union Merges Overlaps**
    - **Validates: Requirements 6.1, 6.4**

  - [x] 6.5 Write property test for interval length computation
    - **Property 19: Interval Length Computation**
    - **Validates: Requirements 6.3**

- [x] 7. Implement evaluation metrics
  - [x] 7.1 Create Recall@K and Precision@K metrics
    - Implement recall_at_k() using interval algebra in src/spanchor/evaluation/recall.py
    - Implement precision_at_k() in src/spanchor/evaluation/precision.py
    - Validate K > 0 and non-empty gold spans
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [x] 7.2 Write property tests for recall and precision bounds
    - **Property 20: Recall Metric Bounds**
    - **Validates: Requirements 7.1, 7.6**

  - [x] 7.3 Write property test for precision metric bounds
    - **Property 21: Precision Metric Bounds**
    - **Validates: Requirements 7.2, 7.7**

  - [x] 7.4 Write property test for recall monotonicity
    - **Property 22: Recall Monotonicity**
    - **Validates: Requirements 7.8**

  - [x] 7.5 Create Hit@K and FullEvidence@K metrics
    - Implement hit_at_k() with min_overlap threshold in src/spanchor/evaluation/hit.py
    - Implement full_evidence_at_k() requiring all gold spans covered
    - Use default min_overlap=0.5
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 7.6 Create IoU diagnostic metric
    - Implement iou() as intersection-over-union in src/spanchor/evaluation/iou.py
    - Mark as diagnostic-only in documentation
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 8. Implement chunk-to-span mapper
  - [x] 8.1 Create chunk mapping engine
    - Implement ChunkMapper class with exact substring search in src/spanchor/mapping/mapper.py
    - Add whitespace normalization fallback with offset map
    - Implement ambiguity detection for duplicate chunks
    - Support ambiguity policies: first_unclaimed, all_occurrences, fail
    - Track mapping status: MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, UNMAPPED
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

  - [x] 8.2 Write property test for exact substring detection
    - **Property 10: Chunk Mapper Exact Substring Detection**
    - **Validates: Requirements 5.1, 5.2**

  - [x] 8.3 Write property test for whitespace normalization fallback
    - **Property 11: Chunk Mapper Whitespace Normalization Fallback**
    - **Validates: Requirements 5.3**

  - [x] 8.4 Write property test for ambiguity detection
    - **Property 12: Chunk Mapper Ambiguity Detection**
    - **Validates: Requirements 5.4**

  - [x] 8.5 Write property test for unmapped detection
    - **Property 13: Chunk Mapper Unmapped Detection**
    - **Validates: Requirements 5.9**

  - [x] 8.6 Write property test for first_unclaimed policy
    - **Property 14: Chunk Mapper Policy Enforcement - First Unclaimed**
    - **Validates: Requirements 5.5**

  - [x] 8.7 Write property test for all_occurrences policy
    - **Property 15: Chunk Mapper Policy Enforcement - All Occurrences**
    - **Validates: Requirements 5.6**

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement evaluation engine
  - [x] 10.1 Create evaluate() function
    - Implement main evaluate() API in src/spanchor/evaluation/engine.py
    - Validate all anchors against documents
    - Map chunk-text results to spans using ChunkMapper
    - Compute all metrics (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU) per query
    - Compute macro-average aggregate metrics
    - Check unmapped rate against max_unmapped_rate threshold
    - Return Run object with timestamp, metrics, and mapper stats
    - _Requirements: 11.3, 11.4, 11.5, 11.6, 11.7, 5.11, 5.12_

  - [x] 10.2 Add metric aggregation
    - Implement macro-average aggregation by default in src/spanchor/evaluation/aggregation.py
    - Add optional micro-average support
    - Compute mean retrieved characters per query
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 10.3 Add small-sample warnings
    - Check if gold set has < 30 queries and print warning
    - Include actual query count in warning message
    - _Requirements: 24.1, 24.2, 24.3_

- [x] 11. Implement comparison and regression detection
  - [x] 11.1 Create compare() function
    - Implement compare() API in src/spanchor/comparison/compare.py
    - Compute per-query metric deltas (candidate - baseline)
    - Classify queries as IMPROVED, REGRESSION, or UNCHANGED based on thresholds
    - Compute aggregate metric deltas
    - Set has_regression flag if any query shows REGRESSION
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

  - [x] 11.2 Add regression policy enforcement
    - Support per-metric max_drop thresholds from configuration
    - Support CLI flag overrides for thresholds
    - Implement minimum-query-count guard if configured
    - _Requirements: 13.1, 13.2, 13.5, 13.6_

- [x] 12. Implement reporting layer
  - [x] 12.1 Create markdown report generation
    - Implement generate_evaluation_report() in src/spanchor/reporting/markdown.py
    - Include aggregate metrics table, per-query metrics table, mapper statistics
    - Implement generate_comparison_report() with per-query deltas and statuses
    - Support redaction mode to omit source text
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7_

  - [x] 12.2 Create JSON report generation
    - Implement JSON report functions in src/spanchor/reporting/json_report.py
    - Include all metrics, configuration, and metadata
    - Support redaction mode for JSON output
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6_

- [x] 13. Implement annotation helpers
  - [x] 13.1 Create locate command helper
    - Implement locate_text() in src/spanchor/annotation/locate.py
    - Search for exact matches across all documents
    - Fallback to whitespace-normalized search if no exact matches
    - Display document_id, offsets, text hash, and surrounding context
    - Number each occurrence when multiple matches found
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 13.2 Create anchor add helper
    - Implement add_anchor() in src/spanchor/annotation/add.py
    - Locate text in documents and create validated anchor
    - Handle unique text by appending to gold JSONL file
    - Handle ambiguous text with --occurrence N flag
    - Validate query_id uniqueness before adding
    - Create gold file if it doesn't exist
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

- [x] 14. Implement CLI commands
  - [x] 14.1 Create validate command
    - Implement validate command in src/spanchor/cli.py using Typer
    - Load and canonicalize documents
    - Parse gold set and validate all anchors
    - Print success message with counts or errors with actionable messages
    - Exit with code 0 (success) or 2 (error)
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

  - [x] 14.2 Create evaluate command
    - Implement evaluate command with docs_dir, gold_path, results_path arguments
    - Add --output, --report, --redact, --k, --max-unmapped-rate options
    - Call evaluate() API and generate reports if requested
    - Exit with code 0 (success) or 3 (unmapped rate exceeded)
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 13.7, 13.8_

  - [x] 14.3 Create compare command
    - Implement compare command with baseline_path, candidate_path arguments
    - Add --report, --policy, --max-recall-drop, --max-precision-drop, --redact options
    - Call compare() API and generate comparison report
    - Exit with code 0 (no regression), 1 (regression), or 2 (error)
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9, 13.3, 13.4_

  - [x] 14.4 Create locate command
    - Implement locate command with text and docs_dir arguments
    - Use annotation helper to find and display matches
    - Format output with Rich for terminal display
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 14.5 Create anchor command with add subcommand
    - Implement anchor command with add subcommand in CLI
    - Accept query-id, question, docs-dir, text, and optional --occurrence arguments
    - Use annotation helper to create and append anchor
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

  - [x] 14.6 Create check-corpus command
    - Implement check-corpus command with docs_dir and gold_path arguments
    - Validate all anchor document hashes, offset bounds, and text matches
    - Report all issues with document_id and query_id
    - Exit with code 0 (healthy) or 2 (issues found)
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6_

- [x] 15. Implement public API and testing helpers
  - [x] 15.1 Create public API exports
    - Create src/spanchor/__init__.py with exports
    - Export models: Anchor, Document, Query, RetrievalResult, Run
    - Export functions: evaluate, compare, check_corpus
    - Export all error classes
    - _Requirements: 26.1, 26.2, 26.3, 26.4, 26.5, 26.6, 26.7_

  - [x] 15.2 Create pytest testing helper
    - Implement assert_no_regression() in src/spanchor/testing.py
    - Raise AssertionError with detailed failure messages for regressions
    - List regressed queries, metrics, values, and thresholds
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_

  - [x] 15.3 Create retriever protocol adapter
    - Define RetrieverProtocol in src/spanchor/adapters/base.py
    - Specify retrieve() method signature accepting query string
    - Document protocol in docstrings
    - _Requirements: 27.1, 27.2, 27.3, 27.4_

- [x] 16. Create check_corpus validation function
  - [x] 16.1 Implement check_corpus() function
    - Create check_corpus() in src/spanchor/validation.py
    - Validate all anchors against documents (hash, bounds, text match)
    - Collect and return all validation errors
    - Used by CLI check-corpus command and exported in public API
    - _Requirements: 20.1, 20.2, 20.3, 26.6_

- [x] 17. Set up testing infrastructure
  - [x] 17.1 Configure pytest and Hypothesis
    - Set up pytest configuration in pyproject.toml
    - Configure Hypothesis settings for property-based tests
    - Set up coverage targets (>= 90% on core modules)
    - Create tests/conftest.py with fixtures for documents, queries, and runs
    - _Requirements: All property test requirements_

  - [x] 17.2 Create example demo data
    - Create examples/demo/ directory structure
    - Add sample docs/ with small text documents
    - Create gold.jsonl with sample queries and anchors
    - Add baseline.json and candidate.json sample runs
    - _Used for manual testing and documentation examples_

- [x] 18. Set up build and tooling configuration
  - [x] 18.1 Complete pyproject.toml configuration
    - Configure hatchling build backend
    - Set up optional dependencies: stats, langchain, llamaindex, annotation
    - Configure ruff linting rules
    - Configure mypy strict mode for src/
    - Set up entry points for spanchor CLI
    - _Requirements: Tech stack requirements_

  - [x] 18.2 Set up pre-commit hooks
    - Create .pre-commit-config.yaml
    - Add ruff linting and formatting hooks
    - Add mypy type checking hook
    - Add pytest hook for quick unit tests
    - _Requirements: Tech stack requirements_

- [x] 19. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- The implementation uses Python 3.11+ with frozen slotted dataclasses for memory efficiency
- All offsets are Unicode code-point based on canonical text (NFC + newline normalized)
- Interval operations use sorted-interval merging (O(n log n)), never per-character sets
- Error messages include what happened, values involved, and suggested actions
- Exit codes: 0 (pass), 1 (regression), 2 (usage/schema error), 3 (unmapped rate threshold)
- Hypothesis is used for property-based testing to validate mathematical properties
- The library is designed to be dependency-light with only typer and rich as runtime deps

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3.1"] },
    { "id": 2, "tasks": ["2.2", "3.2", "3.3"] },
    { "id": 3, "tasks": ["3.4", "3.5", "3.6", "3.7"] },
    { "id": 4, "tasks": ["3.8", "3.9", "3.10", "3.11"] },
    { "id": 5, "tasks": ["5.1"] },
    { "id": 6, "tasks": ["5.2", "5.3", "6.1"] },
    { "id": 7, "tasks": ["6.2", "6.3", "6.4", "6.5", "7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3", "7.4", "7.5", "7.6"] },
    { "id": 9, "tasks": ["8.1"] },
    { "id": 10, "tasks": ["8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "10.1"] },
    { "id": 11, "tasks": ["10.2", "10.3", "11.1"] },
    { "id": 12, "tasks": ["11.2", "12.1", "12.2", "13.1", "13.2"] },
    { "id": 13, "tasks": ["14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "16.1"] },
    { "id": 14, "tasks": ["15.1", "15.2", "15.3", "17.1", "17.2"] },
    { "id": 15, "tasks": ["18.1", "18.2"] }
  ]
}
```
