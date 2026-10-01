<div align="center">
  <img src="https://i.ibb.co/W4dJCkjH/Chat-GPT-Image-Sep-30-2026-11-35-30-PM.png" alt="SPANCHOR logo" width="300" />
</div>

# SPANCHOR

[![PyPI](https://img.shields.io/pypi/v/spanchor)](https://pypi.org/project/spanchor/)
[![Python](https://img.shields.io/pypi/pyversions/spanchor)](https://pypi.org/project/spanchor/)
[![License](https://img.shields.io/pypi/l/spanchor)](LICENSE)
[![CI](https://github.com/Mukeshram-07/spanchor/actions/workflows/ci.yml/badge.svg)](https://github.com/Mukeshram-07/spanchor/actions/workflows/ci.yml)
[![Release](https://github.com/Mukeshram-07/spanchor/actions/workflows/release.yml/badge.svg)](https://github.com/Mukeshram-07/spanchor/actions/workflows/release.yml)

**Regression-test your RAG retrieval pipeline against stable source-document anchors, not fragile chunk IDs.**

SPANCHOR is a Python library and CLI tool for regression-testing RAG retrieval systems. Instead of comparing chunk IDs or chunk boundaries, SPANCHOR anchors expected evidence to character spans in canonical source documents and evaluates retrieved results against those stable source anchors.

## The Problem

When building RAG systems, retrieval quality can degrade unexpectedly:
- Changing chunk size breaks chunk-ID-based evaluation
- Modifying overlap or indexing strategy invalidates chunk boundaries
- Comparing results using chunk IDs doesn't reflect actual evidence retrieval
- Silent regressions go undetected until users report issues

SPANCHOR decouples evaluation from retrieval implementation by anchoring expected evidence to character positions in canonical source documents. Any retrieval strategy (chunks, spans, reranked results) is mapped back to source evidence and evaluated against stable anchors.

**Result**: Change your chunking, retriever, ranking, or indexing strategy and still measure whether you're retrieving the same source evidence.

## Why Source Anchors?

| Approach | Fragile | Reason |
|----------|---------|--------|
| Chunk IDs | ❌ Yes | IDs change with re-chunking |
| Chunk boundaries | ❌ Yes | Boundaries shift with overlap/size changes |
| Embedding similarity | ❌ Yes | Embeddings change with model updates |
| Source spans | ✅ No | Character positions in canonical text are stable |

SPANCHOR uses character-level spans in canonical source documents. These remain valid across retrieval strategy changes, making evaluation truly configuration-agnostic.

## Key Features

- **Stable Source Anchors**: Gold labels point to character spans in canonical documents (NFC-normalized, hash-verified)
- **Character-Level Metrics**: Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU for span coverage
- **Chunk-to-Source Mapping**: Automatically maps retrieval results back to source spans
- **Per-Query Regression Detection**: Identifies individual queries that degrade beyond thresholds
- **Framework Integrations**: Generic dict, LangChain, LlamaIndex adapters (optional dependencies)
- **CI-Ready**: Exit codes (0=pass, 1=regression, 2=error, 3=unmapped-rate exceeded)
- **Local-First**: No network, no telemetry, no API keys — runs entirely offline
- **Deterministic**: Reproducible span algebra and character-level offsets
- **Type-Safe**: Full mypy --strict compliance

## Installation

### Core Library
```bash
pip install spanchor
```

### With Framework Integrations (Optional)
```bash
# LangChain support
pip install "spanchor[langchain]"

# LlamaIndex support
pip install "spanchor[llamaindex]"

# Development
pip install -e "spanchor[dev]"
```

Core `spanchor` has minimal dependencies (typer, rich). Framework integrations are optional and only loaded when needed.

## Quick Start

### 1. Create a Gold Set

Define expected evidence using source anchors:

```python
from spanchor import Document, Anchor, Query
from spanchor.canonical.normalize import compute_hash

# Load source documents
doc = Document.from_text("doc1", "CloudSync is a cloud storage service...")
documents = {"doc1": doc}

# Define gold question with source anchor
anchor = Anchor(
    document_id="doc1",
    start=0,
    end=36,  # "CloudSync is a cloud storage service"
    expected_text_hash=compute_hash("CloudSync is a cloud storage service")
)
query = Query(query_id="q1", question="What is CloudSync?", anchors=(anchor,))
queries = [query]
```

### 2. Evaluate Retrieval Results

```python
from spanchor import evaluate
from spanchor.adapters.generic import dicts_to_retrieval_results

# Your retrieval results (from any retriever)
results = [
    {"text": "CloudSync is a cloud storage service...", "score": 0.95, "document_id": "doc1"},
]
retrieval_results = {"q1": dicts_to_retrieval_results(results)}

# Evaluate baseline
baseline_run = evaluate(
    documents=documents,
    queries=queries,
    retrieval_results=retrieval_results,
    k=5
)

print(f"Recall@5: {baseline_run.aggregate_metrics['mean_recall@5']:.3f}")
```

### 3. Compare Baseline vs Candidate

```python
from spanchor import compare

# Evaluate candidate configuration
candidate_run = evaluate(documents, queries, candidate_results, k=5)

# Compare and detect regressions
comparison = compare(
    baseline=baseline_run,
    candidate=candidate_run,
    policy={"recall@5": 0.05}  # Allow ≤5% drop per-query
)

if comparison.has_regression:
    print(f"REGRESSION DETECTED")
    print(f"Regressed queries: {sum(1 for s in comparison.per_query_status.values() if s == 'REGRESSION')}")
else:
    print(f"NO REGRESSION")
```

## Real Regression Example

This example is from the validated SPANCHOR test suite (100 queries, 4 technical documents):

### Baseline Configuration
- Chunk size: 250 characters
- Overlap: 0
- Metrics: Recall@5=0.405, Hit@5=0.410

### Candidate Configuration (Regressed)
- Chunk size: 200 characters (smaller)
- Overlap: 50 characters (added overlap)
- Metrics: Recall@5=0.249, Hit@5=0.260

### Regression Result
```
Baseline Recall:  0.405
Candidate Recall: 0.249
Drop:             -0.156 (-15.6%)
Policy threshold: 0.05 (-5%)
Result:           REGRESSION (19 queries exceeded threshold)
Exit code:        1
```

Smaller chunks with overlap degraded recall for this corpus because they fragmented evidence across multiple results. SPANCHOR detected this automatically.

## Metrics

SPANCHOR computes character-level overlap metrics:

- **Recall@K**: Fraction of gold evidence characters covered by top-K retrieved spans: |G ∩ R| / |G|
- **Precision@K**: Fraction of retrieved characters overlapping gold: |G ∩ R| / |R|
- **Hit@K**: Whether ≥1 gold span has ≥50% overlap with retrieved spans
- **FullEvidence@K**: Whether ALL gold spans have ≥50% overlap
- **IoU**: Intersection-over-union diagnostic metric

**Important**: SPANCHOR uses **per-query regression detection**:
- Aggregate metrics are computed for trending/reporting
- Regression gate is triggered by individual queries exceeding policy thresholds
- A single query regressing prevents deployment

This prevents aggregate improvements from masking individual query regressions.

## Architecture

```
Your RAG Pipeline
  ├── Retriever → Chunks
  │                  ↓
  │         SPANCHOR Evaluation
  │              ├── Map chunks to source spans
  │              ├── Compute per-query metrics
  │              └── Per-query comparison
  │                  ↓
  │         Regression Gate
  │              ├── Policy thresholds per metric
  │              └── Per-query classification
  │                  ↓
  │         CI Decision (exit 0 or 1)
```

SPANCHOR integrates as a post-retrieval evaluation layer. It takes retrieved text and compares it against source-anchored evidence.

## Framework Integrations

### Generic Dictionary Results
```python
from spanchor.adapters.generic import dicts_to_retrieval_results

results = [
    {"text": "...", "score": 0.95, "document_id": "doc1"},
]
spanchor_results = dicts_to_retrieval_results(results)
```

Supports flexible field names: text/chunk/content/body, score/relevance_score/similarity, etc.

### LangChain
```python
from langchain_community.retrievers import BM25Retriever
from spanchor.adapters.langchain import documents_to_retrieval_results

retriever = BM25Retriever.from_texts(texts)
docs = retriever.invoke("query")
spanchor_results = documents_to_retrieval_results(docs)
```

Install: `pip install "spanchor[langchain]"`

### LlamaIndex
```python
from llama_index.core import SimpleDirectoryReader
from spanchor.adapters.llamaindex import nodes_to_retrieval_results

reader = SimpleDirectoryReader("./data")
docs = reader.load_data()
nodes = retriever.retrieve("query")
spanchor_results = nodes_to_retrieval_results(nodes)
```

Install: `pip install "spanchor[llamaindex]"`

## Integration Example

Full end-to-end adoption demo showing baseline vs candidate comparison:

```bash
cd examples/adoption_demo
python run_demo.py
```

Demo includes:
- Loading 4 technical documents (18KB)
- Evaluating 100 gold queries
- Baseline vs candidate comparison
- Regression detection demonstration
- Exit codes (0 for pass, 1 for regression)

See [examples/adoption_demo/README.md](examples/adoption_demo/README.md) for details.

## CLI Commands

```bash
# Validate documents and anchors
spanchor validate docs/ gold.jsonl

# Evaluate retrieval results
spanchor evaluate docs/ gold.jsonl results.json --report evaluation.md

# Compare baseline vs candidate
spanchor compare baseline.json candidate.json --policy policy.json --report comparison.md

# Locate text for anchoring
spanchor locate "search phrase" docs/

# Check corpus for issues
spanchor check-corpus docs/
```

Exit codes:
- **0**: Success (evaluate, validate) or no regressions (compare)
- **1**: Regressions detected (compare)
- **2**: Schema/usage error
- **3**: Unmapped chunk rate exceeded

## What SPANCHOR Is

✓ Regression-testing framework for RAG retrieval pipelines  
✓ Per-query metric comparison with configurable thresholds  
✓ Source-anchored evaluation (stable across configuration changes)  
✓ Character-level span coverage analysis  
✓ CI-ready with exit codes  
✓ Offline and deterministic  
✓ Framework-agnostic (works with any retriever)  

## What SPANCHOR Is NOT

✗ A retriever (use your own: BM25, embeddings, reranker, etc.)  
✗ An embeddings provider (bring your own model)  
✗ A chunking strategy (use your preferred approach)  
✗ An LLM (needed only for generation, not evaluation)  
✗ A data pipeline (you provide documents and queries)  
✗ Production perfect (alpha/early development)  

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Detailed workflow documentation
- [API Reference](docs/API.md) - Complete API documentation
- [Real-World Example](examples/real_world_validation/README.md) - 100-query validation demo
- [Adoption Guide](examples/adoption_demo/README.md) - Integration patterns

## Development

```bash
git clone https://github.com/Mukeshram-07/spanchor.git
cd spanchor

# Setup
pip install -e ".[dev]"
pre-commit install

# Test
pytest
mypy --strict src/
ruff check src/

# Build
python -m build
```

## Testing

754 tests covering:
- Core evaluation logic
- Metric computation
- Regression detection
- Framework integrations
- CLI commands
- Edge cases and error handling

Run: `pytest -v`

## Roadmap

**v0.2.x (Current)**
- ✅ Generic, LangChain, LlamaIndex adapters
- ✅ Per-query regression detection
- ✅ Full type safety (mypy --strict)
- ✅ Adoption example and guides

**v0.3+**
- Schema versioning improvements
- Advanced policy configurations
- Performance optimizations
- Additional framework adapters

## Contributing

Contributions welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `pytest`, `mypy --strict`, and `ruff` pass
5. Submit a pull request

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.

---

**SPANCHOR**: Regression-test your RAG retrieval quality with confidence.

Created by [Mukeshram-07](https://github.com/Mukeshram-07)

