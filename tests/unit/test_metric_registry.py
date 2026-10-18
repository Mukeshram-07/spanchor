"""Unit tests for metric registry (Feature 6).

Tests the pluggable metric system that allows custom metric registration
while preserving backward compatibility with the 5 standard metrics.

Key features tested:
- Default registry computes all 5 metrics correctly
- Custom metric registration
- Override existing metric
- Results identical to v0.3.0 (when using default registry)
- Backward compatibility (existing evaluate() calls work unchanged)
"""

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.evaluation.engine import evaluate
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.metrics import MetricDefinition, MetricRegistry
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult


class TestMetricRegistryDefaults:
    """Test default metric registry behavior."""

    def test_default_registry_has_five_metrics(self):
        """Test that default registry contains all 5 standard metrics plus Feature 5 set-wise metrics."""
        registry = MetricRegistry()
        metrics = registry.get_all_metrics()

        # Should have exactly 8 metrics (5 standard + 3 set-wise from Feature 5)
        assert len(metrics) == 8

        # Check all expected metrics are present
        expected_names = {
            "recall@5",
            "precision@5",
            "hit@5",
            "full_evidence@5",
            "iou",
            "span_concentration",  # Feature 5
            "fragmentation_ratio",  # Feature 5
            "pairwise_overlap",  # Feature 5
        }
        actual_names = set(metrics.keys())
        assert actual_names == expected_names

    def test_default_registry_metric_types(self):
        """Test that default metrics have correct result types."""
        registry = MetricRegistry()
        metrics = registry.get_all_metrics()

        # Float metrics
        assert metrics["recall@5"].result_type == float
        assert metrics["precision@5"].result_type == float
        assert metrics["iou"].result_type == float

        # Int metrics
        assert metrics["hit@5"].result_type == int
        assert metrics["full_evidence@5"].result_type == int

    def test_default_registry_computes_recall(self):
        """Test that default registry correctly computes recall@5."""
        registry = MetricRegistry(k=5, min_overlap=0.5)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 5)]

        result = registry.compute_metric(
            metric_name="recall@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # Should compute recall correctly: |overlap| / |gold| = 5 / 10 = 0.5
        assert result == 0.5

    def test_default_registry_computes_precision(self):
        """Test that default registry correctly computes precision@5."""
        registry = MetricRegistry(k=5, min_overlap=0.5)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 5)]

        result = registry.compute_metric(
            metric_name="precision@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # Should compute precision correctly: |overlap| / |retrieved| = 5 / 5 = 1.0
        assert result == 1.0

    def test_default_registry_computes_hit(self):
        """Test that default registry correctly computes hit@5."""
        registry = MetricRegistry(k=5, min_overlap=0.5)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 5)]

        result = registry.compute_metric(
            metric_name="hit@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # Should return 1 (hit) because 5/10 >= 0.5
        assert result == 1

    def test_default_registry_computes_full_evidence(self):
        """Test that default registry correctly computes full_evidence@5."""
        registry = MetricRegistry(k=5, min_overlap=0.5)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 5)]

        result = registry.compute_metric(
            metric_name="full_evidence@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # Should return 1 because 5/10 = 0.5 >= min_overlap (0.5)
        assert result == 1

    def test_default_registry_computes_full_evidence_no_match(self):
        """Test that full_evidence returns 0 when threshold not met."""
        registry = MetricRegistry(k=5, min_overlap=0.8)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 5)]

        result = registry.compute_metric(
            metric_name="full_evidence@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # Should return 0 because 5/10 = 0.5 < min_overlap (0.8)
        assert result == 0

    def test_default_registry_computes_iou(self):
        """Test that default registry correctly computes IoU."""
        registry = MetricRegistry()

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(5, 15)]

        result = registry.compute_metric(
            metric_name="iou",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # IoU = |overlap| / |union| = 5 / 15 ≈ 0.333
        assert abs(result - (5.0 / 15.0)) < 0.001

    def test_default_registry_compute_all(self):
        """Test compute_all() returns all metrics including Feature 5 set-wise metrics."""
        registry = MetricRegistry(k=5, min_overlap=0.5)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 10)]

        results = registry.compute_all(gold_spans, retrieved_spans)

        # Should have 8 metrics (5 standard + 3 Feature 5 set-wise)
        assert len(results) == 8
        assert "recall@5" in results
        assert "precision@5" in results
        assert "hit@5" in results
        assert "full_evidence@5" in results
        assert "iou" in results
        assert "span_concentration" in results  # Feature 5
        assert "fragmentation_ratio" in results  # Feature 5
        assert "pairwise_overlap" in results  # Feature 5

    def test_default_registry_with_custom_k(self):
        """Test registry respects custom K value."""
        registry = MetricRegistry(k=3, min_overlap=0.5)
        metrics = registry.get_all_metrics()

        # Metrics should be named for k=3
        assert "recall@3" in metrics
        assert "precision@3" in metrics
        assert "hit@3" in metrics
        assert "full_evidence@3" in metrics

    def test_default_registry_with_custom_min_overlap(self):
        """Test registry respects custom min_overlap value."""
        registry = MetricRegistry(k=5, min_overlap=0.8)

        gold_spans: list[Interval] = [(0, 10)]
        retrieved_spans: list[Interval] = [(0, 7)]

        hit_result = registry.compute_metric(
            metric_name="hit@5",
            gold_spans=gold_spans,
            retrieved_spans=retrieved_spans,
        )

        # 7/10 = 0.7 < 0.8, so should return 0 (no hit)
        assert hit_result == 0


