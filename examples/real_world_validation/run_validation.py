#!/usr/bin/env python3
"""
Real-world validation demo for spanchor using CloudSync documentation.

This script:
1. Validates the gold set against canonical documents
2. Evaluates baseline retrieval results
3. Evaluates candidate retrieval results
4. Compares baseline vs candidate
5. Generates reports
6. Tests CI exit codes
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spanchor import Anchor, Document, compare, evaluate
from spanchor.models.query import Query
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

    with open(gold_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)
            query_id = entry["query_id"]
            question = entry["question"]

            # Create anchors from the anchor specs
            anchors = []
            for anchor_spec in entry["anchors"]:
                anchor = Anchor(
                    document_id=anchor_spec["document_id"],
                    start=anchor_spec["start"],
                    end=anchor_spec["end"],
                    expected_text_hash=anchor_spec["expected_text_hash"],
                )
                anchors.append(anchor)

            query = Query(query_id=query_id, question=question, anchors=tuple(anchors))
            queries.append(query)

    return queries


def load_retrieval_results(results_path: Path) -> dict[str, list[RetrievalResult]]:
    """Load retrieval results from JSONL."""
    query_results = {}

    with open(results_path, encoding="utf-8") as f:
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
    """Run the full validation pipeline."""
    script_dir = Path(__file__).parent
    corpus_dir = script_dir / "corpus"
    gold_path = script_dir / "gold.jsonl"
    baseline_path = script_dir / "baseline_results.jsonl"
    candidate_path = script_dir / "candidate_results.jsonl"

    print("=" * 80)
    print("CLOUDSYNC DOCUMENTATION - REAL-WORLD VALIDATION")
    print("=" * 80)
    print()

    # Step 1: Load documents
    print("[1/5] Loading documents...")
    documents = load_documents(corpus_dir)
    print(f"  -> Loaded {len(documents)} documents")
    for doc_id, doc in documents.items():
        print(f"     {doc_id}: {len(doc.text)} chars, hash={doc.sha256[:16]}...")
    print()

    # Step 2: Load gold queries
    print("[2/5] Loading gold queries...")
    queries = load_gold_set(gold_path)
    print(f"  -> Loaded {len(queries)} gold queries")
    total_anchors = sum(len(q.anchors) for q in queries)
    print(f"  -> Total anchors: {total_anchors}")
    print()

    # Step 3: Load retrieval results
    print("[3/5] Loading retrieval results...")
    baseline_results = load_retrieval_results(baseline_path)
    candidate_results = load_retrieval_results(candidate_path)
    print(f"  -> Baseline: {len(baseline_results)} queries retrieved")
    print(f"  -> Candidate: {len(candidate_results)} queries retrieved")
    print()

    # Step 4: Evaluate baseline
    print("[4/5] Evaluating baseline retrieval...")
    baseline_run = evaluate(
        documents=documents,
        queries=queries,
        retrieval_results=baseline_results,
        k=5,
        max_unmapped_rate=0.1,
    )

    print("  -> Aggregate Metrics (baseline):")
    print(f"     Recall@5:        {baseline_run.aggregate_metrics['mean_recall@5']:.3f}")
    print(f"     Precision@5:     {baseline_run.aggregate_metrics['mean_precision@5']:.3f}")
    print(f"     Hit@5:           {baseline_run.aggregate_metrics['mean_hit@5']:.3f}")
    print(f"     FullEvidence@5:  {baseline_run.aggregate_metrics['mean_full_evidence@5']:.3f}")
    print(f"     Mapping success: {baseline_run.mapper_stats.get('success_rate', 0):.1%}")
    print()

    # Step 5: Evaluate candidate
    print("[5/5] Evaluating candidate retrieval...")
    candidate_run = evaluate(
        documents=documents,
        queries=queries,
        retrieval_results=candidate_results,
        k=5,
        max_unmapped_rate=0.1,
    )

    print("  -> Aggregate Metrics (candidate):")
    print(f"     Recall@5:        {candidate_run.aggregate_metrics['mean_recall@5']:.3f}")
    print(f"     Precision@5:     {candidate_run.aggregate_metrics['mean_precision@5']:.3f}")
    print(f"     Hit@5:           {candidate_run.aggregate_metrics['mean_hit@5']:.3f}")
    print(f"     FullEvidence@5:  {candidate_run.aggregate_metrics['mean_full_evidence@5']:.3f}")
    print(f"     Mapping success: {candidate_run.mapper_stats.get('success_rate', 0):.1%}")
    print()

    # Step 6: Compare runs
    print("[6/6] Comparing baseline vs candidate...")
    # NOTE: Policy keys must match PER-QUERY metric names (not aggregate "mean_" names)
    # spanchor uses per-query regression detection:
    # - Policy threshold applies to individual query deltas, not aggregate
    # - Aggregate deltas are computed for reporting but not for regression gate
    comparison = compare(
        baseline=baseline_run,
        candidate=candidate_run,
        policy={
            "recall@5": 0.05,
            "precision@5": 0.05,
        },
    )

    # Count classifications
    improved = 0
    unchanged = 0
    regressed = 0

    for qid, status in comparison.per_query_status.items():
        if status == "IMPROVED":
            improved += 1
        elif status == "UNCHANGED":
            unchanged += 1
        else:  # REGRESSION
            regressed += 1

    print(f"  -> Improved:   {improved} queries")
    print(f"  -> Unchanged:  {unchanged} queries")
    print(f"  -> Regressed:  {regressed} queries")
    print()

    print("Aggregate Metric Changes (candidate - baseline):")
    deltas = comparison.aggregate_deltas
    print(f"  Recall@5:        {deltas.get('mean_recall@5', 0):+.4f}")
    print(f"  Precision@5:     {deltas.get('mean_precision@5', 0):+.4f}")
    print(f"  Hit@5:           {deltas.get('mean_hit@5', 0):+.4f}")
    print(f"  FullEvidence@5:  {deltas.get('mean_full_evidence@5', 0):+.4f}")
    print()

    # Regression policy result
    has_regression = comparison.has_regression
    print(f"Regression Policy: {'FAILED' if has_regression else 'PASSED'}")
    if has_regression:
        print("  -> Metric deltas exceeded configured thresholds")
    print()

    # Save runs as JSON
    baseline_json = script_dir / "baseline.json"
    candidate_json = script_dir / "candidate.json"

    print(f"Saving baseline run to {baseline_json}...")
    with open(baseline_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": baseline_run.timestamp,
                "aggregate_metrics": baseline_run.aggregate_metrics,
                "mapper_stats": baseline_run.mapper_stats,
            },
            f,
            indent=2,
            default=str,
        )

    print(f"Saving candidate run to {candidate_json}...")
    with open(candidate_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": candidate_run.timestamp,
                "aggregate_metrics": candidate_run.aggregate_metrics,
                "mapper_stats": candidate_run.mapper_stats,
            },
            f,
            indent=2,
            default=str,
        )

    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Documents:        {len(documents)}")
    print(f"Gold queries:     {len(queries)}")
    print(f"Baseline Recall:  {baseline_run.aggregate_metrics['mean_recall@5']:.3f}")
    print(f"Candidate Recall: {candidate_run.aggregate_metrics['mean_recall@5']:.3f}")
    print(f"Change:           {deltas.get('mean_recall@5', 0):+.4f}")
    print(f"Improvements:     {improved}")
    print(f"Regressions:      {regressed}")
    print(f"Status:           {'PASS' if not has_regression else 'FAIL'}")
    print("=" * 80)
    print()

    # Exit code: 0 if no regression, 1 if regression
    exit_code = 1 if has_regression else 0
    print(f"Exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
