"""Unit tests for regression policy enforcement (Task 11.2).

Tests:
- min_query_count guard in compare() (Req 13.5, 13.6)
- load_policy() reads thresholds correctly (Req 13.1)
- merge_policy() overrides base with CLI values (Req 13.2)

Validates: Requirements 13.1, 13.2, 13.5, 13.6
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from spanchor.comparison.compare import compare
from spanchor.comparison.policy import RegressionPolicy, load_policy, merge_policy
from spanchor.errors import ComparisonError
from spanchor.models.run import Run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_run(per_query_metrics: dict[str, dict[str, float]]) -> Run:
    """Build a minimal Run for testing."""
    return Run(
        timestamp="2024-01-01T00:00:00Z",
        queries=tuple(),
        per_query_metrics=per_query_metrics,
        aggregate_metrics={},
        config={},
        mapper_stats={},
    )


def write_json_policy(tmp_path: Path, data: dict) -> Path:
    """Write a dict to a JSON file and return its path."""
    p = tmp_path / "policy.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# min_query_count guard in compare() (Req 13.5, 13.6)
# ---------------------------------------------------------------------------


class TestMinQueryCountGuard:
    """Tests for the minimum-query-count guard in compare()."""

    def test_raises_when_common_queries_below_min(self):
        """ComparisonError raised when fewer common queries than min_query_count. (Req 13.6)"""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        # 1 common query, but we require 5
        with pytest.raises(ComparisonError) as exc_info:
            compare(baseline, candidate, {}, min_query_count=5)

        msg = str(exc_info.value)
        assert "5" in msg  # the required minimum
        assert "1" in msg  # the actual count

    def test_error_message_is_descriptive(self):
        """Error message includes required minimum and actual count."""
        baseline = make_run({"q1": {"recall@5": 0.80}, "q2": {"recall@5": 0.70}})
        candidate = make_run({"q1": {"recall@5": 0.85}, "q2": {"recall@5": 0.75}})

        with pytest.raises(ComparisonError) as exc_info:
            compare(baseline, candidate, {}, min_query_count=10)

        msg = str(exc_info.value)
        assert "10" in msg   # required minimum
        assert "2" in msg    # actual common count

    def test_passes_when_common_queries_equal_min(self):
        """No error when common query count exactly equals min_query_count. (Req 13.5)"""
        metrics = {f"q{i}": {"recall@5": 0.80} for i in range(5)}
        baseline = make_run(metrics)
        candidate = make_run(metrics)

        # Should not raise
        result = compare(baseline, candidate, {}, min_query_count=5)
        assert len(result.per_query_deltas) == 5

    def test_passes_when_common_queries_exceed_min(self):
        """No error when common query count exceeds min_query_count."""
        metrics = {f"q{i}": {"recall@5": 0.80} for i in range(10)}
        baseline = make_run(metrics)
        candidate = make_run(metrics)

        result = compare(baseline, candidate, {}, min_query_count=5)
        assert len(result.per_query_deltas) == 10

    def test_no_guard_when_min_query_count_is_none(self):
        """No error when min_query_count is None (default). (Req 13.5)"""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        # Should not raise regardless of query count
        result = compare(baseline, candidate, {}, min_query_count=None)
        assert "q1" in result.per_query_deltas

    def test_raises_before_computing_deltas(self):
        """Guard fires before any delta computation (fail-fast)."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        with pytest.raises(ComparisonError):
            compare(baseline, candidate, {"recall@5": 0.05}, min_query_count=3)

    def test_min_query_count_zero_always_passes(self):
        """min_query_count=0 is a no-op — any non-empty intersection passes."""
        baseline = make_run({"q1": {"recall@5": 0.80}})
        candidate = make_run({"q1": {"recall@5": 0.85}})

        result = compare(baseline, candidate, {}, min_query_count=0)
        assert "q1" in result.per_query_deltas

    def test_counts_only_common_queries(self):
        """Guard counts common queries, not total queries from either run."""
        # baseline has 10 queries, candidate has 10, but only 2 in common
        baseline_metrics = {f"b{i}": {"recall@5": 0.80} for i in range(8)}
        baseline_metrics.update({"shared1": {"recall@5": 0.80}, "shared2": {"recall@5": 0.80}})

        candidate_metrics = {f"c{i}": {"recall@5": 0.85} for i in range(8)}
        candidate_metrics.update({"shared1": {"recall@5": 0.85}, "shared2": {"recall@5": 0.85}})

        baseline = make_run(baseline_metrics)
        candidate = make_run(candidate_metrics)

        with pytest.raises(ComparisonError) as exc_info:
            compare(baseline, candidate, {}, min_query_count=5)

        assert "2" in str(exc_info.value)  # actual common count


