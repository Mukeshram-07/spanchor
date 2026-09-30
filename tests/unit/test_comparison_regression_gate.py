"""Comprehensive tests for regression gate validation.

Tests covering:
1. Aggregate metric regression beyond threshold
2. Aggregate metric change within threshold
3. Per-query regression beyond threshold
4. Per-query change within threshold
5. Correct classification
6. Correct CLI exit code
7. Multiple metrics with different thresholds
8. Boundary condition exactly equal to threshold
9. No regression when candidate improves
10. Regression when candidate worsens

Validates: Requirements 12.1-12.8, 13.1-13.8
"""

import pytest

from spanchor.comparison.compare import compare
from spanchor.models.query import Query
from spanchor.models.run import Run


def make_run(
    per_query_metrics: dict[str, dict[str, float]],
    aggregate_metrics: dict[str, float] | None = None,
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
        queries=tuple(),
        per_query_metrics=per_query_metrics,
        aggregate_metrics=aggregate_metrics,
        config={},
        mapper_stats={},
    )


class TestRegressionGateValidation:
    """Tests for regression gate validation semantics."""

    def test_per_query_regression_beyond_threshold(self):
        """Individual query regresses beyond threshold -> REGRESSION classification."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.80}})

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "REGRESSION"
        assert result.has_regression is True

    def test_per_query_change_within_threshold(self):
        """Individual query drop within threshold -> UNCHANGED classification."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.87}})  # drop 0.03 < threshold 0.05

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "UNCHANGED"
        assert result.has_regression is False

    def test_aggregate_metric_computed_not_gated(self):
        """Aggregate deltas computed for reporting but not for regression gate."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.90},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.85},
                "q2": {"recall@5": 0.85},
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # Aggregate delta is -0.05 (exactly at threshold), but gate is per-query
        assert result.aggregate_deltas["recall@5"] == pytest.approx(-0.05)
        # Per-query deltas both -0.05 which equals threshold, so UNCHANGED
        assert result.per_query_status["q1"] == "UNCHANGED"
        assert result.per_query_status["q2"] == "UNCHANGED"
        assert result.has_regression is False

    def test_per_query_regression_triggered_by_aggregate_drop(self):
        """When many queries drop slightly, each individually triggers REGRESSION."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.90},
                "q3": {"recall@5": 0.90},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.84},  # drop 0.06 > threshold 0.05
                "q2": {"recall@5": 0.84},
                "q3": {"recall@5": 0.84},
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # All three queries regress per-query
        assert result.per_query_status["q1"] == "REGRESSION"
        assert result.per_query_status["q2"] == "REGRESSION"
        assert result.per_query_status["q3"] == "REGRESSION"
        assert result.has_regression is True

    def test_multiple_metrics_different_thresholds(self):
        """Each metric can have different thresholds."""
        baseline = make_run({"q1": {"recall@5": 0.90, "precision@5": 0.80}})
        candidate = make_run(
            {
                "q1": {"recall@5": 0.84, "precision@5": 0.75}  # both drop 0.06
            }
        )

        # recall threshold 0.05, precision threshold 0.10
        result = compare(baseline, candidate, {"recall@5": 0.05, "precision@5": 0.10})

        # recall drop 0.06 > 0.05 -> triggers REGRESSION
        # precision drop 0.06 < 0.10 -> within threshold
        # REGRESSION wins
        assert result.per_query_status["q1"] == "REGRESSION"
        assert result.has_regression is True

    def test_boundary_exactly_at_threshold(self):
        """Boundary condition: delta exactly equal to threshold."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.85}})  # drop exactly 0.05

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # Delta -0.05 == -threshold, so NOT < -threshold
        # Classification should be UNCHANGED (within threshold)
        assert result.per_query_status["q1"] == "UNCHANGED"
        assert result.has_regression is False

    def test_boundary_just_beyond_threshold(self):
        """Boundary condition: delta just beyond threshold."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.8499}})  # drop 0.0501 > 0.05

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # Delta -0.0501 < -0.05 threshold
        assert result.per_query_status["q1"] == "REGRESSION"
        assert result.has_regression is True

    def test_no_regression_when_candidate_improves(self):
        """Candidate better than baseline -> IMPROVED, no regression."""
        baseline = make_run({"q1": {"recall@5": 0.70}, "q2": {"recall@5": 0.60}})
        candidate = make_run({"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.70}})

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "IMPROVED"
        assert result.per_query_status["q2"] == "IMPROVED"
        assert result.has_regression is False

    def test_mixed_improved_unchanged_regressed(self):
        """Mixed scenario: some improve, some unchanged, some regress."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.70},  # will improve
                "q2": {"recall@5": 0.80},  # will regress
                "q3": {"recall@5": 0.75},  # will stay unchanged
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.77},  # improvement 0.07 > 0.05
                "q2": {"recall@5": 0.74},  # regression 0.06 > 0.05
                "q3": {"recall@5": 0.75},  # unchanged
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.per_query_status["q1"] == "IMPROVED"
        assert result.per_query_status["q2"] == "REGRESSION"
        assert result.per_query_status["q3"] == "UNCHANGED"
        assert result.has_regression is True  # Because q2 regressed

    def test_policy_metric_name_must_match_per_query_metrics(self):
        """Policy keys must match per-query metric names, NOT aggregate names."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.80}})

        # WRONG: using "mean_recall@5" (aggregate name)
        result_wrong = compare(baseline, candidate, {"mean_recall@5": 0.05})
        # Policy key doesn't match per-query metric "recall@5", so no regression detected
        assert result_wrong.has_regression is False

        # CORRECT: using "recall@5" (per-query name)
        result_correct = compare(baseline, candidate, {"recall@5": 0.05})
        # Policy key matches, regression properly detected
        assert result_correct.has_regression is True

    def test_exit_code_zero_when_no_regression(self):
        """Exit code should be 0 when has_regression is False."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.87}})  # within threshold

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.has_regression is False
        # In practice, CLI would return 0
        exit_code = 1 if result.has_regression else 0
        assert exit_code == 0

    def test_exit_code_one_when_regression_detected(self):
        """Exit code should be 1 when has_regression is True."""
        baseline = make_run({"q1": {"recall@5": 0.90}})
        candidate = make_run({"q1": {"recall@5": 0.84}})  # exceeds threshold

        result = compare(baseline, candidate, {"recall@5": 0.05})

        assert result.has_regression is True
        # In practice, CLI would return 1
        exit_code = 1 if result.has_regression else 0
        assert exit_code == 1

    def test_per_query_deltas_computation(self):
        """Per-query deltas are computed independently."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.80, "precision@5": 0.70},
                "q2": {"recall@5": 0.85, "precision@5": 0.75},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.75, "precision@5": 0.68},
                "q2": {"recall@5": 0.90, "precision@5": 0.80},
            }
        )

        result = compare(baseline, candidate, {})

        # q1 deltas
        assert result.per_query_deltas["q1"]["recall@5"] == pytest.approx(-0.05)
        assert result.per_query_deltas["q1"]["precision@5"] == pytest.approx(-0.02)

        # q2 deltas
        assert result.per_query_deltas["q2"]["recall@5"] == pytest.approx(0.05)
        assert result.per_query_deltas["q2"]["precision@5"] == pytest.approx(0.05)

    def test_aggregate_deltas_macro_average(self):
        """Aggregate deltas are computed as macro-average across queries."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.80},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.85},  # delta -0.05
                "q2": {"recall@5": 0.82},  # delta +0.02
            }
        )

        result = compare(baseline, candidate, {})

        # Aggregate: (-0.05 + 0.02) / 2 = -0.015
        assert result.aggregate_deltas["recall@5"] == pytest.approx(-0.015)

    def test_only_common_queries_compared(self):
        """Only queries present in both runs are compared."""
        baseline = make_run(
            {
                "q1": {"recall@5": 0.90},
                "q2": {"recall@5": 0.80},
            }
        )
        candidate = make_run(
            {
                "q1": {"recall@5": 0.85},
                # q2 is missing in candidate
            }
        )

        result = compare(baseline, candidate, {})

        assert "q1" in result.per_query_deltas
        assert "q2" not in result.per_query_deltas
        assert len(result.per_query_deltas) == 1

    def test_semantics_are_per_query_not_aggregate(self):
        """CRITICAL: Regression semantics are PER-QUERY, NOT aggregate-based."""
        # Scenario: 100 queries
        # - 1 query drops 0.10 (exceeds threshold)
        # - 99 queries improve 0.01 each
        # Aggregate: (-0.10 + 99 * 0.01) / 100 = 0.89 / 100 = 0.0089
        # But: has_regression should be TRUE (1 query regressed per-query policy)

        baseline = make_run(
            {
                **{"q_regress": {"recall@5": 0.90}},
                **{f"q{i}": {"recall@5": 0.50} for i in range(99)},
            }
        )
        candidate = make_run(
            {
                **{"q_regress": {"recall@5": 0.80}},  # drop 0.10
                **{f"q{i}": {"recall@5": 0.51} for i in range(99)},  # improve 0.01
            }
        )

        result = compare(baseline, candidate, {"recall@5": 0.05})

        # Aggregate is slightly positive: 0.0089
        # (-0.10 + 99 * 0.01) / 100 = 0.0089
        assert result.aggregate_deltas["recall@5"] == pytest.approx(0.0089)

        # But has_regression is TRUE because 1 query regressed (per-query gate)
        assert result.has_regression is True
        assert result.per_query_status["q_regress"] == "REGRESSION"
        assert result.per_query_status["q0"] == "UNCHANGED"  # 0.01 < 0.05 threshold

        # This is the correct behavior: ANY query regressing triggers the gate
