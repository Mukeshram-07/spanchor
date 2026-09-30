"""Unit tests for metric aggregation module.

Tests for macro-average and micro-average aggregation of per-query metrics.
"""

import pytest

from spanchor.evaluation.aggregation import aggregate_metrics, compute_mean_retrieved_chars
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query


class TestMacroAverageAggregation:
    """Tests for macro-average aggregation (default behavior)."""

    def test_macro_average_equal_weights(self) -> None:
        """Test that macro-average gives equal weight to all queries."""
        # Two queries: one with 0.8, one with 1.0 -> average should be 0.9
        per_query_metrics = {
            "q1": {"recall@5": 0.8, "precision@5": 0.9, "retrieved_chars": 100.0},
            "q2": {"recall@5": 1.0, "precision@5": 0.7, "retrieved_chars": 200.0},
        }
        
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),
        ]
        
        result = aggregate_metrics(per_query_metrics, queries, "macro")
        
        # Macro-average: (0.8 + 1.0) / 2 = 0.9
        assert result["mean_recall@5"] == 0.9
        # Macro-average: (0.9 + 0.7) / 2 = 0.8
        assert result["mean_precision@5"] == 0.8
        # Macro-average: (100 + 200) / 2 = 150
        assert result["mean_retrieved_chars"] == 150.0

    def test_macro_average_single_query(self) -> None:
        """Test macro-average with a single query."""
        per_query_metrics = {
            "q1": {"recall@5": 0.75, "precision@5": 0.85, "retrieved_chars": 120.0},
        }
        
        queries = [Query("q1", "test", ())]
        
        result = aggregate_metrics(per_query_metrics, queries, "macro")
        
        assert result["mean_recall@5"] == 0.75
        assert result["mean_precision@5"] == 0.85
        assert result["mean_retrieved_chars"] == 120.0

    def test_macro_average_empty_queries(self) -> None:
        """Test macro-average with no queries returns empty dict."""
        result = aggregate_metrics({}, [], "macro")
        assert result == {}

    def test_macro_average_missing_query_metrics(self) -> None:
        """Test macro-average handles missing query gracefully."""
        per_query_metrics = {
            "q1": {"recall@5": 0.8, "precision@5": 0.9},
        }
        
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),  # Missing from per_query_metrics
        ]
        
        result = aggregate_metrics(per_query_metrics, queries, "macro")
        
        # Should only average q1 since q2 is missing
        assert result["mean_recall@5"] == 0.8
        assert result["mean_precision@5"] == 0.9


class TestMicroAverageAggregation:
    """Tests for micro-average aggregation."""

    def test_micro_average_weighted_by_retrieved_chars(self) -> None:
        """Test that micro-average weights by retrieved chars."""
        # q1: recall=0.8, retrieved_chars=100 -> contributes 80
        # q2: recall=0.6, retrieved_chars=200 -> contributes 120
        # Total: 200 / 300 = 0.6667
        per_query_metrics = {
            "q1": {"recall@5": 0.8, "precision@5": 0.9, "retrieved_chars": 100.0},
            "q2": {"recall@5": 0.6, "precision@5": 0.7, "retrieved_chars": 200.0},
        }
        
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),
        ]
        
        result = aggregate_metrics(per_query_metrics, queries, "micro")
        
        # Micro-average: (0.8 * 100 + 0.6 * 200) / (100 + 200) = 200 / 300 = 0.6667
        assert abs(result["micro_recall@5"] - 0.6667) < 0.001
        # Micro-average: (0.9 * 100 + 0.7 * 200) / (100 + 200) = 230 / 300 = 0.7667
        assert abs(result["micro_precision@5"] - 0.7667) < 0.001
        # Total retrieved chars
        assert result["micro_retrieved_chars"] == 300.0

    def test_micro_average_single_query(self) -> None:
        """Test micro-average with a single query."""
        per_query_metrics = {
            "q1": {"recall@5": 0.75, "precision@5": 0.85, "retrieved_chars": 120.0},
        }
        
        queries = [Query("q1", "test", ())]
        
        result = aggregate_metrics(per_query_metrics, queries, "micro")
        
        # With single query, micro and macro should be the same
        assert result["micro_recall@5"] == 0.75
        assert result["micro_precision@5"] == 0.85
        assert result["micro_retrieved_chars"] == 120.0

    def test_micro_average_zero_retrieved_chars_fallback(self) -> None:
        """Test micro-average falls back to macro when no retrieved chars."""
        per_query_metrics = {
            "q1": {"recall@5": 0.8, "precision@5": 0.9, "retrieved_chars": 0.0},
            "q2": {"recall@5": 1.0, "precision@5": 0.7, "retrieved_chars": 0.0},
        }
        
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),
        ]
        
        result = aggregate_metrics(per_query_metrics, queries, "micro")
        
        # Should fall back to macro-average
        assert "mean_recall@5" in result
        assert result["mean_recall@5"] == 0.9


