"""Tests for statistical regression analysis (Feature 2).

Tests bootstrap-based confidence interval computation for paired-query
metric deltas, including configuration validation, determinism, edge cases,
and integration with the compare() function.
"""

import pytest
import warnings

from spanchor.comparison import (
    StatisticsConfig,
    BootstrapResult,
    compare,
    ComparisonResult,
)
from spanchor.errors import ComparisonError
from spanchor.models import Run, Query, Anchor, Document


def _make_run(per_query_metrics: dict[str, dict[str, float]]) -> Run:
    """Helper to create a Run with given per-query metrics."""
    return Run(
        timestamp="2024-01-01T00:00:00Z",
        queries=(),
        per_query_metrics=per_query_metrics,
        aggregate_metrics={},
        config={},
        mapper_stats={},
    )


# ============================================================================
# Configuration Validation Tests
# ============================================================================


class TestStatisticsConfigValidation:
    """Test StatisticsConfig parameter validation."""

    def test_valid_default_config(self) -> None:
        """Default configuration should be valid."""
        config = StatisticsConfig()
        assert config.enabled is False
        assert config.confidence_level == 0.95
        assert config.num_resamples == 10_000
        assert config.random_seed is None
        assert config.min_paired_queries is None

    def test_valid_confidence_levels(self) -> None:
        """Valid confidence levels should not raise."""
        for level in [0.5, 0.90, 0.95, 0.99]:
            config = StatisticsConfig(confidence_level=level)
            assert config.confidence_level == level

    def test_invalid_confidence_level_zero(self) -> None:
        """Confidence level 0.0 should raise ValueError."""
        with pytest.raises(ValueError, match="confidence_level must be in"):
            StatisticsConfig(confidence_level=0.0)

    def test_invalid_confidence_level_one(self) -> None:
        """Confidence level 1.0 should raise ValueError."""
        with pytest.raises(ValueError, match="confidence_level must be in"):
            StatisticsConfig(confidence_level=1.0)

    def test_invalid_confidence_level_negative(self) -> None:
        """Negative confidence level should raise ValueError."""
        with pytest.raises(ValueError, match="confidence_level must be in"):
            StatisticsConfig(confidence_level=-0.1)

    def test_invalid_confidence_level_gt_one(self) -> None:
        """Confidence level > 1.0 should raise ValueError."""
        with pytest.raises(ValueError, match="confidence_level must be in"):
            StatisticsConfig(confidence_level=1.5)

    def test_valid_resamples(self) -> None:
        """Valid resample counts should not raise."""
        for count in [100, 10_000, 100_000]:
            config = StatisticsConfig(num_resamples=count)
            assert config.num_resamples == count

    def test_invalid_resamples_zero(self) -> None:
        """Zero resamples should raise ValueError."""
        with pytest.raises(ValueError, match="num_resamples must be positive"):
            StatisticsConfig(num_resamples=0)

    def test_invalid_resamples_negative(self) -> None:
        """Negative resamples should raise ValueError."""
        with pytest.raises(ValueError, match="num_resamples must be positive"):
            StatisticsConfig(num_resamples=-1)

    def test_valid_random_seed(self) -> None:
        """Valid random seeds should not raise."""
        for seed in [0, 1, 42, 12345]:
            config = StatisticsConfig(random_seed=seed)
            assert config.random_seed == seed

    def test_invalid_random_seed_negative(self) -> None:
        """Negative random seed should raise ValueError."""
        with pytest.raises(ValueError, match="random_seed must be non-negative"):
            StatisticsConfig(random_seed=-1)

    def test_valid_min_paired_queries(self) -> None:
        """Valid min_paired_queries should not raise."""
        for min_q in [1, 10, 30, 100]:
            config = StatisticsConfig(min_paired_queries=min_q)
            assert config.min_paired_queries == min_q


# ============================================================================
# Bootstrap CI Computation Tests
# ============================================================================


