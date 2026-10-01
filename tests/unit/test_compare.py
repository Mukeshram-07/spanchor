"""Unit tests for the comparison engine (compare()).

Tests classification logic, delta computation, aggregate deltas,
has_regression flag, and edge cases.

Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8
"""

import pytest

from spanchor.comparison.compare import ComparisonResult, compare
from spanchor.errors import ComparisonError
from spanchor.models.query import Query
from spanchor.models.run import Run

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_run(
    per_query_metrics: dict[str, dict[str, float]],
    aggregate_metrics: dict[str, float] | None = None,
    queries: tuple[Query, ...] | None = None,
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
        queries=queries or tuple(),
        per_query_metrics=per_query_metrics,
        aggregate_metrics=aggregate_metrics,
        config={},
        mapper_stats={},
    )


# ---------------------------------------------------------------------------
# Per-query delta computation (Req 12.1)
# ---------------------------------------------------------------------------


class TestPerQueryDeltas:
    """Tests for per-query delta computation."""

    def test_delta_is_candidate_minus_baseline(self):
        """Delta should equal candidate metric - baseline metric. (Req 12.1)"""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.90}})

        result = compare(baseline, candidate, {})

        assert "q1" in result.per_query_deltas
        assert abs(result.per_query_deltas["q1"]["recall@5"] - 0.10) < 1e-9

    def test_negative_delta_when_candidate_worse(self):
        """Delta is negative when candidate is worse than baseline. (Req 12.1)"""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.80}})

        result = compare(baseline, candidate, {})

        assert result.per_query_deltas["q1"]["recall@5"] == pytest.approx(-0.10)

    def test_zero_delta_when_identical(self):
        """Delta is zero when candidate and baseline are identical. (Req 12.1)"""
        metrics = {"q1": {"recall@5": 0.75, "precision@5": 0.60}}
        baseline = make_run(metrics)
        candidate = make_run(metrics)

        result = compare(baseline, candidate, {})

        for metric, delta in result.per_query_deltas["q1"].items():
            assert delta == pytest.approx(0.0), f"{metric} delta should be 0"

    def test_multiple_metrics_per_query(self):
        """Deltas are computed for all common metrics in a query. (Req 12.1)"""
        baseline = make_run({"q1": {"recall@5": 0.80, "precision@5": 0.70, "hit@5": 1.0}})
        candidate = make_run({"q1": {"recall@5": 0.85, "precision@5": 0.65, "hit@5": 1.0}})

        result = compare(baseline, candidate, {})
        deltas = result.per_query_deltas["q1"]

        assert deltas["recall@5"] == pytest.approx(0.05)
        assert deltas["precision@5"] == pytest.approx(-0.05)
        assert deltas["hit@5"] == pytest.approx(0.0)

    def test_multiple_queries_deltas(self):
        """Deltas are computed independently for each query. (Req 12.1)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.60},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.50},
            }
        )

        result = compare(baseline, candidate, {})

        assert result.per_query_deltas["q1"]["recall@5"] == pytest.approx(0.10)
        assert result.per_query_deltas["q2"]["recall@5"] == pytest.approx(-0.10)

    def test_only_common_metrics_included_in_deltas(self):
        """Only metrics present in both baseline and candidate are included."""
        baseline = make_run({"q1": {"recall@5": 0.80, "iou": 0.60}})
        candidate = make_run({"q1": {"recall@5": 0.85, "precision@5": 0.70}})

        result = compare(baseline, candidate, {})
        deltas = result.per_query_deltas["q1"]

        # "recall@5" is common
        assert "recall@5" in deltas
        # "iou" only in baseline, "precision@5" only in candidate → not in deltas
        assert "iou" not in deltas
        assert "precision@5" not in deltas


# ---------------------------------------------------------------------------
# Classification: IMPROVED (Req 12.4)
# ---------------------------------------------------------------------------


class TestClassificationImproved:
    """Tests for IMPROVED classification."""

    def test_query_is_improved_when_metric_exceeds_threshold(self):
        """Query is IMPROVED when delta > max_drop threshold. (Req 12.4)"""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.90}})  # delta = +0.10

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "IMPROVED"

    def test_query_is_improved_when_delta_exactly_equals_threshold(self):
        """Query at exactly threshold is NOT IMPROVED (must be strictly greater)."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})  # delta = +0.05

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # delta == threshold → UNCHANGED, not IMPROVED
        assert result.per_query_status["q1"] == "UNCHANGED"

    def test_query_improved_with_multiple_metrics_all_positive(self):
        """Query is IMPROVED when multiple metrics improve. (Req 12.4)"""
        baseline = make_run({"q1": {"recall@5": 0.70, "hit@5": 0.60}})
        candidate = make_run({"q1": {"recall@5": 0.85, "hit@5": 0.80}})

        result = compare(baseline, candidate, {"recall@5": 0.05, "hit@5": 0.05})

        assert result.per_query_status["q1"] == "IMPROVED"


