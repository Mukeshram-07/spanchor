#!/usr/bin/env python
"""SPANCHOR v0.2.0 Real-World Acceptance Demo.

This script demonstrates:
1. Core SPANCHOR evaluation workflow
2. Generic adapter usage with dict results
3. LangChain adapter usage (if available)
4. Regression detection (FAIL scenario)
5. Non-regressing candidate (PASS scenario)

Run from adoption_demo directory:
    python run_demo.py
"""

import json
import sys
from pathlib import Path

# Use the real_world_validation example as the base data
REAL_WORLD_DIR = Path(__file__).parent.parent / "real_world_validation"


def test_core_imports():
    """Verify core spanchor imports."""
    print("=" * 70)
    print("TASK 1: CORE IMPORTS")
    print("=" * 70)
    try:
        import spanchor

        print(f"[OK] spanchor imported")
        print(f"  Version: {spanchor.__version__}")
        assert spanchor.__version__ == "0.2.0", f"Expected 0.2.0, got {spanchor.__version__}"
        print(f"[OK] Version verified: 0.2.0")

        from spanchor import Document, Anchor, evaluate, compare

        print(f"[OK] Core APIs available: Document, Anchor, evaluate, compare")

        from spanchor.adapters.generic import dict_to_retrieval_result, dicts_to_retrieval_results

        print(
            f"[OK] Generic adapters available: dict_to_retrieval_result, dicts_to_retrieval_results"
        )

        # Try LangChain adapter (may not be installed)
        try:
            from spanchor.adapters.langchain import (
                documents_to_retrieval_results as lc_docs_to_results,
            )

            print(f"[OK] LangChain adapter available (optional dependency installed)")
            langchain_available = True
        except ImportError:
            print(f"SKIP LangChain adapter not available (optional - not installed)")
            langchain_available = False

        # Try LlamaIndex adapter (may not be installed)
        try:
            from spanchor.adapters.llamaindex import (
                nodes_to_retrieval_results as li_nodes_to_results,
            )

            print(f"[OK] LlamaIndex adapter available (optional dependency installed)")
            llamaindex_available = True
        except ImportError:
            print(f"SKIP LlamaIndex adapter not available (optional - not installed)")
            llamaindex_available = False

        return True, langchain_available, llamaindex_available

    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False, False, False


def load_documents(corpus_dir: Path) -> dict:
    """Load and canonicalize corpus documents."""
    from spanchor import Document

    documents = {}
    for file_path in sorted(corpus_dir.glob("*.txt")):
        doc_id = file_path.stem
        text = file_path.read_text(encoding="utf-8")
        doc = Document.from_text(doc_id, text)
        documents[doc_id] = doc
    return documents


def load_gold_set(gold_path: Path) -> list:
    """Load gold queries from JSONL."""
    import json

    from spanchor import Anchor
    from spanchor.models.query import Query

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


def load_retrieval_results(results_path: Path) -> dict:
    """Load retrieval results from JSONL."""
    import json

    from spanchor.models.retrieval import RetrievalResult

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