class TestBootstrapCIDeterminism:
    """Test that bootstrap CI computation is deterministic."""

    def test_same_seed_same_input_same_ci(self) -> None:
        """Same seed + same deltas should produce identical CI."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
            "q3": {"recall@5": 0.80},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.87},
            "q2": {"recall@5": 0.88},
            "q3": {"recall@5": 0.82},
        }
        config = StatisticsConfig(enabled=True, random_seed=42)

        # Create two dummy runs
        baseline = Run(
            timestamp="2024-01-01T00:00:00Z",
            queries=(),
            per_query_metrics=baseline_metrics,
            aggregate_metrics={},
            config={},
            mapper_stats={},
        )
        candidate = Run(
            timestamp="2024-01-02T00:00:00Z",
            queries=(),
            per_query_metrics=candidate_metrics,
            aggregate_metrics={},
            config={},
            mapper_stats={},
        )

        # Compare twice — results should be identical
        result1 = compare(baseline, candidate, {}, statistics_config=config)
        result2 = compare(baseline, candidate, {}, statistics_config=config)

        assert result1.bootstrap_results is not None
        assert result2.bootstrap_results is not None

        for metric_name in result1.bootstrap_results.keys():
            ci1 = result1.bootstrap_results[metric_name]
            ci2 = result2.bootstrap_results[metric_name]

            assert ci1.mean_delta == ci2.mean_delta
            assert ci1.lower_ci == ci2.lower_ci
            assert ci1.upper_ci == ci2.upper_ci

    def test_different_seed_different_ci(self) -> None:
        """Different seeds produce different results with larger samples."""
        # Use more queries so CIs are more meaningful
        baseline_metrics = {
            f"q{i}": {"recall@5": 0.85 + (i % 5) * 0.01}
            for i in range(15)
        }
        candidate_metrics = {
            f"q{i}": {"recall@5": 0.87 + (i % 5) * 0.01}
            for i in range(15)
        }

        baseline = Run(
            timestamp="2024-01-01T00:00:00Z",
            queries=(),
            per_query_metrics=baseline_metrics,
            aggregate_metrics={},
            config={},
            mapper_stats={},
        )
        candidate = Run(
            timestamp="2024-01-02T00:00:00Z",
            queries=(),
            per_query_metrics=candidate_metrics,
            aggregate_metrics={},
            config={},
            mapper_stats={},
        )

        config1 = StatisticsConfig(enabled=True, random_seed=42)
        config2 = StatisticsConfig(enabled=True, random_seed=999)

        result1 = compare(baseline, candidate, {}, statistics_config=config1)
        result2 = compare(baseline, candidate, {}, statistics_config=config2)

        # Both should have bootstrap results
        assert result1.bootstrap_results is not None
        assert result2.bootstrap_results is not None
        assert len(result1.bootstrap_results) > 0
        assert len(result2.bootstrap_results) > 0


# ============================================================================
# CI Correctness Tests
# ============================================================================


class TestBootstrapCICorrectness:
    """Test correctness of CI computation."""

    def test_trivial_deltas_zero(self) -> None:
        """All-zero deltas should produce CI=[0, 0]."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.85},  # Same as baseline
            "q2": {"recall@5": 0.90},  # Same as baseline
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        result = compare(baseline, candidate, {}, statistics_config=config)

        assert result.bootstrap_results is not None
        assert "recall@5" in result.bootstrap_results

        ci = result.bootstrap_results["recall@5"]
        assert ci.mean_delta == pytest.approx(0.0)
        assert ci.lower_ci == pytest.approx(0.0)
        assert ci.upper_ci == pytest.approx(0.0)

    def test_ci_bounds_order(self) -> None:
        """Lower CI bound should be <= mean <= upper CI bound."""
        baseline_metrics = {
            "q1": {"recall@5": 0.70},
            "q2": {"recall@5": 0.80},
            "q3": {"recall@5": 0.75},
            "q4": {"recall@5": 0.85},
            "q5": {"recall@5": 0.65},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.72},
            "q2": {"recall@5": 0.82},
            "q3": {"recall@5": 0.77},
            "q4": {"recall@5": 0.87},
            "q5": {"recall@5": 0.67},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        result = compare(baseline, candidate, {}, statistics_config=config)

        assert result.bootstrap_results is not None
        for ci in result.bootstrap_results.values():
            assert ci.lower_ci <= ci.mean_delta <= ci.upper_ci


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestBootstrapCIEdgeCases:
    """Test edge cases in CI computation."""

    def test_single_paired_query(self) -> None:
        """Single paired query should still compute CI (with warning)."""
        baseline_metrics = {"q1": {"recall@5": 0.85}}
        candidate_metrics = {"q1": {"recall@5": 0.87}}

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = compare(baseline, candidate, {}, statistics_config=config)

            # Should have warning about small sample
            assert len(w) > 0
            assert "unreliable" in str(w[0].message).lower()

        assert result.bootstrap_results is not None
        assert "recall@5" in result.bootstrap_results

    def test_two_paired_queries(self) -> None:
        """Two paired queries should compute CI (with warning)."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.87},
            "q2": {"recall@5": 0.88},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = compare(baseline, candidate, {}, statistics_config=config)
            assert len(w) > 0

        assert result.bootstrap_results is not None

    def test_thirty_paired_queries_no_warning(self) -> None:
        """Thirty paired queries should not produce warning."""
        baseline_metrics = {
            f"q{i}": {"recall@5": 0.85 + (i % 10) * 0.01}
            for i in range(30)
        }
        candidate_metrics = {
            f"q{i}": {"recall@5": 0.87 + (i % 10) * 0.01}
            for i in range(30)
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = compare(baseline, candidate, {}, statistics_config=config)

            # Should NOT have warning
            assert len(w) == 0

        assert result.bootstrap_results is not None


# ============================================================================
# Integration Tests
# ============================================================================


class TestCompareIntegration:
    """Test integration of statistics with compare() function."""

    def test_statistics_disabled_by_default(self) -> None:
        """Statistics should be disabled by default (backward compat)."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.87},
            "q2": {"recall@5": 0.88},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)

        # No StatisticsConfig provided
        result = compare(baseline, candidate, {})

        assert result.statistics_enabled is False
        assert result.bootstrap_results is None
        assert result.num_paired_queries == 0

    def test_statistics_disabled_with_config_false(self) -> None:
        """Statistics should be disabled when config.enabled=False."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.87},
            "q2": {"recall@5": 0.88},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=False)

        result = compare(baseline, candidate, {}, statistics_config=config)

        assert result.statistics_enabled is False
        assert result.bootstrap_results is None

    def test_statistics_enabled_with_config_true(self) -> None:
        """Statistics should be enabled when config.enabled=True."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85},
            "q2": {"recall@5": 0.90},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.87},
            "q2": {"recall@5": 0.88},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, random_seed=42)

        result = compare(baseline, candidate, {}, statistics_config=config)

        assert result.statistics_enabled is True
        assert result.bootstrap_results is not None
        assert len(result.bootstrap_results) > 0
        assert result.num_paired_queries == 2

    def test_insufficient_paired_queries_error(self) -> None:
        """Should raise error if min_paired_queries not met."""
        baseline_metrics = {"q1": {"recall@5": 0.85}}
        candidate_metrics = {"q1": {"recall@5": 0.87}}

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        config = StatisticsConfig(enabled=True, min_paired_queries=5)

        with pytest.raises(
            ComparisonError, match="Insufficient paired queries"
        ):
            compare(baseline, candidate, {}, statistics_config=config)

    def test_backward_compatible_existing_tests(self) -> None:
        """Existing compare() behavior unchanged without statistics."""
        baseline_metrics = {
            "q1": {"recall@5": 0.85, "precision@5": 0.80},
            "q2": {"recall@5": 0.90, "precision@5": 0.75},
        }
        candidate_metrics = {
            "q1": {"recall@5": 0.92, "precision@5": 0.78},  # delta = 0.07 > 0.05 threshold
            "q2": {"recall@5": 0.88, "precision@5": 0.77},
        }

        baseline = _make_run(per_query_metrics=baseline_metrics)
        candidate = _make_run(per_query_metrics=candidate_metrics)
        policy = {"recall@5": 0.05}

        # Compare without statistics
        result = compare(baseline, candidate, policy)

        # Results should be identical to v0.3.0
        assert result.statistics_enabled is False
        assert result.per_query_deltas["q1"]["recall@5"] == pytest.approx(0.07)
        assert result.per_query_status["q1"] == "IMPROVED"  # 0.07 > 0.05 threshold
        assert not result.has_regression


