# Requirements Document

## Introduction

Spanchor is a Python library and CLI tool for regression-testing RAG (Retrieval-Augmented Generation) retrieval pipelines using stable source-document anchors instead of fragile chunk IDs. The system separates source evidence from retrieval representation by anchoring gold labels to character spans in canonical source documents, then mapping any retriever output back to those spans for scoring and comparison.

## Glossary

- **Anchor**: A reference to a specific character span in a canonical source document, consisting of document_id, start offset, end offset, and text hash
- **Canonical_Document**: A source document that has been normalized (NFC Unicode normalization, newline normalization to \n) and assigned a sha256 hash
- **Chunk_Mapper**: Component that maps retrieval results in chunk-text form to character spans in canonical documents
- **Evaluation_Engine**: Component that computes coverage metrics by comparing retrieved spans against gold anchor spans
- **Gold_Set**: Collection of queries with their associated ground-truth anchors pointing to relevant evidence spans
- **Retrieval_Result**: Output from a retriever, either in span form (document_id, start, end, rank, score) or chunk-text form (text, rank, score, optional document_id and metadata)
- **Run**: A complete evaluation result containing queries, retrieved spans, and computed metrics
- **Comparison_Engine**: Component that compares two runs (baseline vs candidate) and identifies per-query regressions
- **CLI_Tool**: Command-line interface providing validate, evaluate, compare, locate, anchor, and check-corpus commands
- **Annotation_Helper**: Minimal utility for locating text in documents and creating anchor entries
- **Report_Generator**: Component that produces markdown and JSON evaluation and comparison reports

## Requirements

### Requirement 1: Document Canonicalization and Hashing

**User Story:** As a developer, I want source documents to be canonicalized and hashed, so that anchors remain stable across different text encodings and line-ending conventions.

#### Acceptance Criteria

1. WHEN a source document is loaded, THE Canonical_Document SHALL apply NFC Unicode normalization to the text
2. WHEN a source document is loaded, THE Canonical_Document SHALL normalize all \r\n and \r sequences to \n
3. WHEN a source document is loaded, THE Canonical_Document SHALL compute a sha256 hash of the canonicalized text
4. THE Canonical_Document SHALL store the document_id, canonicalized text, and sha256 hash
5. FOR ALL valid source documents, loading, exporting, and reloading SHALL produce the same sha256 hash (round-trip property)

### Requirement 2: Anchor Model and Validation

**User Story:** As a developer, I want anchors to reference precise character spans with integrity verification, so that gold labels can be validated against their source documents.

#### Acceptance Criteria

1. THE Anchor SHALL contain document_id, start offset, end offset, and expected text hash fields
2. THE Anchor SHALL use half-open intervals where start is inclusive and end is exclusive
3. THE Anchor SHALL store a schema_version field for forward compatibility
4. WHEN an Anchor is validated against a Canonical_Document, THE Anchor SHALL verify the document hash matches the expected hash
5. WHEN an Anchor is validated against a Canonical_Document, THE Anchor SHALL verify the span offsets are within document bounds
6. WHEN an Anchor is validated against a Canonical_Document, THE Anchor SHALL verify the text at the specified offsets matches the anchor text
7. IF the document hash does not match, THEN THE Anchor SHALL raise a HashMismatchError with the document_id and both hashes
8. IF the offsets are out of bounds, THEN THE Anchor SHALL raise an AnchorResolutionError with the document_id and invalid offsets
9. IF the text at the offsets does not match, THEN THE Anchor SHALL raise an AnchorResolutionError with the document_id, offsets, expected text, and actual text

### Requirement 3: Query and Gold Set Model

**User Story:** As a developer, I want to define queries with their associated gold anchors, so that I can maintain a stable test set for retrieval evaluation.

#### Acceptance Criteria

1. THE Query SHALL contain a query_id, question text, and a list of Anchor references
2. THE Query SHALL support queries with zero, one, or multiple gold anchors
3. THE Query SHALL store a schema_version field for forward compatibility
4. THE Gold_Set SHALL be stored in JSONL format with one query per line
5. WHEN a Gold_Set is loaded, THE Gold_Set SHALL validate that all queries have unique query_id values
6. WHEN a Gold_Set is loaded, THE Gold_Set SHALL validate the schema_version for each query
7. IF a query_id is duplicated, THEN THE Gold_Set SHALL raise an InvalidSchemaError with the duplicated query_id
8. IF the schema_version is unsupported, THEN THE Gold_Set SHALL raise an InvalidSchemaError with the unsupported version

