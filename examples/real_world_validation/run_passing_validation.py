#!/usr/bin/env python3
"""
Test PASSING regression scenario - candidate within acceptable thresholds.

This demonstrates the PASS path: slight configuration change that does NOT
trigger the regression gate.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spanchor import evaluate, compare
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.anchor import Anchor
from spanchor.models.retrieval import RetrievalResult


def load_documents(corpus_dir: Path) -> dict[str, Document]:
    """Load and canonicalize corpus documents."""
    documents = {}
    for file_path in sorted(corpus_dir.glob("*.txt")):
        doc_id = file_path.stem
        text = file_path.read_text(encoding="utf-8")
        doc = Document.from_text(doc_id, text)
        documents[doc_id] = doc
    return documents


def load_gold_set(gold_path: Path) -> list[Query]:
    """Load gold queries from JSONL."""
    queries = []
    with open(gold_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            query_id = entry["query_id"]
            question = entry["question"]
            anchors = []
            for anchor_spec in entry["anchors"]:
                anchor = Anchor(
                    document_id=anchor_spec["document_id"],
                    start=anchor_spec["start"],
                    end=anchor_spec["end"],
                    expected_text_hash=anchor_spec["expected_text_hash"],
                )
                anchors.append(anchor)
            query = Query(query_id, question, tuple(anchors))
            queries.append(query)
    return queries


def load_retrieval_results(results_path: Path) -> dict[str, list[RetrievalResult]]:
    """Load retrieval results from JSONL."""
    query_results = {}
    with open(results_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            query_id = entry["query_id"]
            results = []
            for retrieved in entry["retrieved"]:
                result = RetrievalResult(
                    rank=retrieved["rank"],
                    score=retrieved["score"],
                    document_id=retrieved["document_id"],
                    start=retrieved["start"],
                    end=retrieved["end"],
                )
                results.append(result)
            query_results[query_id] = results
    return query_results


def main():
    """Run validation with PASSING scenario."""
    script_dir = Path(__file__).parent
    corpus_dir = script_dir / "corpus"
    gold_path = script_dir / "gold.jsonl"
    baseline_path = script_dir / "baseline_results.jsonl"
    candidate_path = script_dir / "candidate_passing_results.jsonl"

    print("=" * 80)
    print("PASSING SCENARIO - Candidate within acceptable thresholds")
    print("=" * 80)
    print()

    # Load documents
    print("[1/4] Loading documents...")
    documents = load_documents(corpus_dir)
    print(f"  -> Loaded {len(documents)} documents")
    print()

    # Load queries
    print("[2/4] Loading gold queries...")
    queries = load_gold_set(gold_path)
    print(f"  -> Loaded {len(queries)} gold queries")
    print()

    # Load retrieval results
    print("[3/4] Loading retrieval results...")
    baseline_results = load_retrieval_results(baseline_path)
    candidate_results = load_retrieval_results(candidate_path)
    print(f"  -> Baseline: {len(baseline_results)} queries")
    print(f"  -> Candidate: {len(candidate_results)} queries (safe config: chunk_size=240, overlap=10)")
    print()

    # Evaluate baseline
    print("[4/4] Evaluating and comparing...")
    baseline_run = evaluate(documents, queries, baseline_results, k=5, max_unmapped_rate=0.1)
    candidate_run = evaluate(documents, queries, candidate_results, k=5, max_unmapped_rate=0.1)

    print(f"Baseline Recall@5:        {baseline_run.aggregate_metrics['mean_recall@5']:.3f}")
    print(f"Candidate Recall@5:       {candidate_run.aggregate_metrics['mean_recall@5']:.3f}")
    print()

    # Compare with conservative policy
    comparison = compare(
        baseline=baseline_run,
        candidate=candidate_run,
        policy={
            "recall@5": 0.05,
            "precision@5": 0.05,
        }
    )

    # Count classifications
    improved = sum(1 for s in comparison.per_query_status.values() if s == "IMPROVED")
    unchanged = sum(1 for s in comparison.per_query_status.values() if s == "UNCHANGED")
    regressed = sum(1 for s in comparison.per_query_status.values() if s == "REGRESSION")

    print(f"Improved:   {improved}")
    print(f"Unchanged:  {unchanged}")
    print(f"Regressed:  {regressed}")
    print()

    has_regression = comparison.has_regression
    print(f"Policy Result: {'FAILED' if has_regression else 'PASSED'}")
    print()

    print("=" * 80)
    print(f"Exit Code: {1 if has_regression else 0}")
    print("=" * 80)

    return 1 if has_regression else 0


if __name__ == "__main__":
    sys.exit(main())
