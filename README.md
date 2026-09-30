# SPANCHOR

**Regression-test your RAG retrieval pipeline against stable source-document anchors, not fragile chunk IDs.**

SPANCHOR is a Python library and CLI tool for regression-testing RAG retrieval systems. Instead of comparing chunk IDs or chunk boundaries, SPANCHOR anchors expected evidence to character spans in canonical source documents and evaluates retrieved results against those stable source anchors.

**Core Principle:** Separate SOURCE EVIDENCE from RETRIEVAL REPRESENTATION.

## Problem

Traditional retrieval evaluation couples gold labels to implementation details:
- Chunk IDs change when chunking strategy changes
- Chunk boundaries shift with overlap or chunk-size adjustments
- Comparing "did we get chunk c_0042?" breaks silently when pipeline changes

SPANCHOR decouples gold labels from retrieval representation. Expected evidence is anchored to character positions in canonical source documents. Any retrieval output (chunks or spans) is mapped back to source positions and evaluated against the expected evidence.

This lets you change your retriever, chunking, ranking, or indexing strategy and still measure whether the retrieval outcome still covers the same source evidence.

## Key Features

- **Stable Source Anchors**: Gold labels point to character spans in canonical documents (NFC-normalized, hash-verified)
- **Character-Level Metrics**: Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU for span coverage
- **Chunk-to-Source Mapping**: Automatically maps chunk-text retrieval results back to source spans
- **Per-Query Regression Detection**: Detects when individual queries degrade below configured thresholds
- **CI-Ready**: Exit codes (0=pass, 1=regression, 2=error, 3=unmapped-rate exceeded)
- **Local-First**: No network calls, no telemetry, no API keys
- **Deterministic**: Character offsets on canonical text, reproducible span algebra

## Installation

```bash
pip install spanchor
```

For development:

```bash
git clone https://github.com/Mukeshram-07/spanchor.git
cd spanchor
pip install -e ".[dev]"
```

## Quick Start

### 1. Validate Your Document Corpus

```bash
spanchor validate docs/ gold.jsonl
```

Checks that all anchors resolve to the expected text in their source documents.

### 2. Evaluate Retrieval Results

```bash
spanchor evaluate docs/ gold.jsonl results.json --report evaluation.md
```

Computes Recall@K, Precision@K, Hit@K, FullEvidence@K, and IoU for each query. Generates a markdown report.

### 3. Compare Baseline vs Candidate

```bash
spanchor compare baseline.json candidate.json --policy policy.json --report comparison.md
```

Detects per-query regressions using configurable thresholds. Exits with code 0 (pass) or 1 (regression).

### 4. Find Text for Anchoring

```bash
spanchor locate "search phrase" docs/
```

Finds matching text spans in documents to help create anchors.

## Core Concepts

| Term | Meaning |
|------|---------|
| **Document** | A source file with canonical text (NFC-normalized, hash-verified) |
| **Canonical Text** | Unicode text in NFC form with normalized newlines (\r\n and \r → \n) |
| **Span** | Half-open character interval [start, end) in canonical text |
| **Anchor** | Links a query to expected source evidence: {document_id, start, end, hash} |
| **Gold Set** | Collection of anchors for validated evaluation questions |
| **Retrieval Result** | Retrieved chunk text, ranked by retriever |
| **Evaluation Run** | Per-query metrics (Recall@K, Precision@K, etc.) for a single run |
| **Baseline** | Established retrieval performance (before change) |
| **Candidate** | New retrieval performance (after change) |
| **Regression** | Query where candidate performance falls below baseline by policy threshold |
| **Regression Policy** | Per-metric max_drop thresholds (e.g., {"recall@5": 0.05, "precision@5": 0.05}) |

## Metrics

All metrics operate on character-level span coverage:

- **Recall@K**: Fraction of gold evidence characters covered by top-K retrieved spans: |G ∩ R| / |G|
- **Precision@K**: Fraction of retrieved characters that overlap gold: |G ∩ R| / |R|
- **Hit@K**: Whether at least one gold span has ≥50% character overlap with retrieved spans
- **FullEvidence@K**: Whether ALL gold spans meet ≥50% character overlap
- **IoU**: Intersection-over-union of gold and retrieved spans for diagnostic overlap analysis

Metrics are computed per-query. Aggregate metrics (mean, std, min, max) are reported for trends and diagnostics but do not drive the regression gate. Regression detection operates on per-query deltas.

## CLI Reference

```bash
spanchor --help
```

Shows all commands. Each command has detailed help:

```bash
spanchor validate --help
spanchor evaluate --help
spanchor compare --help
spanchor locate --help
spanchor check-corpus --help
spanchor anchor --help
```

### Exit Codes