def test_baseline_run():
    """Run baseline evaluation using real_world_validation data."""
    print("\n" + "=" * 70)
    print("TASK 2: BASELINE RUN")
    print("=" * 70)

    from spanchor import evaluate

    try:
        # Load corpus
        corpus_dir = REAL_WORLD_DIR / "corpus"
        print(f"Loading documents from {corpus_dir}...")
        documents = load_documents(corpus_dir)
        print(f"[OK] Loaded {len(documents)} documents")

        # Load gold set
        gold_file = REAL_WORLD_DIR / "gold.jsonl"
        print(f"Loading gold set from {gold_file}...")
        queries = load_gold_set(gold_file)
        print(f"[OK] Loaded {len(queries)} gold queries with anchors")

        # Load baseline results
        baseline_results_file = REAL_WORLD_DIR / "baseline_results.jsonl"
        print(f"Loading baseline retrieval results from {baseline_results_file}...")
        baseline_results = load_retrieval_results(baseline_results_file)
        print(f"[OK] Loaded baseline results for {len(baseline_results)} queries")

        # Evaluate baseline
        print("Running baseline evaluation...")
        baseline_run = evaluate(
            documents=documents,
            queries=queries,
            retrieval_results=baseline_results,
            k=5,
        )
        print(f"[OK] Baseline evaluation complete")

        # Extract metrics
        print(f"\nBaseline Metrics (aggregate):")
        baseline_agg = baseline_run.aggregate_metrics
        print(f"  Recall@5:    {baseline_agg.get('mean_recall@5', 0):.3f}")
        print(f"  Precision@5: {baseline_agg.get('mean_precision@5', 0):.3f}")
        print(f"  Hit@5:       {baseline_agg.get('mean_hit@5', 0):.3f}")

        # Count queries and stats
        num_queries = len(baseline_run.per_query_metrics)
        print(f"  Queries evaluated: {num_queries}")

        return True, baseline_run, documents, queries

    except Exception as e:
        print(f"[FAIL] Baseline run failed: {e}")
        import traceback

        traceback.print_exc()
        return False, None, None, None


def test_candidate_run_regression():
    """Run candidate evaluation that SHOULD regress."""
    print("\n" + "=" * 70)
    print("TASK 3: CANDIDATE RUN (REGRESSION SCENARIO)")
    print("=" * 70)

    from spanchor import evaluate

    try:
        # Load corpus
        corpus_dir = REAL_WORLD_DIR / "corpus"
        documents = load_documents(corpus_dir)

        # Load gold set
        gold_file = REAL_WORLD_DIR / "gold.jsonl"
        queries = load_gold_set(gold_file)

        # Load candidate results (this is the regressing version)
        candidate_results_file = REAL_WORLD_DIR / "candidate_results.jsonl"
        print(f"Loading candidate retrieval results from {candidate_results_file}...")
        candidate_results = load_retrieval_results(candidate_results_file)
        print(f"[OK] Loaded candidate results for {len(candidate_results)} queries")

        # Evaluate candidate
        print("Running candidate evaluation...")
        candidate_run = evaluate(
            documents=documents,
            queries=queries,
            retrieval_results=candidate_results,
            k=5,
        )
        print(f"[OK] Candidate evaluation complete")

        # Extract metrics
        print(f"\nCandidate Metrics (aggregate):")
        candidate_agg = candidate_run.aggregate_metrics
        print(f"  Recall@5:    {candidate_agg.get('mean_recall@5', 0):.3f}")
        print(f"  Precision@5: {candidate_agg.get('mean_precision@5', 0):.3f}")
        print(f"  Hit@5:       {candidate_agg.get('mean_hit@5', 0):.3f}")

        return True, candidate_run

    except Exception as e:
        print(f"[FAIL] Candidate run failed: {e}")
        import traceback

        traceback.print_exc()
        return False, None


def test_candidate_run_passing():
    """Run candidate evaluation that should NOT regress."""
    print("\n" + "=" * 70)
    print("TASK 4: CANDIDATE RUN (PASSING SCENARIO)")
    print("=" * 70)

    from spanchor import evaluate

    try:
        # Load corpus
        corpus_dir = REAL_WORLD_DIR / "corpus"
        documents = load_documents(corpus_dir)

        # Load gold set
        gold_file = REAL_WORLD_DIR / "gold.jsonl"
        queries = load_gold_set(gold_file)

        # Load passing candidate results
        candidate_passing_file = REAL_WORLD_DIR / "candidate_passing_results.jsonl"
        print(f"Loading passing candidate results from {candidate_passing_file}...")
        candidate_passing_results = load_retrieval_results(candidate_passing_file)
        print(f"[OK] Loaded passing candidate results for {len(candidate_passing_results)} queries")

        # Evaluate candidate
        print("Running candidate evaluation...")
        candidate_passing_run = evaluate(
            documents=documents,
            queries=queries,
            retrieval_results=candidate_passing_results,
            k=5,
        )
        print(f"[OK] Candidate evaluation complete")

        # Extract metrics
        print(f"\nCandidate (Passing) Metrics (aggregate):")
        candidate_agg = candidate_passing_run.aggregate_metrics
        print(f"  Recall@5:    {candidate_agg.get('mean_recall@5', 0):.3f}")
        print(f"  Precision@5: {candidate_agg.get('mean_precision@5', 0):.3f}")
        print(f"  Hit@5:       {candidate_agg.get('mean_hit@5', 0):.3f}")

        return True, candidate_passing_run

    except Exception as e:
        print(f"[FAIL] Candidate passing run failed: {e}")
        import traceback

        traceback.print_exc()
        return False, None