# ---------------------------------------------------------------------------
# Classification: REGRESSION (Req 12.3)
# ---------------------------------------------------------------------------


class TestClassificationRegression:
    """Tests for REGRESSION classification."""

    def test_query_is_regression_when_metric_drops_beyond_threshold(self):
        """Query is REGRESSION when delta < -max_drop. (Req 12.3)"""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.80}})  # delta = -0.10

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "REGRESSION"

    def test_query_is_regression_even_with_other_improved_metrics(self):
        """REGRESSION wins even when another metric improves. (Req 12.3)"""
        baseline = make_run({"q1": {"recall@5": 0.90, "precision@5": 0.60}})
        candidate = make_run({"q1": {"recall@5": 0.80, "precision@5": 0.90}})
        # recall drops 0.10 (REGRESSION), precision improves 0.30

        result = compare(baseline, candidate, {"recall@5": 0.05, "precision@5": 0.05})

        assert result.per_query_status["q1"] == "REGRESSION"

    def test_query_at_exactly_negative_threshold_is_unchanged(self):
        """Delta exactly equal to -threshold is UNCHANGED (boundary). (Req 12.3)"""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.85}})  # delta = -0.05

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # delta == -threshold → UNCHANGED, not REGRESSION
        assert result.per_query_status["q1"] == "UNCHANGED"

    def test_regression_on_one_query_not_others(self):
        """REGRESSION on one query doesn't affect others. (Req 12.3)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.70},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.75},  # drops 0.15 → REGRESSION
                "q2": {"recall@5": 0.85},  # improves 0.15 → IMPROVED
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "REGRESSION"
        assert result.per_query_status["q2"] == "IMPROVED"


# ---------------------------------------------------------------------------
# Classification: UNCHANGED (Req 12.5)
# ---------------------------------------------------------------------------


class TestClassificationUnchanged:
    """Tests for UNCHANGED classification."""

    def test_query_is_unchanged_when_delta_within_threshold(self):
        """Query is UNCHANGED when all deltas are within threshold. (Req 12.5)"""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.82}})  # delta = +0.02

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "UNCHANGED"

    def test_all_unchanged_with_empty_policy(self):
        """Empty policy means every query is UNCHANGED regardless of delta. (Default policy)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.50},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.10},  # huge drop
                "q2": {"recall@5": 0.99},  # huge gain
            }
        )

        result = compare(baseline, candidate, {})  # empty policy

        assert result.per_query_status["q1"] == "UNCHANGED"
        assert result.per_query_status["q2"] == "UNCHANGED"

    def test_unchanged_with_zero_delta(self):
        """Zero delta is always UNCHANGED regardless of threshold. (Req 12.5)"""
        baseline = make_run({"q1": {"recall@5": 0.75}})
        candidate = make_run({"q1": {"recall@5": 0.75}})

        result = compare(baseline, candidate, {"recall@5": 0.0})

        assert result.per_query_status["q1"] == "UNCHANGED"


# ---------------------------------------------------------------------------
# Aggregate deltas (Req 12.6)
# ---------------------------------------------------------------------------