### Requirement 4: Retrieval Result Model

**User Story:** As a developer, I want to represent retrieval results in both span and chunk-text forms, so that the system can handle output from different retriever implementations.

#### Acceptance Criteria

1. THE Retrieval_Result SHALL support span form with document_id, start offset, end offset, rank, and score fields
2. THE Retrieval_Result SHALL support chunk-text form with text, rank, score, and optional document_id and metadata fields
3. THE Retrieval_Result SHALL include a span_type field defaulting to "text"
4. THE Retrieval_Result SHALL store a schema_version field for forward compatibility
5. WHEN a Retrieval_Result in chunk-text form is provided, THE Retrieval_Result SHALL indicate it requires mapping
6. THE Retrieval_Result SHALL validate that rank values are positive integers
7. THE Retrieval_Result SHALL validate that score values are numeric

### Requirement 5: Chunk-to-Span Mapper

**User Story:** As a developer, I want chunk text to be mapped back to canonical document spans, so that retrieval results from chunk-based systems can be evaluated using source anchors.

#### Acceptance Criteria

1. WHEN a chunk in chunk-text form with a document_id is provided, THE Chunk_Mapper SHALL search for exact substring matches in that document
2. WHEN a chunk in chunk-text form without a document_id is provided, THE Chunk_Mapper SHALL search for exact substring matches across all documents
3. IF no exact match is found, THEN THE Chunk_Mapper SHALL apply whitespace normalization and search using an offset map
4. WHEN a chunk text appears multiple times in the search space, THE Chunk_Mapper SHALL mark the result as AMBIGUOUS
5. WHEN an AMBIGUOUS chunk is encountered and the policy is "first unclaimed occurrence", THE Chunk_Mapper SHALL map to the first occurrence not yet claimed by another chunk
6. WHERE the policy is "all occurrences", THE Chunk_Mapper SHALL create multiple span results for an AMBIGUOUS chunk
7. WHERE the policy is "fail", THE Chunk_Mapper SHALL raise an AnchorResolutionError for an AMBIGUOUS chunk
8. WHEN a chunk spans multiple documents, THE Chunk_Mapper SHALL create one span per document
9. WHEN a chunk cannot be mapped, THE Chunk_Mapper SHALL mark the result as UNMAPPED
10. THE Chunk_Mapper SHALL return mapping results with status values MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, or UNMAPPED
11. THE Chunk_Mapper SHALL count UNMAPPED chunks and include them in evaluation reports
12. WHEN the unmapped chunk rate exceeds max_unmapped_rate threshold, THE Chunk_Mapper SHALL exit with code 3

### Requirement 6: Interval Algebra Utilities

**User Story:** As a developer, I want efficient interval operations, so that span overlaps and unions can be computed accurately for metric calculation.

#### Acceptance Criteria

1. THE Evaluation_Engine SHALL compute the union of overlapping intervals using sorted-interval merging with O(n log n) complexity
2. THE Evaluation_Engine SHALL compute the intersection of intervals from two sets
3. THE Evaluation_Engine SHALL compute the length of an interval set by summing non-overlapping interval lengths
4. WHEN computing union, THE Evaluation_Engine SHALL ensure overlapping or adjacent spans are merged
5. WHEN computing intersection, THE Evaluation_Engine SHALL return only the portions where intervals from both sets overlap
6. FOR ALL interval operations, union(union(X)) SHALL equal union(X) (idempotence property)
7. FOR ALL interval sets X and Y, intersection(X, Y) SHALL equal intersection(Y, X) (symmetry property)

### Requirement 7: Recall and Precision Metrics

**User Story:** As a developer, I want character-level recall and precision metrics, so that I can measure how well retrieved spans cover gold evidence.

#### Acceptance Criteria

1. WHEN computing Recall@K, THE Evaluation_Engine SHALL calculate |G ∩ R| / |G| where G is the union of gold spans and R is the union of top-K retrieved spans
2. WHEN computing Precision@K, THE Evaluation_Engine SHALL calculate |G ∩ R| / |R| where R is the union of top-K retrieved spans
3. WHEN |R| equals zero, THE Evaluation_Engine SHALL set Precision@K to zero
4. WHEN |G| equals zero, THE Evaluation_Engine SHALL raise an EvaluationError indicating empty gold spans
5. WHEN K equals zero, THE Evaluation_Engine SHALL raise an EvaluationError indicating invalid K value
6. THE Evaluation_Engine SHALL ensure Recall@K is between 0 and 1 inclusive
7. THE Evaluation_Engine SHALL ensure Precision@K is between 0 and 1 inclusive
8. FOR ALL K values, Recall@K with K+1 SHALL be greater than or equal to Recall@K (monotonicity property)