def test_regression_detection_fail(baseline_run, candidate_run):
    """Test regression detection (FAIL scenario)."""
    print("\n" + "=" * 70)
    print("TASK 5: REGRESSION DETECTION (EXPECT FAILURE)")
    print("=" * 70)

    from spanchor import compare

    try:
        # Define policy
        policy = {
            "recall@5": 0.05,  # Allow ≤5% drop in individual query recall
            "precision@5": 0.05,  # Allow ≤5% drop in individual query precision
        }
        print(f"Policy: {policy}")

        # Compare
        print("Running comparison...")
        comparison = compare(
            baseline=baseline_run,
            candidate=candidate_run,
            policy=policy,
        )
        print(f"[OK] Comparison complete")

        # Check results
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

        print(f"\nComparison Results:")
        print(f"  Has Regression: {comparison.has_regression}")
        print(f"  Improved queries: {improved}")
        print(f"  Unchanged queries: {unchanged}")
        print(f"  Regressed queries: {regressed}")

        if comparison.has_regression:
            print(f"\n[OK] REGRESSION DETECTED (as expected)")
            exit_code = 1
        else:
            print(f"\n[FAIL] No regression detected (unexpected)")
            exit_code = 0

        return exit_code, comparison

    except Exception as e:
        print(f"[FAIL] Regression detection failed: {e}")
        import traceback

        traceback.print_exc()
        return 2, None


def test_regression_detection_pass(baseline_run, candidate_passing_run):
    """Test regression detection (PASS scenario)."""
    print("\n" + "=" * 70)
    print("TASK 6: REGRESSION DETECTION (EXPECT PASS)")
    print("=" * 70)

    from spanchor import compare

    try:
        # Define policy
        policy = {
            "recall@5": 0.05,  # Allow ≤5% drop in individual query recall
            "precision@5": 0.05,  # Allow ≤5% drop in individual query precision
        }
        print(f"Policy: {policy}")

        # Compare
        print("Running comparison...")
        comparison_pass = compare(
            baseline=baseline_run,
            candidate=candidate_passing_run,
            policy=policy,
        )
        print(f"[OK] Comparison complete")

        # Check results
        improved = 0
        unchanged = 0
        regressed = 0

        for qid, status in comparison_pass.per_query_status.items():
            if status == "IMPROVED":
                improved += 1
            elif status == "UNCHANGED":
                unchanged += 1
            else:  # REGRESSION
                regressed += 1

        print(f"\nComparison Results:")
        print(f"  Has Regression: {comparison_pass.has_regression}")
        print(f"  Improved queries: {improved}")
        print(f"  Unchanged queries: {unchanged}")
        print(f"  Regressed queries: {regressed}")

        if not comparison_pass.has_regression:
            print(f"\n[OK] NO REGRESSION (as expected)")
            exit_code = 0
        else:
            print(f"\n[FAIL] Regression detected (unexpected)")
            exit_code = 1

        return exit_code, comparison_pass

    except Exception as e:
        print(f"[FAIL] Regression detection failed: {e}")
        import traceback

        traceback.print_exc()
        return 2, None