- **0**: Success (evaluate, validate) or no regressions (compare)
- **1**: Regressions detected (compare)
- **2**: Schema error or usage error
- **3**: Unmapped chunk rate exceeded (evaluate)

## Regression Testing Workflow

1. **Establish Baseline**: Run evaluate on current retriever
   ```bash
   spanchor evaluate docs/ gold.jsonl current_results.json -o baseline.json
   ```

2. **Make a Change**: Modify retriever, chunking, ranking, etc.

3. **Evaluate Candidate**: Run same gold set against modified pipeline
   ```bash
   spanchor evaluate docs/ gold.jsonl new_results.json -o candidate.json
   ```

4. **Compare & Gate**: Detect per-query regressions
   ```bash
   spanchor compare baseline.json candidate.json --policy policy.json
   ```

5. **CI Decision**: Exit code determines pass/fail
   - Exit 0: Changes safe (no regressions)
   - Exit 1: Regressions detected (block deployment)

## Integration with RAG Pipelines

SPANCHOR evaluates the **retrieval stage** of RAG systems. It does not replace:

- Your vector database or retriever
- Embedding models
- Chunking strategy or document processor
- LLM or answer-generation layer
- RAG framework

Typical integration:

```
Existing RAG → Retriever → Retrieved Chunks
                                    ↓
                        SPANCHOR Evaluation
                                    ↓
                        Map to Source Spans
                                    ↓
                        Compute Metrics
                                    ↓
                        Compare Baseline/Candidate
                                    ↓
                        Regression Gate → CI Pass/Fail
```

SPANCHOR integrates as a post-retrieval evaluation layer. It takes retrieved chunks and maps them back to source document spans for evaluation.

## Design Principles

### Source Anchors Are Stable (With Caveats)

Source anchors remain stable as long as:
- The canonical source document text does not change
- Document identity (doc_id) remains consistent

If the source document is updated, anchors need to be recreated. If a document is renamed or removed, anchors become orphaned.

### Per-Query Regression Detection

Regression detection operates on **per-query metrics**, not aggregates.

Example:
- Query 1: Recall drops from 0.8 → 0.7 (policy: max 0.05 drop) → **REGRESSION**
- Query 2: Recall improves from 0.5 → 0.9 → **IMPROVED**
- Query 3: Recall unchanged → **UNCHANGED**

Result: Exit 1 (regression detected). Aggregate mean might still be 0.8, but the gate catches the per-query drop.

### Local, Deterministic, Offline

- Character offsets are absolute positions in canonical text
- Text normalization (NFC, newlines) is deterministic
- Span algebra (union, intersection) is deterministic
- No external services, embeddings, or LLM calls
- Reproducible results for CI/CD

## Example: Changing Chunk Size

### Scenario

**Baseline Pipeline:**
- Chunk size: 250 characters
- Overlap: 0

**Candidate Pipeline:**
- Chunk size: 200 characters
- Overlap: 50

Chunks have different boundaries. Traditional chunk-ID comparison fails silently.

**SPANCHOR Approach:**

1. Gold set: Anchors to source character spans (e.g., "Getting Started" section is [120, 450))
2. Baseline retrieval returns: chunks c_0 and c_1
3. SPANCHOR maps: c_0 and c_1 → spans [100, 300) and [280, 450)
4. Evaluation: Recall@5 = covered / total
5. Candidate retrieval returns: chunks c_0, c_1, c_2 (different boundaries)
6. SPANCHOR maps: c_0, c_1, c_2 → spans [110, 310), [270, 430), [420, 470)
7. Evaluation: Recall@5 = covered / total
8. Comparison: If coverage drops, regression detected

The evaluation remains stable even though chunk boundaries shifted.

## Project Status

SPANCHOR v0.1.0 is the initial public release. It establishes the core source-anchored retrieval evaluation workflow and is ready for experimentation and integration.

v0.1.0 covers:
- Stable source-document anchors
- Character-level span coverage metrics
- Baseline/candidate comparison
- Per-query regression detection
- Chunk-to-source mapping with policy handling
- CLI workflows
- Markdown and JSON reporting

## Non-Goals

SPANCHOR is NOT:

- A RAG framework or orchestrator
- A vector database or retriever implementation
- An embedding service or model
- A document parser or OCR tool
- An LLM provider or answer-generation system
- An answer-quality evaluator (rates generated answers)
- An observability or dashboarding platform
- An agent framework

SPANCHOR focuses exclusively on **retrieval evaluation** and **regression testing** of the retrieval stage.

## License

SPANCHOR is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Repository

- **GitHub**: https://github.com/Mukeshram-07/spanchor
- **PyPI**: https://pypi.org/project/spanchor/

## Contributing

Contributions are welcome. Please open an issue or pull request on GitHub.

---

For more details, see the [examples/real_world_validation/](examples/real_world_validation/) directory for a complete working example.