### Requirement 8: Hit and FullEvidence Metrics

**User Story:** As a developer, I want boolean success metrics for single and multi-span queries, so that I can measure whether queries have adequate coverage.

#### Acceptance Criteria

1. WHEN computing Hit@K, THE Evaluation_Engine SHALL return 1 if any gold span has at least min_overlap fraction of its characters covered by top-K retrieved spans
2. WHEN computing Hit@K, THE Evaluation_Engine SHALL return 0 if no gold span meets the min_overlap threshold
3. WHEN computing FullEvidence@K, THE Evaluation_Engine SHALL return 1 if every gold span has at least min_overlap fraction covered by top-K retrieved spans
4. WHEN computing FullEvidence@K, THE Evaluation_Engine SHALL return 0 if any gold span fails to meet the min_overlap threshold
5. THE Evaluation_Engine SHALL use a default min_overlap value of 0.5
6. WHERE the user specifies a custom min_overlap value, THE Evaluation_Engine SHALL use that value
7. THE Evaluation_Engine SHALL validate that min_overlap is between 0 and 1 inclusive

### Requirement 9: IoU Diagnostic Metric

**User Story:** As a developer, I want Intersection-over-Union as a diagnostic metric, so that I can understand overall span alignment quality.

#### Acceptance Criteria

1. WHEN computing IoU, THE Evaluation_Engine SHALL calculate |G ∩ R| / |G ∪ R| where G is the union of gold spans and R is the union of retrieved spans
2. THE Evaluation_Engine SHALL ensure IoU is between 0 and 1 inclusive
3. WHEN |G ∪ R| equals zero, THE Evaluation_Engine SHALL set IoU to zero
4. FOR ALL span sets X and Y, IoU(X, Y) SHALL equal IoU(Y, X) (symmetry property)
5. THE Evaluation_Engine SHALL mark IoU as diagnostic-only and not use it for correctness determination

### Requirement 10: Metric Aggregation

**User Story:** As a developer, I want metrics aggregated across queries, so that I can understand overall pipeline performance.

#### Acceptance Criteria

1. WHEN aggregating metrics, THE Evaluation_Engine SHALL compute macro-average by averaging metric values across queries by default
2. WHERE the user requests micro-average, THE Evaluation_Engine SHALL compute micro-average by aggregating characters first, then computing metrics
3. THE Evaluation_Engine SHALL report the total number of retrieved characters per query as a token-cost proxy
4. THE Evaluation_Engine SHALL report the mean retrieved characters across all queries

### Requirement 11: Run Model and Evaluation API

**User Story:** As a developer, I want to evaluate retrieval results against a gold set programmatically, so that I can integrate spanchor into my testing pipeline.

#### Acceptance Criteria

1. THE Run SHALL contain the evaluation timestamp, gold queries, retrieval results, computed metrics, and configuration parameters
2. THE Run SHALL store a schema_version field for forward compatibility
3. WHEN evaluate() is called with documents, gold set, and retrieval results, THE Evaluation_Engine SHALL validate all anchors against documents
4. WHEN evaluate() is called, THE Evaluation_Engine SHALL map chunk-text results to spans using the Chunk_Mapper
5. WHEN evaluate() is called, THE Evaluation_Engine SHALL compute Recall@K, Precision@K, Hit@K, FullEvidence@K, and IoU for each query
6. WHEN evaluate() is called, THE Evaluation_Engine SHALL compute aggregate metrics across all queries
7. WHEN evaluate() is called, THE Evaluation_Engine SHALL return a Run object with all results and metadata

### Requirement 12: Comparison and Regression Detection

**User Story:** As a developer, I want to compare two runs and detect per-query regressions, so that I can prevent retrieval quality degradation in CI.

#### Acceptance Criteria

