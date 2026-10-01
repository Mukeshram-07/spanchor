import sys

sys.path.insert(0, "../../src")
import json
from pathlib import Path

from spanchor import Anchor, Document, Query, evaluate
from spanchor.models.retrieval import RetrievalResult

# Load docs
docs = {}
for f in sorted(Path("corpus").glob("*.txt")):
    doc_id = f.stem
    text = f.read_text()
    docs[doc_id] = Document.from_text(doc_id, text)

# Load 1 query
with open("gold.jsonl") as f:
    entry = json.loads(f.readline())
    query_id = entry["query_id"]
    question = entry["question"]
    anchors = tuple(
        Anchor(a["document_id"], a["start"], a["end"], a["expected_text_hash"])
        for a in entry["anchors"]
    )
    query = Query(query_id, question, anchors)

# Load baseline results
baseline_results = {}
with open("baseline_results.jsonl") as f:
    for line in f:
        entry = json.loads(line)
        if entry["query_id"] == query_id:
            baseline_results[query_id] = [
                RetrievalResult(
                    rank=r["rank"],
                    score=r["score"],
                    document_id=r["document_id"],
                    start=r["start"],
                    end=r["end"],
                )
                for r in entry["retrieved"]
            ]
            break

# Evaluate
run = evaluate(docs, [query], baseline_results, k=5)
print("Metrics keys:", list(run.aggregate_metrics.keys()))
for k, v in run.aggregate_metrics.items():
    print(f"  {k}: {v}")
