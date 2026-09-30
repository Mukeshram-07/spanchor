# Spanchor

**Regression-testing for RAG retrieval pipelines using stable source-document anchors.**

## Overview

Spanchor is a Python library and CLI tool that enables deterministic, regression-testing for RAG retrieval systems. Instead of relying on fragile chunk IDs, spanchor anchors gold labels to character spans in canonical source documents, then evaluates any retriever output against those stable anchors.

**Core Principle:** Separate SOURCE EVIDENCE from RETRIEVAL REPRESENTATION.

## Key Features

- 🎯 **Stable Anchors**: Gold labels point to character spans in canonical documents (NFC normalized, hash-verified)
- 📊 **Character-Level Metrics**: Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU
- 🔄 **Chunk Mapping**: Automatically maps chunk-text retrieval results back to source spans
- 🚨 **Regression Detection**: Compare baseline vs candidate runs with configurable thresholds
- ✅ **CI-Ready**: Exit codes and markdown reports for easy integration
- 🔒 **Local-First**: No network calls, no telemetry, deterministic operation

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"
```

## Quick Start

```python
from spanchor import Document, Anchor, evaluate

# 1. Create canonical documents
doc = Document.from_text("doc1", "Hello world! This is a test.")

# 2. Create anchors (in practice, use CLI helpers)
anchor = Anchor(
    document_id="doc1",
    start=0,
    end=12,
    expected_text_hash=doc.sha256,
)

# 3. Evaluate retrieval results
# (See full documentation for evaluation API)
```

## CLI Commands

```bash
# Validate gold set against documents
spanchor validate docs/ gold.jsonl

# Evaluate retrieval results
spanchor evaluate docs/ gold.jsonl results.json --report report.md

# Compare baseline vs candidate
spanchor compare baseline.json candidate.json --report comparison.md

# Find text in documents for anchoring
spanchor locate "search text" docs/

# Check corpus health
spanchor check-corpus docs/ gold.jsonl
```

## Requirements

- Python 3.11, 3.12, or 3.13
- Runtime: `typer`, `rich`
- Dev: `pytest`, `hypothesis`, `mypy`, `ruff`

## License

Apache-2.0

## Non-Goals

Spanchor is NOT:
- A RAG framework
- A vector database
- An embedding manager
- A document parser/OCR tool
- An LLM provider integration
- An answer quality evaluator

It's a focused tool for **retrieval** regression testing only.