1. WHEN compare() is called with baseline and candidate runs, THE Comparison_Engine SHALL compute per-query metric deltas
2. WHEN compare() is called, THE Comparison_Engine SHALL classify each query as IMPROVED, REGRESSION, or UNCHANGED
3. WHEN a query metric drops by more than the configured max_drop threshold, THE Comparison_Engine SHALL classify it as REGRESSION
4. WHEN a query metric improves beyond the max_drop threshold, THE Comparison_Engine SHALL classify it as IMPROVED
5. WHEN a query metric change is within the max_drop threshold, THE Comparison_Engine SHALL classify it as UNCHANGED
6. THE Comparison_Engine SHALL compute aggregate metric deltas across all queries
7. THE Comparison_Engine SHALL generate a per-query delta table with statuses
8. THE Comparison_Engine SHALL generate an aggregate summary table with baseline, candidate, and delta values

### Requirement 13: Regression Policy Enforcement

**User Story:** As a developer, I want configurable regression thresholds with appropriate exit codes, so that CI can fail builds on quality drops.

#### Acceptance Criteria

1. THE Comparison_Engine SHALL accept per-metric max_drop thresholds from configuration
2. THE Comparison_Engine SHALL accept per-metric max_drop thresholds from CLI flags
3. WHEN any query has a REGRESSION status, THE CLI_Tool SHALL exit with code 1
4. WHEN all queries are UNCHANGED or IMPROVED, THE CLI_Tool SHALL exit with code 0
5. WHERE a minimum-query-count guard is configured, THE Comparison_Engine SHALL enforce that the gold set has at least that many queries
6. IF the gold set has fewer queries than the minimum-query-count, THEN THE Comparison_Engine SHALL raise a ComparisonError
7. WHEN the unmapped chunk rate exceeds max_unmapped_rate, THE CLI_Tool SHALL exit with code 3
8. WHEN a schema or usage error occurs, THE CLI_Tool SHALL exit with code 2

### Requirement 14: Storage and Schema Validation

**User Story:** As a developer, I want robust JSON/JSONL reading and writing with strict validation, so that data errors are caught before evaluation with actionable messages.

#### Acceptance Criteria

1. THE Storage_Module SHALL read and write Gold_Set data in JSONL format
2. THE Storage_Module SHALL read and write Run data in JSON or JSONL format
3. WHEN reading any file, THE Storage_Module SHALL validate the schema_version field
4. WHEN reading any file, THE Storage_Module SHALL validate all required fields are present
5. WHEN reading any file, THE Storage_Module SHALL validate field types match expected types
6. IF validation fails, THEN THE Storage_Module SHALL raise an InvalidSchemaError with the file path, line number, field name, and error description
7. THE Storage_Module SHALL provide clear error messages that include what happened, the values involved, and a suggested action
8. THE Storage_Module SHALL validate that all document_id references in anchors exist in the provided documents
9. IF a document_id is referenced but not found, THEN THE Storage_Module SHALL raise a DocumentNotFoundError with the missing document_id and query_id

### Requirement 15: Annotation Helper - Locate Command

**User Story:** As a developer, I want to find text in source documents and see matching anchor candidates, so that I can create gold anchors without manually computing offsets.

#### Acceptance Criteria

1. WHEN spanchor locate is called with text and document directory, THE Annotation_Helper SHALL search for exact matches across all documents
2. WHEN spanchor locate finds matches, THE Annotation_Helper SHALL print document_id, start offset, end offset, text hash, and surrounding context for each match
3. WHEN spanchor locate finds zero matches, THE Annotation_Helper SHALL search using whitespace-normalized matching
4. WHEN spanchor locate finds multiple matches, THE Annotation_Helper SHALL number each occurrence
5. THE Annotation_Helper SHALL display enough context characters before and after the match for user verification

### Requirement 16: Annotation Helper - Anchor Add Command

**User Story:** As a developer, I want to add validated anchors to my gold set through CLI, so that I can build gold sets without manual JSON editing.

#### Acceptance Criteria

1. WHEN spanchor anchor add is called with query-id, question, document directory, and text, THE Annotation_Helper SHALL locate the text in documents
2. WHEN the text is unique, THE Annotation_Helper SHALL append a valid query with anchor to the gold JSONL file
3. WHEN the text is ambiguous, THE Annotation_Helper SHALL reject the operation unless the user specifies --occurrence N
4. WHERE the user specifies --occurrence N, THE Annotation_Helper SHALL use the Nth occurrence for the anchor
5. WHEN spanchor anchor add succeeds, THE Annotation_Helper SHALL print a confirmation with the created query_id and anchor details
6. IF the gold file does not exist, THEN THE Annotation_Helper SHALL create it with the new query
7. THE Annotation_Helper SHALL validate that the query_id is not already present in the gold file