class TestInvalidAggregationMethod:
    """Tests for invalid aggregation method handling."""

    def test_invalid_aggregation_method_raises_error(self) -> None:
        """Test that invalid aggregation method raises ValueError."""
        per_query_metrics = {
            "q1": {"recall@5": 0.8},
        }
        queries = [Query("q1", "test", ())]
        
        with pytest.raises(ValueError, match="Invalid aggregation_method.*Must be 'macro' or 'micro'"):
            aggregate_metrics(per_query_metrics, queries, "invalid")  # type: ignore


class TestComputeMeanRetrievedChars:
    """Tests for compute_mean_retrieved_chars helper function."""

    def test_compute_mean_retrieved_chars(self) -> None:
        """Test computing mean retrieved characters."""
        per_query_metrics = {
            "q1": {"retrieved_chars": 500.0},
            "q2": {"retrieved_chars": 300.0},
        }
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),
        ]
        
        result = compute_mean_retrieved_chars(per_query_metrics, queries)
        
        assert result == 400.0

    def test_compute_mean_retrieved_chars_empty(self) -> None:
        """Test computing mean with no queries."""
        result = compute_mean_retrieved_chars({}, [])
        assert result == 0.0

    def test_compute_mean_retrieved_chars_missing_field(self) -> None:
        """Test computing mean when retrieved_chars field is missing."""
        per_query_metrics = {
            "q1": {"recall@5": 0.8},  # No retrieved_chars field
        }
        queries = [Query("q1", "test", ())]
        
        result = compute_mean_retrieved_chars(per_query_metrics, queries)
        
        # Should default to 0.0 for missing field
        assert result == 0.0


class TestAggregationWithRealMetrics:
    """Integration-style tests with realistic metric values."""

    def test_aggregation_preserves_all_metric_types(self) -> None:
        """Test that aggregation handles all metric types correctly."""
        per_query_metrics = {
            "q1": {
                "recall@5": 0.85,
                "precision@5": 0.90,
                "hit@5": 1.0,
                "full_evidence@5": 1.0,
                "iou": 0.78,
                "retrieved_chars": 250.0,
            },
            "q2": {
                "recall@5": 0.75,
                "precision@5": 0.80,
                "hit@5": 1.0,
                "full_evidence@5": 0.0,
                "iou": 0.65,
                "retrieved_chars": 180.0,
            },
        }
        
        queries = [
            Query("q1", "test1", ()),
            Query("q2", "test2", ()),
        ]
        
        result = aggregate_metrics(per_query_metrics, queries, "macro")
        
        # Check all metrics are present
        assert "mean_recall@5" in result
        assert "mean_precision@5" in result
        assert "mean_hit@5" in result
        assert "mean_full_evidence@5" in result
        assert "mean_iou" in result
        assert "mean_retrieved_chars" in result
        
        # Check macro-average values
        assert result["mean_recall@5"] == 0.80
        assert abs(result["mean_precision@5"] - 0.85) < 0.0001
        assert result["mean_hit@5"] == 1.0
        assert result["mean_full_evidence@5"] == 0.5
        assert abs(result["mean_iou"] - 0.715) < 0.0001
        assert result["mean_retrieved_chars"] == 215.0
