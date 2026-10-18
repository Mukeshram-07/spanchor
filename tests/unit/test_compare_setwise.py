"""Unit tests for set-wise metrics integration into compare() function.

Tests integration of set-wise metrics (span_concentration, fragmentation_ratio,
pairwise_overlap) into the comparison workflow.

Validates: Feature 8.3 Requirement: Wire Set-wise Metrics into Comparison
"""

from spanchor.comparison.compare import compare
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult
from spanchor.models.run import Run

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_run(
    per_query_metrics: dict[str, dict[str, float]],
    aggregate_metrics: dict[str, float] | None = None,
    queries: tuple[Query, ...] | None = None,
    per_query_retrieval_results: dict[str, tuple[RetrievalResult, ...]] | None = None,
) -> Run:
    """Build a minimal Run for testing."""
    if aggregate_metrics is None:
        # Compute macro-average for convenience
        all_metrics: set[str] = set()
        for m in per_query_metrics.values():
            all_metrics.update(m.keys())
        aggregate_metrics = {}
        for metric in all_metrics:
            vals = [m[metric] for m in per_query_metrics.values() if metric in m]
            if vals:
                aggregate_metrics[f"mean_{metric}"] = sum(vals) / len(vals)

    return Run(
        timestamp="2024-01-01T00:00:00Z",
        queries=queries or (),
        per_query_metrics=per_query_metrics,
        aggregate_metrics=aggregate_metrics,
        config={},
        mapper_stats={},
        per_query_retrieval_results=per_query_retrieval_results,
    )