### Requirement 17: CLI Validate Command

**User Story:** As a developer, I want to validate my gold set and documents, so that I can catch data errors before running evaluation.

#### Acceptance Criteria

1. WHEN spanchor validate is called with documents and gold set, THE CLI_Tool SHALL load and canonicalize all documents
2. WHEN spanchor validate is called, THE CLI_Tool SHALL load and parse the gold set
3. WHEN spanchor validate is called, THE CLI_Tool SHALL validate every anchor against its referenced document
4. WHEN spanchor validate succeeds, THE CLI_Tool SHALL print a success message with counts of documents, queries, and anchors validated
5. WHEN spanchor validate encounters errors, THE CLI_Tool SHALL print all errors with actionable messages and exit with code 2

### Requirement 18: CLI Evaluate Command

**User Story:** As a developer, I want to evaluate retrieval results against a gold set via CLI, so that I can measure pipeline quality from command line or scripts.

#### Acceptance Criteria

1. WHEN spanchor evaluate is called with documents, gold set, and retrieval results, THE CLI_Tool SHALL perform full evaluation
2. WHEN spanchor evaluate is called, THE CLI_Tool SHALL map chunk-text results to spans
3. WHEN spanchor evaluate is called, THE CLI_Tool SHALL compute all metrics for each query and in aggregate
4. WHEN spanchor evaluate is called with --output path, THE CLI_Tool SHALL write the Run to the specified JSON file
5. WHEN spanchor evaluate is called with --report path, THE CLI_Tool SHALL write a markdown report to the specified file
6. WHERE the user specifies --redact, THE CLI_Tool SHALL omit source text from reports
7. WHEN spanchor evaluate completes successfully, THE CLI_Tool SHALL exit with code 0

### Requirement 19: CLI Compare Command

**User Story:** As a developer, I want to compare two runs and enforce regression policy via CLI, so that I can detect quality drops in CI pipelines.

#### Acceptance Criteria

1. WHEN spanchor compare is called with baseline and candidate run files, THE CLI_Tool SHALL load both runs
2. WHEN spanchor compare is called, THE CLI_Tool SHALL compute per-query deltas and statuses
3. WHEN spanchor compare is called, THE CLI_Tool SHALL compute aggregate deltas
4. WHEN spanchor compare is called with --report path, THE CLI_Tool SHALL write a markdown comparison report
5. WHEN spanchor compare is called with --policy path, THE CLI_Tool SHALL load regression policy thresholds from the file
6. WHERE policy flags like --max-recall-drop are provided, THE CLI_Tool SHALL use those thresholds
7. WHEN any query shows REGRESSION status, THE CLI_Tool SHALL exit with code 1
8. WHEN all queries are UNCHANGED or IMPROVED, THE CLI_Tool SHALL exit with code 0
9. WHERE the user specifies --redact, THE CLI_Tool SHALL omit source text from comparison reports

### Requirement 20: CLI Check-Corpus Command

**User Story:** As a developer, I want to verify document corpus health, so that I can detect hash mismatches or offset issues before evaluation.

#### Acceptance Criteria

1. WHEN spanchor check-corpus is called with documents and gold set, THE CLI_Tool SHALL validate every anchor's document hash
2. WHEN spanchor check-corpus is called, THE CLI_Tool SHALL validate every anchor's offset bounds
3. WHEN spanchor check-corpus is called, THE CLI_Tool SHALL validate every anchor's text match at offset
4. WHEN spanchor check-corpus finds issues, THE CLI_Tool SHALL report all mismatches and invalid offsets with document_id and query_id
5. WHEN spanchor check-corpus finds zero issues, THE CLI_Tool SHALL print a success message and exit with code 0
6. WHEN spanchor check-corpus finds issues, THE CLI_Tool SHALL exit with code 2

### Requirement 21: Markdown Report Generation

**User Story:** As a developer, I want human-readable markdown reports, so that I can review evaluation and comparison results in documentation or pull requests.

#### Acceptance Criteria

