"""Backward compatibility tests for metric registry.

Verifies that the new metric registry produces byte-for-byte identical
results to v0.3.0 when using the default registry.
"""

from spanchor.canonical.normalize import compute_hash
from spanchor.evaluation.engine import evaluate
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult


class TestMetricRegistryBackwardCompatibility:
    """Test backward compatibility with v0.3.0 evaluation results."""

    def test_evaluate_with_no_registry_parameter_produces_same_results(self):
        """Test that omitting metric_registry parameter produces same results."""
        doc = Document.from_text("doc1", "The quick brown fox jumps over the lazy dog.")
        text_hash = compute_hash("quick brown fox")
        anchor = Anchor("doc1", 4, 19, text_hash)
        query = Query("q1", "What animal is quick?", (anchor,))
        result = RetrievalResult(rank=1, score=0.88, text="quick brown fox")

        # Evaluate without metric_registry parameter (v0.3.0 style)
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            min_overlap=0.5,
            max_unmapped_rate=0.1,
            ambiguity_policy="first_unclaimed",
            aggregation_method="macro",
        )

        # Should have all 5 standard metrics
        q_metrics = run.per_query_metrics["q1"]
        assert "recall@5" in q_metrics
        assert "precision@5" in q_metrics
        assert "hit@5" in q_metrics
        assert "full_evidence@5" in q_metrics
        assert "iou" in q_metrics

        # Values should be as expected for perfect match
        assert q_metrics["recall@5"] == 1.0
        assert q_metrics["precision@5"] == 1.0
        assert q_metrics["hit@5"] == 1
        assert q_metrics["full_evidence@5"] == 1
        assert q_metrics["iou"] == 1.0

    def test_evaluate_multiple_queries_produces_consistent_metrics(self):
        """Test evaluate with multiple queries produces consistent aggregates."""
        doc = Document.from_text("doc1", "Alpha Beta Gamma Delta Epsilon Zeta Eta")

        # Query 1: "Alpha Beta"
        anchor1 = Anchor("doc1", 0, 10, compute_hash("Alpha Beta"))
        query1 = Query("q1", "What?", (anchor1,))
        result1 = RetrievalResult(rank=1, score=0.9, text="Alpha Beta")

        # Query 2: "Gamma Delta"
        anchor2 = Anchor("doc1", 11, 22, compute_hash("Gamma Delta"))
        query2 = Query("q2", "What?", (anchor2,))
        result2 = RetrievalResult(rank=1, score=0.85, text="Gamma Delta")

        run = evaluate(
            documents={"doc1": doc},
            queries=[query1, query2],
            retrieval_results={"q1": [result1], "q2": [result2]},
            k=5,
        )

        # Both queries should have perfect metrics
        assert run.per_query_metrics["q1"]["recall@5"] == 1.0
        assert run.per_query_metrics["q2"]["recall@5"] == 1.0

        # Aggregate should be 1.0 (macro average of two 1.0s)
        assert run.aggregate_metrics["mean_recall@5"] == 1.0

    def test_evaluate_with_partial_recall_consistent(self):
        """Test partial recall computation is consistent."""
        doc = Document.from_text("doc1", "0123456789ABCDEFGHIJ")

        # Gold: "0123456789" (10 chars at 0-10)
        anchor = Anchor("doc1", 0, 10, compute_hash("0123456789"))
        query = Query("q1", "What?", (anchor,))

        # Retrieved: "01234" (5 chars at 0-5)
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Recall should be 5/10 = 0.5
        assert run.per_query_metrics["q1"]["recall@5"] == 0.5
        # Precision should be 5/5 = 1.0
        assert run.per_query_metrics["q1"]["precision@5"] == 1.0

    def test_evaluate_with_custom_k_parameter_works(self):
        """Test that custom k parameter works correctly."""
        doc = Document.from_text("doc1", "Test")
        anchor = Anchor("doc1", 0, 4, compute_hash("Test"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=4)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=3,  # Custom k
        )

        # Should have metrics for k=3
        q_metrics = run.per_query_metrics["q1"]
        assert "recall@3" in q_metrics
        assert "precision@3" in q_metrics
        assert "hit@3" in q_metrics
        assert "full_evidence@3" in q_metrics

    def test_evaluate_with_custom_min_overlap_works(self):
        """Test that custom min_overlap parameter works correctly."""
        doc = Document.from_text("doc1", "0123456789")

        # Gold: full 10 chars
        anchor = Anchor("doc1", 0, 10, compute_hash("0123456789"))
        query = Query("q1", "What?", (anchor,))

        # Retrieved: 6 chars (60% overlap)
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=6)

        # Test with high min_overlap (70%)
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            min_overlap=0.7,
        )

        # Hit should be 0 (60% < 70%)
        assert run.per_query_metrics["q1"]["hit@5"] == 0

        # Test with low min_overlap (50%)
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            min_overlap=0.5,
        )

        # Hit should be 1 (60% >= 50%)
        assert run.per_query_metrics["q1"]["hit@5"] == 1

    def test_evaluate_span_form_results_consistent(self):
        """Test that span-form results produce expected metrics."""
        doc = Document.from_text("doc1", "ABCDEFGHIJ")

        # Gold: "BCDE" (chars 1-5)
        anchor = Anchor("doc1", 1, 5, compute_hash("BCDE"))
        query = Query("q1", "What?", (anchor,))

        # Retrieved: "BCD" (chars 1-4) - 3 char overlap out of 4 gold
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=1, end=4)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Recall: 3/4 = 0.75
        assert run.per_query_metrics["q1"]["recall@5"] == 0.75
        # Precision: 3/3 = 1.0
        assert run.per_query_metrics["q1"]["precision@5"] == 1.0
        # IoU: |overlap| / |union| = 3 / 4 = 0.75
        # Gold: [1, 5), Retrieved: [1, 4)
        # Union: [1, 5) = 4 chars
        # Intersection: [1, 4) = 3 chars
        # IoU = 3/4 = 0.75
        iou_result = run.per_query_metrics["q1"]["iou"]
        assert abs(iou_result - 0.75) < 0.001
