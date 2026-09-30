# Spanchor Demo Data

This directory contains example demo data for manual testing and documentation of the spanchor library.

## Directory Structure

```
examples/demo/
├── docs/                    # Source documents
│   ├── intro_to_rag.txt     # Introduction to RAG concepts
│   └── anchor_concepts.txt  # Explanation of anchors and offsets
├── gold.jsonl              # Gold set with 4 queries and anchors
├── baseline.json           # Baseline retrieval run
├── candidate.json          # Candidate retrieval run for comparison
└── README.md              # This file
```

## Demo Data Description

### Source Documents

#### `intro_to_rag.txt`
A concise explanation of Retrieval-Augmented Generation, covering:
- RAG definition and motivation
- Three-stage pipeline: indexing, retrieval, generation
- Why retrieval quality matters

**Size:** ~500 characters
**Used by:** Queries q1, q2

#### `anchor_concepts.txt`
Explanation of the anchor concept in spanchor:
- Anchor definition and stability
- Four fields stored in an anchor
- Unicode code-point offsets and canonicalization

**Size:** ~600 characters
**Used by:** Queries q3, q4

### Gold Set (`gold.jsonl`)

Four queries with validated anchors pointing to relevant evidence spans:

1. **q1**: "What is RAG?"
   - Document: `intro_to_rag`
   - Span: [0, 142)
   - Covers: "Retrieval-Augmented Generation (RAG)..." definition

2. **q2**: "What stages does a RAG pipeline have?"
   - Document: `intro_to_rag`
   - Span: [402, 486)
   - Covers: "A typical RAG pipeline consists of three stages..."

3. **q3**: "What does an anchor store?"
   - Document: `anchor_concepts`
   - Span: [257, 412)
   - Covers: "Every anchor stores four fields..."

4. **q4**: "What are Unicode code-point offsets?"
   - Document: `anchor_concepts`
   - Span: [556, 651)
   - Covers: "Offsets in spanchor are Unicode code-point offsets..."

**Schema:** All queries use `schema_version: 0.1.0` with proper anchor hashing

### Runs

#### `baseline.json`
Baseline retrieval performance (timestamp: 2024-01-15T10:00:00Z):
- **Recall@5:** 0.80 (macro-average)
- **Precision@5:** 0.74
- **Hit@5:** 0.75
- **Full Evidence@5:** 0.50
- **Mapping Stats:** All 4 queries mapped exactly

#### `candidate.json`
Candidate retrieval performance with improvements (timestamp: 2024-01-16T10:00:00Z):
- **Recall@5:** 0.81 (slight improvement)
- **Precision@5:** 0.75
- **Hit@5:** 1.00 (improved)
- **Full Evidence@5:** 0.50 (unchanged)
- **Mapping Stats:** All 4 queries mapped exactly

### Realistic Improvements

The candidate run shows realistic improvements you might see in practice:
- q1: Recall improved from 0.88 → 0.92
- q2: Slight regression (0.75 → 0.70) - shows realistic mixed results
- q3: Recall improved from 0.92 → 0.95 (high baseline, marginal gain)
- q4: Hit@5 improved from 0.0 → 1.0 (significant improvement)

## Usage

### Validate Gold Set
```bash
spanchor validate examples/demo/docs examples/demo/gold.jsonl
```

### Evaluate Retrieval Results
```bash
spanchor evaluate examples/demo/docs examples/demo/gold.jsonl \
  baseline_results.json \
  --output baseline.json \
  --report baseline_report.md
```

### Compare Two Runs
```bash
spanchor compare examples/demo/baseline.json examples/demo/candidate.json \
  --report comparison.md \
  --max-recall-drop 0.05
```

### Locate Text in Documents
```bash
spanchor locate "Unicode code-point offsets" examples/demo/docs
```

### Add New Anchor to Gold Set
```bash
spanchor anchor add q5 "New question?" examples/demo/docs \
  "anchor text" \
  --output examples/demo/gold.jsonl
```

## Extending Demo Data

To add more queries:

1. Create or edit document in `docs/`
2. Run `spanchor locate` to find text
3. Run `spanchor anchor add` to create validated anchor
4. Run `spanchor validate` to ensure integrity

All anchors are validated automatically to ensure:
- Text offsets are within document bounds
- Character hash matches the anchor text
- Document hash hasn't changed