class TestMetricRegistryCustomMetrics:
    """Test custom metric registration."""

    def test_register_custom_metric(self):
        """Test registering a custom metric."""
        registry = MetricRegistry()

        # Create a custom metric
        custom_metric = MetricDefinition(
            name="custom_average",
            compute_fn=lambda g, r: 0.5,
            result_type=float,
        )

        registry.register(custom_metric)

        # Should now have 9 metrics (8 defaults + 1 custom)
        metrics = registry.get_all_metrics()
        assert len(metrics) == 9
        assert "custom_average" in metrics

    def test_register_and_compute_custom_metric(self):
        """Test computing a registered custom metric."""
        registry = MetricRegistry()

        # Create custom metric that always returns 0.7
        custom_metric = MetricDefinition(
            name="test_metric",
            compute_fn=lambda g, r: 0.7,
            result_type=float,
        )

        registry.register(custom_metric)

        result = registry.compute_metric(
            metric_name="test_metric",
            gold_spans=[(0, 10)],
            retrieved_spans=[(0, 5)],
        )

        assert result == 0.7

    def test_register_custom_metric_with_complex_logic(self):
        """Test custom metric with actual computation logic."""
        registry = MetricRegistry()

        # Custom metric: count of gold spans
        custom_metric = MetricDefinition(
            name="gold_span_count",
            compute_fn=lambda g, r: float(len(g)),
            result_type=float,
        )

        registry.register(custom_metric)

        result = registry.compute_metric(
            metric_name="gold_span_count",
            gold_spans=[(0, 10), (20, 30), (40, 50)],
            retrieved_spans=[(0, 5)],
        )

        # Should return 3 (count of gold spans)
        assert result == 3.0

    def test_override_existing_metric(self):
        """Test overriding an existing metric."""
        registry = MetricRegistry()

        # Create override metric for recall@5
        override_metric = MetricDefinition(
            name="recall@5",
            compute_fn=lambda g, r: 0.999,  # Always return 0.999
            result_type=float,
        )

        registry.register(override_metric)

        result = registry.compute_metric(
            metric_name="recall@5",
            gold_spans=[(0, 10)],
            retrieved_spans=[(0, 5)],
        )

        # Should return override value, not computed recall
        assert result == 0.999

    def test_get_nonexistent_metric(self):
        """Test getting a metric that doesn't exist."""
        registry = MetricRegistry()

        result = registry.get("nonexistent_metric")
        assert result is None

    def test_compute_nonexistent_metric_raises_error(self):
        """Test computing a metric that doesn't exist raises KeyError."""
        registry = MetricRegistry()

        with pytest.raises(KeyError):
            registry.compute_metric(
                metric_name="nonexistent_metric",
                gold_spans=[(0, 10)],
                retrieved_spans=[(0, 5)],
            )