class TestAggregateDeltas:
    """Tests for aggregate delta computation."""

    def test_aggregate_delta_is_macro_average(self):
        """Aggregate delta is the macro-average of per-query deltas. (Req 12.6)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.60},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.90},  # +0.10
                "q2": {"recall@5": 0.70},  # +0.10
            }
        )

        result = compare(baseline, candidate, {})

        # macro-average = (0.10 + 0.10) / 2 = 0.10
        assert result.aggregate_deltas["recall@5"] == pytest.approx(0.10)

    def test_aggregate_delta_mixed_values(self):
        """Aggregate delta handles mix of positive and negative deltas. (Req 12.6)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.80},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.90},  # +0.10
                "q2": {"recall@5": 0.70},  # -0.10
            }
        )

        result = compare(baseline, candidate, {})

        # macro-average = (0.10 + (-0.10)) / 2 = 0.0
        assert result.aggregate_deltas["recall@5"] == pytest.approx(0.0)

    def test_aggregate_delta_multiple_metrics(self):
        """Aggregate deltas are computed for each metric independently. (Req 12.6)"""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80, "hit@5": 0.70},
                "q2": {"recall@5": 0.60, "hit@5": 0.50},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.90, "hit@5": 0.80},  # recall +0.10, hit +0.10
                "q2": {"recall@5": 0.40, "hit@5": 0.60},  # recall -0.20, hit +0.10
            }
        )

        result = compare(baseline, candidate, {})

        # recall macro-average = (0.10 + (-0.20)) / 2 = -0.05
        assert result.aggregate_deltas["recall@5"] == pytest.approx(-0.05)
        # hit macro-average = (0.10 + 0.10) / 2 = 0.10
        assert result.aggregate_deltas["hit@5"] == pytest.approx(0.10)

    def test_aggregate_delta_single_query(self):
        """Aggregate delta for single query equals that query's delta. (Req 12.6)"""
        baseline = make_run({"q1": {"recall@5": 0.75}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        result = compare(baseline, candidate, {})

        assert result.aggregate_deltas["recall@5"] == pytest.approx(0.10)


# ---------------------------------------------------------------------------
# has_regression flag (Req 12.7 implied)
# ---------------------------------------------------------------------------


class TestHasRegression:
    """Tests for the has_regression flag."""

    def test_has_regression_true_when_any_query_is_regression(self):
        """has_regression is True when at least one query is REGRESSION."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},  # will REGRESS
                "q2": {"recall@5": 0.70},  # will be IMPROVED
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.75},
                "q2": {"recall@5": 0.90},
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.has_regression is True

    def test_has_regression_false_when_all_unchanged(self):
        """has_regression is False when all queries are UNCHANGED."""
        baseline = make_run({"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.70}})
        candidate = make_run({"q1": {"recall@5": 0.82}, "q2": {"recall@5": 0.72}})

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.has_regression is False

    def test_has_regression_false_when_all_improved(self):
        """has_regression is False when all queries are IMPROVED."""
        baseline = make_run({"q1": {"recall@5": 0.70}, "q2": {"recall@5": 0.60}})
        candidate = make_run({"q1": {"recall@5": 0.85}, "q2": {"recall@5": 0.80}})

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.has_regression is False

    def test_has_regression_false_with_empty_policy(self):
        """has_regression is always False with empty policy (no thresholds)."""
        baseline = make_run({"q1": {"recall@5": 0.99}})
        candidate = make_run({"q1": {"recall@5": 0.01}})

        result = compare(baseline, candidate, {})

        assert result.has_regression is False


# ---------------------------------------------------------------------------
# Only common queries included
# ---------------------------------------------------------------------------


class TestCommonQueries:
    """Tests that only queries common to both runs are compared."""

    def test_only_common_queries_in_result(self):
        """Queries only in baseline or only in candidate are excluded."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q_only_baseline": {"recall@5": 0.50},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.85},
                "q_only_candidate": {"recall@5": 0.90},
            }
        )

        result = compare(baseline, candidate, {})

        assert "q1" in result.per_query_deltas
        assert "q_only_baseline" not in result.per_query_deltas
        assert "q_only_candidate" not in result.per_query_deltas

    def test_no_common_queries_raises_comparison_error(self):
        """ComparisonError raised when runs share no common queries."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q_other": {"recall@5": 0.85}})

        with pytest.raises(ComparisonError) as exc_info:
            compare(baseline, candidate, {})

        assert "No common queries" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Return type and structure
# ---------------------------------------------------------------------------


class TestReturnStructure:
    """Tests that ComparisonResult has all required fields."""

    def test_result_has_all_required_fields(self):
        """ComparisonResult contains per_query_deltas, status, aggregate_deltas, has_regression."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        result = compare(baseline, candidate, {})

        assert isinstance(result, ComparisonResult)
        assert isinstance(result.per_query_deltas, dict)
        assert isinstance(result.per_query_status, dict)
        assert isinstance(result.aggregate_deltas, dict)
        assert isinstance(result.has_regression, bool)

    def test_status_values_are_valid_literals(self):
        """All per_query_status values are one of the three valid literals."""
        valid_statuses = {"IMPROVED", "REGRESSION", "UNCHANGED"}
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.90},
                "q3": {"recall@5": 0.70},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.90},  # IMPROVED
                "q2": {"recall@5": 0.78},  # REGRESSION (drop 0.12 > 0.05)
                "q3": {"recall@5": 0.72},  # UNCHANGED (drop 0.02 < 0.05)
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        for qid, status in result.per_query_status.items():
            assert status in valid_statuses, f"Invalid status for {qid}: {status}"

    def test_per_query_deltas_and_status_have_same_keys(self):
        """per_query_deltas and per_query_status cover the exact same query IDs."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.70},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.85},
                "q2": {"recall@5": 0.60},
            }
        )

        result = compare(baseline, candidate, {})

        assert set(result.per_query_deltas.keys()) == set(result.per_query_status.keys())