# ---------------------------------------------------------------------------
# load_policy() (Req 13.1)
# ---------------------------------------------------------------------------


class TestLoadPolicy:
    """Tests for load_policy() reading thresholds from config files."""

    def test_loads_thresholds_from_nested_format(self, tmp_path):
        """load_policy reads nested thresholds dict correctly. (Req 13.1)"""
        p = write_json_policy(tmp_path, {
            "thresholds": {
                "recall@5": 0.05,
                "hit@5": 0.10,
            }
        })

        policy = load_policy(p)

        assert policy.thresholds["recall@5"] == pytest.approx(0.05)
        assert policy.thresholds["hit@5"] == pytest.approx(0.10)

    def test_loads_thresholds_from_flat_format(self, tmp_path):
        """load_policy reads flat metric-key format correctly."""
        p = write_json_policy(tmp_path, {
            "recall@5": 0.05,
            "precision@5": 0.08,
        })

        policy = load_policy(p)

        assert policy.thresholds["recall@5"] == pytest.approx(0.05)
        assert policy.thresholds["precision@5"] == pytest.approx(0.08)

    def test_loads_min_query_count(self, tmp_path):
        """load_policy reads min_query_count field. (Req 13.5)"""
        p = write_json_policy(tmp_path, {
            "thresholds": {"recall@5": 0.05},
            "min_query_count": 30,
        })

        policy = load_policy(p)

        assert policy.min_query_count == 30

    def test_min_query_count_none_when_absent(self, tmp_path):
        """min_query_count is None when not present in the file."""
        p = write_json_policy(tmp_path, {"recall@5": 0.05})

        policy = load_policy(p)

        assert policy.min_query_count is None

    def test_accepts_path_string(self, tmp_path):
        """load_policy accepts a string path as well as a Path object."""
        p = write_json_policy(tmp_path, {"recall@5": 0.05})

        policy = load_policy(str(p))

        assert "recall@5" in policy.thresholds

    def test_raises_file_not_found(self, tmp_path):
        """load_policy raises FileNotFoundError for non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_policy(tmp_path / "nonexistent.json")

    def test_raises_on_invalid_json(self, tmp_path):
        """load_policy raises ValueError on malformed JSON."""
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding="utf-8")

        with pytest.raises(ValueError, match="JSON"):
            load_policy(bad)

    def test_raises_on_negative_threshold(self, tmp_path):
        """load_policy raises ValueError when a threshold is negative."""
        p = write_json_policy(tmp_path, {"recall@5": -0.05})

        with pytest.raises(ValueError, match="non-negative"):
            load_policy(p)

    def test_raises_on_non_numeric_threshold(self, tmp_path):
        """load_policy raises ValueError when a threshold is not a number."""
        p = write_json_policy(tmp_path, {"recall@5": "bad"})

        with pytest.raises(ValueError):
            load_policy(p)

    def test_raises_on_non_integer_min_query_count(self, tmp_path):
        """load_policy raises ValueError when min_query_count is not an int."""
        p = write_json_policy(tmp_path, {"min_query_count": 3.5})

        with pytest.raises(ValueError):
            load_policy(p)

    def test_empty_policy_file(self, tmp_path):
        """Empty JSON object produces an empty policy with no thresholds."""
        p = write_json_policy(tmp_path, {})

        policy = load_policy(p)

        assert policy.thresholds == {}
        assert policy.min_query_count is None

    def test_returns_regression_policy_instance(self, tmp_path):
        """load_policy always returns a RegressionPolicy instance."""
        p = write_json_policy(tmp_path, {"recall@5": 0.05})

        policy = load_policy(p)

        assert isinstance(policy, RegressionPolicy)

    def test_nested_and_flat_metrics_combined(self, tmp_path):
        """Nested thresholds and top-level flat keys are merged."""
        p = write_json_policy(tmp_path, {
            "thresholds": {"recall@5": 0.05},
            "hit@5": 0.10,
        })

        policy = load_policy(p)

        assert policy.thresholds["recall@5"] == pytest.approx(0.05)
        assert policy.thresholds["hit@5"] == pytest.approx(0.10)


# ---------------------------------------------------------------------------
# merge_policy() (Req 13.2)
# ---------------------------------------------------------------------------


class TestMergePolicy:
    """Tests for merge_policy() CLI override merging."""

    def test_override_single_threshold(self):
        """CLI override replaces a specific threshold. (Req 13.2)"""
        base = RegressionPolicy(thresholds={"recall@5": 0.05, "hit@5": 0.10})

        merged = merge_policy(base, {"recall@5": 0.03})

        assert merged.thresholds["recall@5"] == pytest.approx(0.03)
        assert merged.thresholds["hit@5"] == pytest.approx(0.10)  # unchanged

    def test_override_adds_new_threshold(self):
        """CLI override can add a metric not in the base policy. (Req 13.2)"""
        base = RegressionPolicy(thresholds={"recall@5": 0.05})

        merged = merge_policy(base, {"precision@5": 0.08})

        assert merged.thresholds["recall@5"] == pytest.approx(0.05)
        assert merged.thresholds["precision@5"] == pytest.approx(0.08)

    def test_override_min_query_count(self):
        """CLI override replaces min_query_count. (Req 13.2)"""
        base = RegressionPolicy(thresholds={}, min_query_count=20)

        merged = merge_policy(base, {"min_query_count": 50})

        assert merged.min_query_count == 50

    def test_none_values_are_ignored(self):
        """None-valued override keys leave base values intact. (Req 13.2)"""
        base = RegressionPolicy(thresholds={"recall@5": 0.05}, min_query_count=20)

        merged = merge_policy(base, {"recall@5": None, "min_query_count": None})

        assert merged.thresholds["recall@5"] == pytest.approx(0.05)
        assert merged.min_query_count == 20

    def test_empty_overrides_returns_copy_of_base(self):
        """Empty overrides dict leaves base untouched."""
        base = RegressionPolicy(thresholds={"recall@5": 0.05}, min_query_count=10)

        merged = merge_policy(base, {})

        assert merged.thresholds == base.thresholds
        assert merged.min_query_count == base.min_query_count

    def test_does_not_mutate_base(self):
        """merge_policy never mutates the original base policy."""
        base = RegressionPolicy(thresholds={"recall@5": 0.05})
        original_thresholds = dict(base.thresholds)

        merge_policy(base, {"recall@5": 0.99})

        assert base.thresholds == original_thresholds

    def test_override_with_thresholds_dict(self):
        """Overrides key 'thresholds' merges an entire dict of thresholds."""
        base = RegressionPolicy(thresholds={"recall@5": 0.05})

        merged = merge_policy(base, {"thresholds": {"hit@5": 0.10, "precision@5": 0.07}})

        assert merged.thresholds["recall@5"] == pytest.approx(0.05)  # kept from base
        assert merged.thresholds["hit@5"] == pytest.approx(0.10)
        assert merged.thresholds["precision@5"] == pytest.approx(0.07)

    def test_override_sets_min_query_count_from_none(self):
        """CLI override can set min_query_count when base has None."""
        base = RegressionPolicy(thresholds={}, min_query_count=None)

        merged = merge_policy(base, {"min_query_count": 25})

        assert merged.min_query_count == 25

    def test_multiple_overrides_applied_together(self):
        """Multiple override keys are all applied in one call. (Req 13.2)"""
        base = RegressionPolicy(thresholds={"recall@5": 0.05}, min_query_count=10)

        merged = merge_policy(base, {
            "recall@5": 0.02,
            "hit@5": 0.08,
            "min_query_count": 30,
        })

        assert merged.thresholds["recall@5"] == pytest.approx(0.02)
        assert merged.thresholds["hit@5"] == pytest.approx(0.08)
        assert merged.min_query_count == 30

    def test_to_policy_dict_returns_thresholds(self):
        """RegressionPolicy.to_policy_dict() returns the thresholds dict."""
        policy = RegressionPolicy(thresholds={"recall@5": 0.05, "hit@5": 0.10})

        d = policy.to_policy_dict()

        assert d == {"recall@5": 0.05, "hit@5": 0.10}

    def test_to_policy_dict_is_a_copy(self):
        """to_policy_dict() returns a copy, not the original dict."""
        policy = RegressionPolicy(thresholds={"recall@5": 0.05})

        d = policy.to_policy_dict()
        d["recall@5"] = 0.99  # mutate the copy

        # Original policy should be unchanged
        assert policy.thresholds["recall@5"] == pytest.approx(0.05)