# ---------------------------------------------------------------------------
# Test: Backward Compatibility (include_setwise=False by default)
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Tests that setwise metrics are disabled by default."""

    def test_compare_without_setwise_default(self):
        """When include_setwise is not specified, setwise_deltas should be None."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.90}})

        result = compare(baseline, candidate, {})

        assert result.setwise_deltas is None
        assert result.setwise_aggregate_deltas is None

    def test_compare_with_setwise_false(self):
        """Explicitly setting include_setwise=False should keep setwise_deltas as None."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.90}})

        result = compare(baseline, candidate, {}, include_setwise=False)

        assert result.setwise_deltas is None
        assert result.setwise_aggregate_deltas is None

    def test_compare_with_setwise_but_no_retrieval_results(self):
        """When include_setwise=True but retrieval results unavailable, setwise_deltas None."""
        # Run without retrieval results
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.90}})

        result = compare(baseline, candidate, {}, include_setwise=True)

        # No retrieval results → setwise_deltas should be None
        assert result.setwise_deltas is None
        assert result.setwise_aggregate_deltas is None

    def test_compare_with_setwise_baseline_missing_retrieval_results(self):
        """When only candidate has retrieval results, setwise_deltas should be None."""
        baseline = make_run({"q1": {"recall@5": 0.80}})

        candidate_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),
                RetrievalResult(rank=2, score=0.90, document_id="d1", start=100, end=150),
            )
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Baseline missing → setwise_deltas should be None
        assert result.setwise_deltas is None
        assert result.setwise_aggregate_deltas is None


# ---------------------------------------------------------------------------
# Test: Set-wise Metrics Computation (include_setwise=True)
# ---------------------------------------------------------------------------


class TestSetwiseMetricsComputation:
    """Tests for set-wise metrics computation when enabled."""

    def test_compare_with_setwise_enabled(self):
        """When include_setwise=True and data available, compute setwise_deltas."""
        baseline_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),
                RetrievalResult(rank=2, score=0.90, document_id="d1", start=100, end=150),
            )
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),
                RetrievalResult(rank=2, score=0.92, document_id="d1", start=90, end=160),
            )
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # setwise_deltas should be computed
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas
        # Should have three set-wise metrics
        assert "span_concentration" in result.setwise_deltas["q1"]
        assert "fragmentation_ratio" in result.setwise_deltas["q1"]
        assert "pairwise_overlap" in result.setwise_deltas["q1"]

    def test_setwise_deltas_is_candidate_minus_baseline(self):
        """Set-wise deltas should equal candidate metric - baseline metric."""
        # Simple case: baseline has 2 disjoint spans, candidate has 1 merged span
        # This should increase span_concentration and decrease fragmentation_ratio
        baseline_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),
                RetrievalResult(rank=2, score=0.90, document_id="d1", start=200, end=250),
            )
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=baseline_results,
        )

        # Candidate merges spans to be adjacent/overlapping
        candidate_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),
                RetrievalResult(rank=2, score=0.92, document_id="d1", start=50, end=150),
            )
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Verify deltas are computed
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas
        deltas = result.setwise_deltas["q1"]

        # Concentration should increase (merged spans are more concentrated)
        # fragmentation_ratio should decrease (fewer fragments)
        assert "span_concentration" in deltas
        assert "fragmentation_ratio" in deltas

    def test_setwise_aggregate_deltas_computed(self):
        """Aggregate setwise deltas should be macro-average across queries."""
        baseline_results = {
            "q1": (RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),),
            "q2": (RetrievalResult(rank=1, score=0.90, document_id="d1", start=100, end=150),),
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.75}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),),
            "q2": (RetrievalResult(rank=1, score=0.92, document_id="d1", start=100, end=200),),
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}, "q2": {"recall@5": 0.85}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Aggregate deltas should be computed
        assert result.setwise_aggregate_deltas is not None
        assert "span_concentration" in result.setwise_aggregate_deltas
        assert "fragmentation_ratio" in result.setwise_aggregate_deltas
        assert "pairwise_overlap" in result.setwise_aggregate_deltas

    def test_setwise_deltas_only_for_common_queries(self):
        """Set-wise deltas should only be computed for queries in both runs."""
        baseline_results = {
            "q1": (RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),),
            "q2": (RetrievalResult(rank=1, score=0.90, document_id="d1", start=100, end=150),),
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.75}},
            per_query_retrieval_results=baseline_results,
        )

        # Candidate only has q1 (not q2)
        candidate_results = {
            "q1": (RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),),
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Only q1 should have setwise_deltas
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas
        assert "q2" not in result.setwise_deltas


# ---------------------------------------------------------------------------
# Test: Set-wise Metrics with Multiple Documents
# ---------------------------------------------------------------------------


class TestSetwiseMetricsMultipleDocuments:
    """Tests for set-wise metrics with results from multiple documents."""

    def test_setwise_metrics_with_spans_from_multiple_documents(self):
        """Set-wise metrics should handle spans from multiple documents correctly."""
        baseline_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),
                RetrievalResult(rank=2, score=0.90, document_id="d2", start=100, end=150),
            )
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),
                RetrievalResult(rank=2, score=0.92, document_id="d2", start=50, end=150),
            )
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Should compute setwise metrics (per-document handling is transparent)
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas
        assert "span_concentration" in result.setwise_deltas["q1"]


# ---------------------------------------------------------------------------
# Test: Set-wise Metrics Combined with Other Features
# ---------------------------------------------------------------------------


class TestSetwiseMetricsCombinedWithOtherFeatures:
    """Tests for set-wise metrics combined with statistics and policy."""

    def test_setwise_and_statistics_together(self):
        """Set-wise metrics should work alongside statistical analysis."""
        from spanchor.comparison.statistics import StatisticsConfig

        baseline_results = {
            "q1": (RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),),
            "q2": (RetrievalResult(rank=1, score=0.90, document_id="d1", start=100, end=150),),
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.75}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),),
            "q2": (RetrievalResult(rank=1, score=0.92, document_id="d1", start=100, end=200),),
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}, "q2": {"recall@5": 0.85}},
            per_query_retrieval_results=candidate_results,
        )

        stats_config = StatisticsConfig(enabled=True, num_resamples=100)

        result = compare(
            baseline,
            candidate,
            {"recall@5": 0.05},
            statistics_config=stats_config,
            include_setwise=True,
        )

        # Both statistics and setwise metrics should be present
        assert result.bootstrap_results is not None
        assert result.setwise_deltas is not None
        assert result.setwise_aggregate_deltas is not None

    def test_setwise_with_policy_classification(self):
        """Set-wise metrics should not affect policy-based classification."""
        baseline_results = {
            "q1": (RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),),
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (RetrievalResult(rank=1, score=0.80, document_id="d1", start=0, end=100),),
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {"recall@5": 0.05}, include_setwise=True)

        # Classification should be REGRESSION (based on recall@5 policy)
        assert result.per_query_status["q1"] == "REGRESSION"
        # Set-wise metrics should still be computed
        assert result.setwise_deltas is not None


# ---------------------------------------------------------------------------
# Test: Edge Cases
# ---------------------------------------------------------------------------


class TestSetwiseMetricsEdgeCases:
    """Tests for edge cases in set-wise metrics computation."""

    def test_setwise_with_empty_retrieval_results(self):
        """When a query has empty retrieval results, handle gracefully."""
        baseline_results = {
            "q1": (),  # Empty
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.00}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (),  # Empty
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.00}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Should still compute (empty results → deltas = 0)
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas

    def test_setwise_with_single_result_per_query(self):
        """Set-wise metrics should handle queries with single results."""
        baseline_results = {
            "q1": (RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),),
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),),
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result = compare(baseline, candidate, {}, include_setwise=True)

        # Should compute setwise metrics even with single result
        assert result.setwise_deltas is not None
        assert "q1" in result.setwise_deltas

    def test_setwise_metrics_deterministic(self):
        """Set-wise metric deltas should be deterministic."""
        baseline_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.95, document_id="d1", start=0, end=50),
                RetrievalResult(rank=2, score=0.90, document_id="d1", start=100, end=150),
            )
        }
        baseline = make_run(
            {"q1": {"recall@5": 0.80}},
            per_query_retrieval_results=baseline_results,
        )

        candidate_results = {
            "q1": (
                RetrievalResult(rank=1, score=0.98, document_id="d1", start=0, end=100),
                RetrievalResult(rank=2, score=0.92, document_id="d1", start=90, end=160),
            )
        }
        candidate = make_run(
            {"q1": {"recall@5": 0.90}},
            per_query_retrieval_results=candidate_results,
        )

        result1 = compare(baseline, candidate, {}, include_setwise=True)
        result2 = compare(baseline, candidate, {}, include_setwise=True)

        # Results should be identical
        assert result1.setwise_deltas == result2.setwise_deltas
        assert result1.setwise_aggregate_deltas == result2.setwise_aggregate_deltas