class TestMetricRegistryIntegration:
    """Test metric registry integration with evaluate()."""

    def test_evaluate_with_default_registry(self):
        """Test evaluate() uses default registry when metric_registry=None."""
        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash("Hello")
        anchor = Anchor("doc1", 0, 5, text_hash)
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            metric_registry=None,  # Should use default
        )

        # Should have computed all 5 metrics
        q_metrics = run.per_query_metrics["q1"]
        assert "recall@5" in q_metrics
        assert "precision@5" in q_metrics
        assert "hit@5" in q_metrics
        assert "full_evidence@5" in q_metrics
        assert "iou" in q_metrics

    def test_evaluate_with_custom_registry(self):
        """Test evaluate() accepts custom metric registry."""
        # Create custom registry with only 2 metrics
        registry = MetricRegistry()
        # Remove 3 metrics, keep only recall and iou for testing
        metrics = registry.get_all_metrics()
        custom_registry = MetricRegistry()
        # Register only custom metrics
        custom_registry._metrics = {}
        custom_registry._metrics["recall@5"] = metrics["recall@5"]
        custom_registry._metrics["iou"] = metrics["iou"]

        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash("Hello")
        anchor = Anchor("doc1", 0, 5, text_hash)
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            metric_registry=custom_registry,
        )

        # Should have only 2 metrics plus retrieved_chars
        q_metrics = run.per_query_metrics["q1"]
        assert "recall@5" in q_metrics
        assert "iou" in q_metrics
        assert len(q_metrics) == 3  # recall@5, iou, retrieved_chars

    def test_evaluate_backward_compatibility(self):
        """Test evaluate() works unchanged when metric_registry not provided."""
        doc = Document.from_text("doc1", "The quick brown fox")
        text_hash = compute_hash("quick brown")
        anchor = Anchor("doc1", 4, 15, text_hash)
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=4, end=15)

        # Call without metric_registry parameter (old API)
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

        # Should work exactly as before
        assert run.config["k"] == 5
        assert "recall@5" in run.per_query_metrics["q1"]

    def test_evaluate_default_registry_matches_direct_call(self):
        """Test that default registry produces same results as direct metric calls."""
        doc = Document.from_text("doc1", "Alpha Beta Gamma Delta")
        text_hash = compute_hash("Beta Gamma")
        anchor = Anchor("doc1", 6, 16, text_hash)
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, text="Beta Gamma")

        # Evaluate with default registry
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            min_overlap=0.5,
        )

        q_metrics = run.per_query_metrics["q1"]

        # Verify each metric value using direct function calls
        gold_spans: list[Interval] = [(6, 16)]
        retrieved_spans: list[Interval] = [(6, 16)]

        expected_recall = recall_at_k(gold_spans, retrieved_spans, k=5)
        expected_precision = precision_at_k(gold_spans, retrieved_spans, k=5)

        assert q_metrics["recall@5"] == expected_recall
        assert q_metrics["precision@5"] == expected_precision


class TestMetricRegistryEdgeCases:
    """Test edge cases and error conditions."""

    def test_compute_all_with_empty_gold_spans(self):
        """Test compute_all handles empty gold spans gracefully."""
        registry = MetricRegistry()

        # Empty gold spans should skip metrics that require them
        results = registry.compute_all(
            gold_spans=[],
            retrieved_spans=[(0, 10)],
        )

        # Should return partial results or be empty
        assert isinstance(results, dict)

    def test_registry_with_zero_k(self) -> None:
        """Test registry with k=0 (edge case)."""
        # k=0 should be allowed during registry creation
        registry = MetricRegistry(k=0, min_overlap=0.5)
        # But metrics will fail when computed
        # This is handled by the metric functions themselves
        # Now includes 8 metrics (5 standard + 3 Feature 5 set-wise)
        assert len(registry.get_all_metrics()) == 8

    def test_registry_with_high_k(self) -> None:
        """Test registry with high k value."""
        registry = MetricRegistry(k=100, min_overlap=0.5)
        metrics = registry.get_all_metrics()

        assert "recall@100" in metrics
        assert "precision@100" in metrics
        assert "hit@100" in metrics
        assert "full_evidence@100" in metrics

    def test_multiple_registries_independent(self):
        """Test that multiple registries are independent."""
        registry1 = MetricRegistry(k=5, min_overlap=0.5)
        registry2 = MetricRegistry(k=10, min_overlap=0.7)

        # Add custom metric to registry1
        custom = MetricDefinition(
            name="custom1",
            compute_fn=lambda g, r: 1.0,
            result_type=float,
        )
        registry1.register(custom)

        # registry2 should not have custom metric
        assert "custom1" in registry1.get_all_metrics()
        assert "custom1" not in registry2.get_all_metrics()

        # They should have different k values in metric names
        r1_metrics = set(registry1.get_all_metrics().keys())
        r2_metrics = set(registry2.get_all_metrics().keys())

        assert "recall@5" in r1_metrics
        assert "recall@10" in r2_metrics
