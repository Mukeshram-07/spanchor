"""Unit tests for spanchor.testing.assert_no_regression.

Requirements: 23.1, 23.2, 23.3, 23.4, 23.5
"""

from __future__ import annotations

import pytest

from spanchor.models.query import Query
from spanchor.models.run import Run
from spanchor.testing import assert_no_regression


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_run(per_query_metrics: dict[str, dict[str, float]]) -> Run:
    """Build a minimal Run with the given per_query_metrics."""
    return Run(
        timestamp="2024-01-01T00:00:00Z",
        queries=tuple(
            Query(query_id=qid, question="?", anchors=())
            for qid in per_query_metrics
        ),
        per_query_metrics=per_query_metrics,
        aggregate_metrics={},
        config={},
        mapper_stats={},
    )


# ---------------------------------------------------------------------------
# Req 23.1 – module provides assert_no_regression
# ---------------------------------------------------------------------------


class TestModuleExports:
    def test_importable_from_spanchor_testing(self) -> None:
        from spanchor.testing import assert_no_regression as fn  # noqa: F401
        assert callable(fn)

    def test_importable_from_spanchor_package(self) -> None:
        # spanchor.testing is a sub-module; direct import is the contract
        import spanchor.testing as m
        assert hasattr(m, "assert_no_regression")


# ---------------------------------------------------------------------------
# Req 23.4 – passes silently when no regressions
# ---------------------------------------------------------------------------


class TestPassesSilently:
    def test_identical_runs_pass(self) -> None:
        run = _make_run({"q1": {"recall@5": 0.9}})
        assert_no_regression(run, run, policy={"recall@5": 0.05})

    def test_improvement_passes(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.7}})
        candidate = _make_run({"q1": {"recall@5": 0.9}})
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_small_drop_within_threshold_passes(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.86}})  # drop = 0.04 < 0.05
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_empty_policy_always_passes(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.0}})
        assert_no_regression(baseline, candidate, policy={})

    def test_multiple_queries_all_ok(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}, "q2": {"recall@5": 0.8}})
        candidate = _make_run({"q1": {"recall@5": 0.9}, "q2": {"recall@5": 0.85}})
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_returns_none_on_success(self) -> None:
        run = _make_run({"q1": {"recall@5": 0.9}})
        result = assert_no_regression(run, run, policy={"recall@5": 0.05})
        assert result is None


# ---------------------------------------------------------------------------
# Req 23.3 – raises AssertionError on regression
# ---------------------------------------------------------------------------


class TestRaisesOnRegression:
    def test_single_query_regression_raises(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.7}})  # drop = 0.2 > 0.05
        with pytest.raises(AssertionError):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_one_regressed_one_ok_still_raises(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}, "q2": {"recall@5": 0.8}})
        candidate = _make_run({"q1": {"recall@5": 0.5}, "q2": {"recall@5": 0.85}})
        with pytest.raises(AssertionError):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_exact_threshold_boundary_passes(self) -> None:
        """Drop exactly equal to threshold should NOT be a regression."""
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.85}})  # drop == 0.05 exactly
        # Should pass (not a regression)
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_just_over_threshold_raises(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.8499}})  # drop > 0.05
        with pytest.raises(AssertionError):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})


# ---------------------------------------------------------------------------
# Req 23.5 – failure message includes query_id, metric, values, delta
# ---------------------------------------------------------------------------


class TestFailureMessageContents:
    def test_message_contains_query_id(self) -> None:
        baseline = _make_run({"my-query-123": {"recall@5": 0.9}})
        candidate = _make_run({"my-query-123": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match="my-query-123"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_contains_metric_name(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match="recall@5"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_contains_baseline_value(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match="0.9000"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_contains_candidate_value(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match="0.5000"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_contains_delta(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match=r"delta=-0\.4000"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_contains_threshold(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})
        with pytest.raises(AssertionError, match="threshold=-0.0500"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_lists_regression_count(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}, "q2": {"recall@5": 0.8}})
        candidate = _make_run({"q1": {"recall@5": 0.5}, "q2": {"recall@5": 0.3}})
        with pytest.raises(AssertionError, match="2 quer"):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_message_multiple_metrics(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9, "hit@5": 0.8}})
        candidate = _make_run({"q1": {"recall@5": 0.5, "hit@5": 0.3}})
        with pytest.raises(AssertionError) as exc_info:
            assert_no_regression(
                baseline, candidate, policy={"recall@5": 0.05, "hit@5": 0.05}
            )
        msg = str(exc_info.value)
        assert "recall@5" in msg
        assert "hit@5" in msg


# ---------------------------------------------------------------------------
# Req 23.2 – compare() is called with policy thresholds
# ---------------------------------------------------------------------------


class TestPolicyThresholds:
    def test_metric_not_in_policy_is_ignored(self) -> None:
        """A metric that isn't in the policy never triggers regression."""
        baseline = _make_run({"q1": {"precision@5": 0.9}})
        candidate = _make_run({"q1": {"precision@5": 0.0}})
        # Policy has no entry for precision@5 — should pass silently
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.05})

    def test_zero_threshold_catches_any_drop(self) -> None:
        """A threshold of 0.0 means any drop is a regression."""
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.8999}})
        with pytest.raises(AssertionError):
            assert_no_regression(baseline, candidate, policy={"recall@5": 0.0})

    def test_large_threshold_absorbs_drop(self) -> None:
        baseline = _make_run({"q1": {"recall@5": 0.9}})
        candidate = _make_run({"q1": {"recall@5": 0.5}})  # drop = 0.4
        # threshold = 0.5, so drop < threshold → no regression
        assert_no_regression(baseline, candidate, policy={"recall@5": 0.5})
