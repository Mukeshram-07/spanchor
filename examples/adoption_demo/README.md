# SPANCHOR Adoption Demo — Real-World RAG Integration

This demo shows how to integrate SPANCHOR into a real RAG retrieval pipeline.

## What This Demonstrates

1. **Documents** → Load realistic source documents
2. **Chunking** → Create document chunks with known boundaries
3. **Retrieval** → Run two retrieval configurations (baseline vs candidate)
4. **SPANCHOR Evaluation** → Compute metrics for each configuration
5. **Regression Detection** → Compare baseline vs candidate
6. **Regression Report** → Show which queries improved/regressed

## Directory Structure

```
examples/adoption_demo/
├── corpus/                    # Source documents
│   ├── documentation.txt      # Realistic technical documentation
│   ├── api_reference.txt      # API documentation
│   └── troubleshooting.txt    # Troubleshooting guide
├── gold.jsonl                 # 50 gold questions with source anchors
├── run_demo.py                # Main demo script
├── baseline_retriever.py       # Baseline retrieval configuration
├── candidate_retriever.py      # Candidate retrieval configuration
└── README.md                   # This file
```

## Quick Start

### 1. Install SPANCHOR

```bash
pip install spanchor
```

### 2. Run the Demo

```bash
python run_demo.py
```

This will:
- Load documents and create 50 gold questions
- Run baseline retrieval (larger chunks, no overlap)
- Run candidate retrieval (smaller chunks, with overlap)
- Evaluate both against gold labels
- Compare and detect regressions
- Generate a report

### 3. Interpret the Output

```
Documents:       3
Gold queries:    50
Baseline Recall: 0.85
Candidate Recall: 0.78
Regressions:     8
Status:          REGRESSION DETECTED (Exit code: 1)
```

This means:
- Candidate configuration caused regressions in 8 queries
- Overall recall dropped from 85% to 78%
- Configuration change is not recommended without further investigation

## Configuration Changes Demonstrated

### Baseline

- **Chunk Size**: 400 characters
- **Overlap**: 0 (no overlap between chunks)
- **Rationale**: Maximize chunk independence, minimize redundancy

### Candidate

- **Chunk Size**: 250 characters
- **Overlap**: 100 characters
- **Rationale**: Increase granularity, add context overlap

**Expected Outcome**: Smaller chunks + overlap usually improves coverage for short queries but can hurt recall for queries requiring broader context.

## Understanding the Regression

When baseline recall = 0.85 and candidate = 0.78:

1. **Per-Query Analysis**: Some queries now retrieve less relevant evidence
2. **Configuration Dependency**: Smaller chunks don't capture full context for these queries
3. **Threshold Policy**: Policy allows ≤5% per-query drop, but some queries exceed this
4. **Decision**: Baseline is more reliable for this corpus

## How to Use This Demo

### Scenario 1: Accept the Regression

If you believe the candidate configuration is better for other reasons:
- Review which queries regressed
- Add more gold labels for those queries
- Re-run evaluation with improved gold set
- Re-assess regression decision

### Scenario 2: Improve the Candidate

Adjust candidate parameters:
```python
# Try larger chunks with same overlap
chunk_size = 350  # increased
overlap = 100     # same

# Or reduce overlap to preserve context
chunk_size = 250  # same
overlap = 50      # decreased
```

Then re-run: `python run_demo.py --candidate-config new_config.json`

### Scenario 3: Integrate Into Your Pipeline

Adapt the code to your retriever:

```python
from spanchor import evaluate, compare
from spanchor.adapters import dict_to_retrieval_result

# Your retriever
def my_retriever(query, documents, chunk_config):
    chunks = chunked_documents(documents, chunk_config)
    results = your_bm25_or_embedding_search(chunks, query)
    # Convert to SPANCHOR format
    return [dict_to_retrieval_result(r) for r in results]

# Evaluate
baseline_run = evaluate(documents, queries, baseline_results)
candidate_run = evaluate(documents, queries, candidate_results)
comparison = compare(baseline_run, candidate_run, policy)
```

## Key Insights

### Why This Matters

Different chunking strategies can significantly impact retrieval quality:
- Smaller chunks: Better for focused queries, worse for broad queries
- Larger chunks: Better for broad context, worse for finding precise answers
- Overlap: Adds redundancy, helps bridge chunk boundaries, increases size

SPANCHOR makes this visible by comparing source-document performance, not chunk-ID performance.

### Why Not Chunk IDs?

Traditional approach: "Did we retrieve chunk_123?"
- Problem: Changes chunk strategy breaks evaluation
- Problem: Metrics don't reflect actual evidence retrieval

SPANCHOR approach: "Did we retrieve the evidence span [1824:1912]?"
- Benefit: Strategy-agnostic evaluation
- Benefit: Metrics reflect actual retrieval quality
- Benefit: Configuration changes are safely validated

## Integration Examples

### With LangChain

```python
from langchain_community.retrievers import BM25Retriever
from spanchor.adapters.langchain import documents_to_retrieval_results
from spanchor import evaluate

retriever = BM25Retriever.from_texts(chunk_texts)
docs = retriever.invoke("query")
spanchor_results = documents_to_retrieval_results(docs)

run = evaluate(documents, queries, {"query": spanchor_results})
```

### With LlamaIndex

```python
from llama_index.core import SimpleDirectoryReader
from spanchor.adapters.llamaindex import nodes_to_retrieval_results
from spanchor import evaluate

reader = SimpleDirectoryReader("./data")
documents = reader.load_data()
retriever = IndexRetriever(...)
nodes = retriever.retrieve("query")
spanchor_results = nodes_to_retrieval_results(nodes)

run = evaluate(documents, queries, {"query": spanchor_results})
```

### Pure Dict Format

```python
from spanchor.adapters import dicts_to_retrieval_results
from spanchor import evaluate

results = [
    {"text": "chunk1", "score": 0.9, "document": "doc1"},
    {"text": "chunk2", "score": 0.7, "document": "doc1"},
]
spanchor_results = dicts_to_retrieval_results(results)

run = evaluate(documents, queries, {"query": spanchor_results})
```

## Next Steps

1. **Try different chunking parameters** and see how metrics change
2. **Create more gold questions** to improve statistical confidence
3. **Compare multiple strategies** (embedding-based, keyword-based, hybrid)
4. **Integrate into CI** to prevent silent regressions
5. **Track metrics over time** as you improve your retriever

## Questions?

- See [SPANCHOR README](../../README.md) for core concepts
- See [SPANCHOR Documentation](../../docs/) for detailed guides
- Check [real-world-validation](../real_world_validation/) for another example