def test_generic_adapter():
    """Test generic adapter with dict results."""
    print("\n" + "=" * 70)
    print("TASK 7: GENERIC ADAPTER TEST")
    print("=" * 70)

    from spanchor.adapters.generic import dict_to_retrieval_result, dicts_to_retrieval_results

    try:
        # Test dict_to_retrieval_result
        result_dict = {
            "text": "Important passage about feature X",
            "score": 0.95,
            "rank": 1,
            "document_id": "doc1",
            "metadata_field": "extra_info",
        }
        print(f"Converting dict: {result_dict}")
        result = dict_to_retrieval_result(result_dict)
        print(f"[OK] Converted to RetrievalResult")
        print(f"  rank={result.rank}, score={result.score}, doc_id={result.document_id}")
        print(f"  text={result.text[:30]}..., metadata={result.metadata}")

        # Test dicts_to_retrieval_results
        dicts = [
            {"text": "First result", "score": 0.95, "document_id": "doc1"},
            {"text": "Second result", "score": 0.80, "document_id": "doc2"},
            {"text": "Third result", "score": 0.70, "document_id": "doc1"},
        ]
        print(f"\nConverting list of {len(dicts)} dicts...")
        results = dicts_to_retrieval_results(dicts)
        print(f"[OK] Converted to list of RetrievalResults")
        for r in results:
            print(f"  rank={r.rank}, score={r.score}, text={r.text[:20]}...")

        print(f"\n[OK] Generic adapter verified")
        return True

    except Exception as e:
        print(f"[FAIL] Generic adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_langchain_adapter():
    """Test LangChain adapter if available."""
    print("\n" + "=" * 70)
    print("TASK 8: LANGCHAIN ADAPTER TEST")
    print("=" * 70)

    try:
        from langchain_core.documents import Document as LCDocument
        from spanchor.adapters.langchain import documents_to_retrieval_results

        print("LangChain available, testing adapter...")

        # Create sample LangChain documents
        lc_docs = [
            LCDocument(
                page_content="This is a passage about APIs",
                metadata={"source": "api_docs.txt", "relevance_score": 0.92},
            ),
            LCDocument(
                page_content="This is about authentication",
                metadata={"source": "security.txt", "relevance_score": 0.85},
            ),
        ]
        print(f"Created {len(lc_docs)} LangChain Document objects")

        # Convert to SPANCHOR format
        results = documents_to_retrieval_results(lc_docs)
        print(f"[OK] Converted to RetrievalResults")
        for i, r in enumerate(results):
            print(f"  [{i+1}] rank={r.rank}, score={r.score}, doc={r.document_id}")

        print(f"\n[OK] LangChain adapter verified")
        return True

    except ImportError:
        print("SKIP LangChain not installed (optional dependency)")
        print("  To test: pip install langchain langchain-core")
        return None

    except Exception as e:
        print(f"[FAIL] LangChain adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_llamaindex_adapter():
    """Test LlamaIndex adapter if available."""
    print("\n" + "=" * 70)
    print("TASK 9: LLAMAINDEX ADAPTER TEST")
    print("=" * 70)

    try:
        from llama_index.schema import NodeWithScore, TextNode
        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        print("LlamaIndex available, testing adapter...")

        # Create sample LlamaIndex nodes
        node1 = TextNode(text="This is a retrieval result from LlamaIndex")
        node1_with_score = NodeWithScore(node=node1, score=0.89)

        node2 = TextNode(text="Another result from the index")
        node2_with_score = NodeWithScore(node=node2, score=0.76)

        nodes = [node1_with_score, node2_with_score]
        print(f"Created {len(nodes)} LlamaIndex NodeWithScore objects")

        # Convert to SPANCHOR format
        results = nodes_to_retrieval_results(nodes)
        print(f"[OK] Converted to RetrievalResults")
        for i, r in enumerate(results):
            print(f"  [{i+1}] rank={r.rank}, score={r.score}, text={r.text[:30]}...")

        print(f"\n[OK] LlamaIndex adapter verified")
        return True

    except ImportError:
        print("SKIP LlamaIndex not installed (optional dependency)")
        print("  To test: pip install llama-index llama-index-core")
        return None

    except Exception as e:
        print(f"[FAIL] LlamaIndex adapter test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all acceptance tests."""
    print("\n")
    print("=" * 70)
    print("SPANCHOR v0.2.0 Real-World Acceptance Test".center(70))
    print("=" * 70)
    print()

    # TASK 1: Core imports
    imports_ok, lc_available, li_available = test_core_imports()
    if not imports_ok:
        print("\n[FAIL] Core imports failed - cannot proceed")
        return 2

    # TASK 2: Baseline run
    baseline_ok, baseline_run, documents, queries = test_baseline_run()
    if not baseline_ok:
        print("\n[FAIL] Baseline run failed")
        return 2

    # TASK 3: Candidate run (regression)
    candidate_ok, candidate_run = test_candidate_run_regression()
    if not candidate_ok:
        print("\n[FAIL] Candidate run (regression) failed")
        return 2

    # TASK 4: Candidate run (passing)
    candidate_passing_ok, candidate_passing_run = test_candidate_run_passing()
    if not candidate_passing_ok:
        print("\n[FAIL] Candidate run (passing) failed")
        return 2

    # TASK 5: Regression detection (FAIL)
    fail_exit_code, comparison_fail = test_regression_detection_fail(baseline_run, candidate_run)

    # TASK 6: Regression detection (PASS)
    pass_exit_code, comparison_pass = test_regression_detection_pass(
        baseline_run, candidate_passing_run
    )

    # TASK 7: Generic adapter
    generic_ok = test_generic_adapter()

    # TASK 8: LangChain adapter
    langchain_ok = test_langchain_adapter()

    # TASK 9: LlamaIndex adapter
    llamaindex_ok = test_llamaindex_adapter()

    # Summary
    print("\n" + "=" * 70)
    print("ACCEPTANCE TEST SUMMARY")
    print("=" * 70)
    print(f"\n[OK] Core imports verified (v0.2.0)")
    print(f"[OK] Baseline evaluation run: {len(baseline_run.per_query_metrics)} queries")
    print(
        f"[OK] Candidate evaluation run (regression scenario): {len(candidate_run.per_query_metrics)} queries"
    )
    print(
        f"[OK] Candidate evaluation run (passing scenario): {len(candidate_passing_run.per_query_metrics)} queries"
    )
    print(
        f"[OK] Regression detection (FAIL scenario): has_regression={comparison_fail.has_regression} (exit={fail_exit_code})"
    )
    print(
        f"[OK] Regression detection (PASS scenario): has_regression={comparison_pass.has_regression} (exit={pass_exit_code})"
    )
    print(f"[OK] Generic adapter: {'PASSED' if generic_ok else 'FAILED'}")
    print(
        f"[OK] LangChain adapter: {'PASSED' if langchain_ok is True else 'SKIPPED (optional)' if langchain_ok is None else 'FAILED'}"
    )
    print(
        f"[OK] LlamaIndex adapter: {'PASSED' if llamaindex_ok is True else 'SKIPPED (optional)' if llamaindex_ok is None else 'FAILED'}"
    )

    print(f"\n{'=' * 70}")

    # Determine final result
    all_core_ok = (
        imports_ok
        and baseline_ok
        and candidate_ok
        and candidate_passing_ok
        and generic_ok
        and fail_exit_code == 1  # Regression scenario should exit 1
        and pass_exit_code == 0  # Passing scenario should exit 0
    )

    if all_core_ok:
        print("\nPASS REAL-WORLD ACCEPTANCE: PASSED — READY FOR FINAL RELEASE REVIEW")
        print()
        return 0
    else:
        print("\nFAIL REAL-WORLD ACCEPTANCE: FAILED — FIXES REQUIRED")
        print()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