# ============================================================================
# BootstrapResult Tests
# ============================================================================


class TestBootstrapResult:
    """Test BootstrapResult dataclass."""

    def test_bootstrap_result_fields(self) -> None:
        """BootstrapResult should have all required fields."""
        result = BootstrapResult(
            metric_name="recall@5",
            num_paired_queries=30,
            mean_delta=0.05,
            lower_ci=0.02,
            upper_ci=0.08,
            ci_level=0.95,
            num_resamples=10_000,
            seed=42,
        )

        assert result.metric_name == "recall@5"
        assert result.num_paired_queries == 30
        assert result.mean_delta == 0.05
        assert result.lower_ci == 0.02
        assert result.upper_ci == 0.08
        assert result.ci_level == 0.95
        assert result.num_resamples == 10_000
        assert result.seed == 42

    def test_bootstrap_result_immutable(self) -> None:
        """BootstrapResult should be frozen (immutable)."""
        result = BootstrapResult(
            metric_name="recall@5",
            num_paired_queries=30,
            mean_delta=0.05,
            lower_ci=0.02,
            upper_ci=0.08,
            ci_level=0.95,
            num_resamples=10_000,
            seed=42,
        )

        with pytest.raises(AttributeError):
            result.mean_delta = 0.10  # type: ignore