1. WHEN generating a markdown evaluation report, THE Report_Generator SHALL include aggregate metrics in a table
2. WHEN generating a markdown evaluation report, THE Report_Generator SHALL include per-query metrics in a table
3. WHEN generating a markdown evaluation report, THE Report_Generator SHALL include retrieved character counts
4. WHEN generating a markdown evaluation report, THE Report_Generator SHALL include mapper statistics showing MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, and UNMAPPED counts
5. WHEN generating a markdown comparison report, THE Report_Generator SHALL include a per-query delta table with statuses
6. WHEN generating a markdown comparison report, THE Report_Generator SHALL include an aggregate summary table with deltas
7. WHERE --redact mode is enabled, THE Report_Generator SHALL omit all source text from the report

### Requirement 22: JSON Report Generation

**User Story:** As a developer, I want machine-readable JSON reports, so that I can integrate spanchor results into dashboards and monitoring systems.

#### Acceptance Criteria

1. WHEN generating a JSON evaluation report, THE Report_Generator SHALL include all aggregate metrics
2. WHEN generating a JSON evaluation report, THE Report_Generator SHALL include all per-query metrics
3. WHEN generating a JSON evaluation report, THE Report_Generator SHALL include configuration parameters
4. WHEN generating a JSON comparison report, THE Report_Generator SHALL include per-query deltas and statuses
5. WHEN generating a JSON comparison report, THE Report_Generator SHALL include aggregate deltas
6. WHERE --redact mode is enabled, THE Report_Generator SHALL omit all source text from the JSON report

### Requirement 23: Pytest Integration Helper

**User Story:** As a developer, I want a pytest helper function, so that I can easily assert no regressions in my test suite.

#### Acceptance Criteria

1. THE spanchor.testing module SHALL provide an assert_no_regression function
2. WHEN assert_no_regression is called with baseline and candidate runs and policy thresholds, THE function SHALL compare the runs
3. IF any query shows REGRESSION status, THEN assert_no_regression SHALL raise an AssertionError with clear failure messages listing the regressed queries and metrics
4. IF all queries are UNCHANGED or IMPROVED, THEN assert_no_regression SHALL pass silently
5. THE assert_no_regression failure message SHALL include query_id, metric name, baseline value, candidate value, and delta

### Requirement 24: Small-Sample Warnings

**User Story:** As a developer, I want to be warned about small gold sets, so that I understand when statistical confidence may be low.

#### Acceptance Criteria

1. WHEN a gold set contains fewer than 30 queries, THE Evaluation_Engine SHALL print a warning message indicating statistical confidence may be low
2. THE warning message SHALL include the actual query count
3. THE warning SHALL not prevent evaluation from proceeding

### Requirement 25: Error Type System

**User Story:** As a developer, I want typed exceptions with actionable messages, so that I can quickly diagnose and fix issues.

#### Acceptance Criteria

1. THE system SHALL define InvalidSchemaError for schema and format violations
2. THE system SHALL define DocumentNotFoundError for missing document references
3. THE system SHALL define HashMismatchError for document hash verification failures
4. THE system SHALL define AnchorResolutionError for anchor validation failures
5. THE system SHALL define OrphanedAnchorError for anchors referencing deleted documents
6. THE system SHALL define InvalidRetrievalResultError for malformed retrieval results
7. THE system SHALL define EvaluationError for evaluation computation errors
8. THE system SHALL define ComparisonError for comparison operation errors
9. WHEN any error is raised, THE system SHALL include what happened, the values involved, and a suggested action in the error message

### Requirement 26: Public API Surface

**User Story:** As a developer, I want a clean public API, so that I can programmatically use spanchor in my Python code.

#### Acceptance Criteria

1. THE spanchor module SHALL export the Anchor class
2. THE spanchor module SHALL export the Document class
3. THE spanchor module SHALL export the Query class
4. THE spanchor module SHALL export the evaluate function
5. THE spanchor module SHALL export the compare function
6. THE spanchor module SHALL export the check_corpus function
7. THE spanchor module SHALL export all error classes
8. THE spanchor.testing module SHALL export the assert_no_regression function

### Requirement 27: Retriever Protocol Adapter

**User Story:** As a developer, I want a documented protocol for integrating custom retrievers, so that I can adapt spanchor to my retriever without tight coupling.

#### Acceptance Criteria

1. THE spanchor.adapters module SHALL define a RetrieverProtocol with a retrieve method
2. THE RetrieverProtocol SHALL specify that retrieve accepts a query string and returns a list of Retrieval_Result objects
3. THE spanchor documentation SHALL include examples of implementing the RetrieverProtocol
4. THE RetrieverProtocol SHALL be minimal and require no framework dependencies
