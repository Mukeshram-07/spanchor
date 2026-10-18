"""Tests for set-wise retrieval evaluation metrics (Feature 5).

Tests cover:
- span_concentration (structural clustering)
- fragmentation_ratio (spatial spread)
- pairwise_overlap (internal redundancy)

All tests verify:
1. Edge cases (empty, singleton, duplicates, etc.)
2. Rank independence (set-wise behavior)
3. Document boundary isolation
4. Range and normalization
5. Counterexamples against existing metrics
"""

import pytest

from spanchor.evaluation.setwise import (
    fragmentation_ratio,
    pairwise_overlap,
    span_concentration,
)

# ============================================================================
# SPAN CONCENTRATION TESTS
# ============================================================================


class TestSpanConcentration:
    """Tests for span_concentration metric."""

    def test_empty_set(self) -> None:
        """Empty retrieval set should return 0.0."""
        assert span_concentration([]) == 0.0

    def test_singleton(self) -> None:
        """Single span should have maximum concentration."""
        assert span_concentration([(0, 50)]) == 1.0

    def test_identical_spans(self) -> None:
        """Identical spans merge into one region."""
        result = span_concentration([(0, 50), (0, 50)])
        assert result == 1.0

    def test_duplicate_spans(self) -> None:
        """Multiple identical spans don't increase concentration above 1.0."""
        result = span_concentration([(0, 50), (0, 50), (0, 50)])
        assert result == 1.0

    def test_nested_spans(self) -> None:
        """Nested spans merge into one region."""
        result = span_concentration([(0, 100), (25, 75)])
        assert result == 1.0

    def test_overlapping_spans(self) -> None:
        """Overlapping spans merge into single cluster."""
        result = span_concentration([(0, 100), (50, 150)])
        assert result == 1.0

    def test_disjoint_equal_size(self) -> None:
        """Two equal disjoint regions have concentration 0.5."""
        result = span_concentration([(0, 50), (100, 150)])
        assert result == pytest.approx(0.5)

    def test_disjoint_unequal_size(self) -> None:
        """Larger region dominates concentration."""
        result = span_concentration([(0, 80), (100, 120)])
        assert result == pytest.approx(0.8)

    def test_adjacent_spans(self) -> None:
        """Adjacent intervals merge into one region."""
        result = span_concentration([(0, 50), (50, 100)])
        assert result == 1.0

    def test_many_small_fragments(self) -> None:
        """Many small fragments reduce concentration."""
        spans = [(i * 20, i * 20 + 10) for i in range(10)]
        result = span_concentration(spans)
        # 10 fragments of size 10 each = max 10 out of total 100
        assert result == pytest.approx(0.1)

    def test_monotonicity_increasing(self) -> None:
        """Concentration increases with larger dominant cluster."""
        c1 = span_concentration([(0, 50), (100, 150)])
        c2 = span_concentration([(0, 80), (100, 120)])
        c3 = span_concentration([(0, 95), (100, 105)])
        assert c1 < c2 < c3

    def test_monotonicity_fragmentation(self) -> None:
        """Concentration decreases with more fragments."""
        c1 = span_concentration([(0, 100)])
        c2 = span_concentration([(0, 50), (100, 150)])
        c3 = span_concentration([(0, 33), (50, 83), (100, 133)])
        assert c1 > c2 > c3

    def test_range(self) -> None:
        """Concentration is always in [0.0, 1.0]."""
        test_cases = [
            [],
            [(0, 50)],
            [(0, 50), (100, 150)],
            [(0, 10), (20, 30), (40, 50), (60, 70)],
        ]
        for spans in test_cases:
            result = span_concentration(spans)
            assert 0.0 <= result <= 1.0

    def test_rank_independence(self) -> None:
        """Reordering spans doesn't change result."""
        spans_original = [(0, 50), (100, 150), (50, 100)]
        spans_reordered = [(50, 100), (0, 50), (100, 150)]

        result1 = span_concentration(spans_original)
        result2 = span_concentration(spans_reordered)

        assert result1 == result2

    def test_complex_overlapping(self) -> None:
        """Complex overlapping pattern."""
        # Multiple overlapping spans that merge to one region
        spans = [(0, 60), (40, 100), (80, 120)]
        result = span_concentration(spans)
        # Union is [0, 120), max cluster is 120, total is 120
        assert result == 1.0

    def test_gap_between_clusters(self) -> None:
        """Gap between clusters reduces concentration."""
        # Two clusters: [0, 50) and [200, 250)
        # Larger cluster is 50, total is 100
        spans = [(0, 50), (200, 250)]
        result = span_concentration(spans)
        assert result == 0.5


# ============================================================================
# FRAGMENTATION RATIO TESTS
# ============================================================================


class TestFragmentationRatio:
    """Tests for fragmentation_ratio metric."""

    def test_empty_set(self) -> None:
        """Empty retrieval set should return 0.0."""
        assert fragmentation_ratio([]) == 0.0

    def test_singleton(self) -> None:
        """Single span is undefined (< 2 results) → return 0.0."""
        assert fragmentation_ratio([(0, 50)]) == 0.0

    def test_two_identical_spans(self) -> None:
        """Identical spans merge to one fragment."""
        result = fragmentation_ratio([(0, 50), (0, 50)])
        # (1 fragment - 1) / (2 results - 1) = 0 / 1 = 0.0
        assert result == 0.0

    def test_two_duplicate_spans(self) -> None:
        """Duplicates merge to one fragment."""
        result = fragmentation_ratio([(0, 50), (0, 50)])
        assert result == 0.0

    def test_two_disjoint_spans(self) -> None:
        """Two disjoint results create two fragments."""
        result = fragmentation_ratio([(0, 50), (100, 150)])
        # (2 fragments - 1) / (2 results - 1) = 1 / 1 = 1.0
        assert result == 1.0

    def test_two_overlapping_spans(self) -> None:
        """Overlapping spans merge to one fragment."""
        result = fragmentation_ratio([(0, 100), (50, 150)])
        # Union is [0, 150), one fragment
        assert result == 0.0

    def test_two_nested_spans(self) -> None:
        """Nested spans merge to one fragment."""
        result = fragmentation_ratio([(0, 100), (25, 75)])
        assert result == 0.0

    def test_two_adjacent_spans(self) -> None:
        """Adjacent spans merge to one fragment."""
        result = fragmentation_ratio([(0, 50), (50, 100)])
        assert result == 0.0

    def test_three_disjoint_spans(self) -> None:
        """Three disjoint results create three fragments."""
        result = fragmentation_ratio([(0, 50), (100, 150), (200, 250)])
        # (3 fragments - 1) / (3 results - 1) = 2 / 2 = 1.0
        assert result == 1.0

    def test_many_disjoint_spans(self) -> None:
        """Many disjoint fragments."""
        spans = [(i * 20, i * 20 + 10) for i in range(10)]
        result = fragmentation_ratio(spans)
        # 10 disjoint fragments, 10 results
        # (10 - 1) / (10 - 1) = 9 / 9 = 1.0
        assert result == 1.0

    def test_partial_merge(self) -> None:
        """Some spans merge, others remain separate."""
        # Three results: (0,50) and (50,100) merge; (200,250) separate
        spans = [(0, 50), (50, 100), (200, 250)]
        result = fragmentation_ratio(spans)
        # Union: [(0, 100), (200, 250)] = 2 fragments
        # (2 - 1) / (3 - 1) = 1 / 2 = 0.5
        assert result == pytest.approx(0.5)

    def test_range(self) -> None:
        """Fragmentation is always in [0.0, 1.0]."""
        test_cases = [
            [(0, 50)],
            [(0, 50), (100, 150)],
            [(0, 10), (20, 30), (40, 50), (60, 70)],
        ]
        for spans in test_cases:
            result = fragmentation_ratio(spans)
            assert 0.0 <= result <= 1.0

    def test_rank_independence(self) -> None:
        """Reordering spans doesn't change result."""
        spans_original = [(0, 50), (100, 150), (50, 100)]
        spans_reordered = [(50, 100), (0, 50), (100, 150)]

        result1 = fragmentation_ratio(spans_original)
        result2 = fragmentation_ratio(spans_reordered)

        assert result1 == result2

    def test_five_results_three_fragments(self) -> None:
        """Five results that produce three fragments."""
        # (0,50), (50,100), (100,150) → [0,150) one fragment
        # (200,250) → second fragment
        # (300,350) → third fragment
        spans = [(0, 50), (50, 100), (100, 150), (200, 250), (300, 350)]
        result = fragmentation_ratio(spans)
        # 3 fragments, 5 results
        # (3 - 1) / (5 - 1) = 2 / 4 = 0.5
        assert result == pytest.approx(0.5)


# ============================================================================
# PAIRWISE OVERLAP TESTS
# ============================================================================


class TestPairwiseOverlap:
    """Tests for pairwise_overlap metric."""

    def test_empty_set(self) -> None:
        """Empty retrieval set should return 0.0."""
        assert pairwise_overlap([]) == 0.0

    def test_singleton(self) -> None:
        """Single span has no pairs → return 0.0."""
        assert pairwise_overlap([(0, 50)]) == 0.0

    def test_two_identical_spans(self) -> None:
        """Identical spans have complete overlap."""
        result = pairwise_overlap([(0, 50), (0, 50)])
        assert result == 1.0

    def test_two_duplicate_spans(self) -> None:
        """Duplicate spans have perfect overlap."""
        result = pairwise_overlap([(10, 60), (10, 60)])
        assert result == 1.0

    def test_two_disjoint_spans(self) -> None:
        """Disjoint spans have no overlap."""
        result = pairwise_overlap([(0, 50), (100, 150)])
        assert result == 0.0

    def test_two_partial_overlap(self) -> None:
        """Partial overlap measured correctly."""
        # [0,100) and [50,150)
        # Intersection: [50,100) = 50 chars
        # MIN(100, 100) = 100
        # overlap = 50 / 100 = 0.5
        result = pairwise_overlap([(0, 100), (50, 150)])
        assert result == pytest.approx(0.5)

    def test_two_nested_small_in_large(self) -> None:
        """Smaller span fully contained in larger."""
        # [0,100) and [25,75)
        # Intersection: [25,75) = 50 chars
        # MIN(100, 50) = 50
        # overlap = 50 / 50 = 1.0
        result = pairwise_overlap([(0, 100), (25, 75)])
        assert result == 1.0

    def test_two_nested_large_in_small(self) -> None:
        """Same as above (MIN is commutative)."""
        result = pairwise_overlap([(25, 75), (0, 100)])
        assert result == 1.0

    def test_three_spans_mixed_overlap(self) -> None:
        """Three spans with mixed overlaps."""
        # (0,100), (50,150), (200,250)
        # Pairs:
        #   (0,100) & (50,150): overlap=50, min=100 → 0.5
        #   (0,100) & (200,250): overlap=0, min=100 → 0.0
        #   (50,150) & (200,250): overlap=0, min=100 → 0.0
        # Mean = (0.5 + 0.0 + 0.0) / 3 ≈ 0.167
        result = pairwise_overlap([(0, 100), (50, 150), (200, 250)])
        assert result == pytest.approx(0.5 / 3)

    def test_three_identical_spans(self) -> None:
        """Three identical spans → all pairs have overlap=1.0."""
        # 3 pairs, all with overlap 1.0
        result = pairwise_overlap([(0, 50), (0, 50), (0, 50)])
        assert result == 1.0

    def test_range(self) -> None:
        """Pairwise overlap is always in [0.0, 1.0]."""
        test_cases = [
            [],
            [(0, 50)],
            [(0, 50), (100, 150)],
            [(0, 50), (25, 75)],
            [(0, 20), (10, 30), (20, 40)],
        ]
        for spans in test_cases:
            result = pairwise_overlap(spans)
            assert 0.0 <= result <= 1.0

    def test_rank_independence(self) -> None:
        """Reordering spans doesn't change result."""
        spans_original = [(0, 100), (50, 150)]
        spans_reordered = [(50, 150), (0, 100)]

        result1 = pairwise_overlap(spans_original)
        result2 = pairwise_overlap(spans_reordered)

        assert result1 == result2

    def test_many_pairs_average(self) -> None:
        """Average across many pairs."""
        # Four spans: (0,50), (0,50), (100,150), (100,150)
        # Pairs with overlap:
        #   (0,50) & (0,50): 1.0
        #   (0,50) & (100,150): 0.0
        #   (0,50) & (100,150): 0.0
        #   (0,50) & (100,150): 0.0
        #   (0,50) & (100,150): 0.0
        #   (100,150) & (100,150): 1.0
        # Total 6 pairs, sum = 2.0, mean = 2/6 ≈ 0.333
        spans = [(0, 50), (0, 50), (100, 150), (100, 150)]
        result = pairwise_overlap(spans)
        assert result == pytest.approx(2.0 / 6)


# ============================================================================
# DISTINCTNESS COUNTEREXAMPLES (from final validation)
# ============================================================================


class TestDistinctnessCounterexamples:
    """Test distinctness from existing metrics (regression tests)."""

    def test_concentration_vs_recall_scenario(self) -> None:
        """Span concentration differs from Recall@K with same coverage.

        This test demonstrates that span concentration (structural) differs from
        recall (quality). Two retrieval sets with same union size can have
        different fragment patterns.
        """
        # Baseline: single large span (one contiguous region)
        baseline = [(0, 100)]
        # Candidate: split into 2 disjoint regions with gap
        candidate = [(0, 40), (60, 100)]

        # Both have same total coverage but different fragmentation
        conc_baseline = span_concentration(baseline)
        conc_candidate = span_concentration(candidate)

        # Baseline is one continuous region → full concentration
        assert conc_baseline == pytest.approx(1.0)
        # Candidate has max region = 40, total = 80 → 0.5 concentration
        assert conc_candidate == pytest.approx(0.5)
        assert conc_baseline > conc_candidate

    def test_fragmentation_vs_hit_scenario(self) -> None:
        """Fragmentation differs from Hit@K with same overlap."""
        # Both have overlap with gold, but different fragmentation
        disjoint = [(0, 50), (100, 150)]
        clustered = [(0, 100)]

        frag_disjoint = fragmentation_ratio(disjoint)
        frag_clustered = fragmentation_ratio(clustered)

        assert frag_disjoint > frag_clustered
        assert frag_disjoint == pytest.approx(1.0)
        assert frag_clustered == pytest.approx(0.0)

    def test_pairwise_vs_iou_scenario(self) -> None:
        """Pairwise overlap differs from IoU with same union."""
        # Duplicate spans
        duplicate = [(0, 100), (0, 100)]
        # Adjacent spans
        adjacent = [(0, 50), (50, 100)]

        # Both have same union [0, 100)
        pair_duplicate = pairwise_overlap(duplicate)
        pair_adjacent = pairwise_overlap(adjacent)

        assert pair_duplicate > pair_adjacent
        assert pair_duplicate == pytest.approx(1.0)
        assert pair_adjacent == pytest.approx(0.0)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests with MetricRegistry."""

    def test_metric_registry_has_setwise_metrics(self) -> None:
        """MetricRegistry includes set-wise metrics by default."""
        from spanchor.evaluation.metrics import MetricRegistry

        registry = MetricRegistry()

        assert registry.get("span_concentration") is not None
        assert registry.get("fragmentation_ratio") is not None
        assert registry.get("pairwise_overlap") is not None

    def test_compute_setwise_with_registry(self) -> None:
        """Set-wise metrics can be computed via registry."""
        from spanchor.evaluation.metrics import MetricRegistry

        registry = MetricRegistry()

        gold_spans = [(0, 100)]
        retrieved_spans = [(0, 50), (100, 150)]

        conc = registry.compute_metric(
            "span_concentration",
            gold_spans,
            retrieved_spans
        )
        frag = registry.compute_metric(
            "fragmentation_ratio",
            gold_spans,
            retrieved_spans
        )
        pair = registry.compute_metric(
            "pairwise_overlap",
            gold_spans,
            retrieved_spans
        )

        assert isinstance(conc, float)
        assert isinstance(frag, float)
        assert isinstance(pair, float)

    def test_compute_all_includes_setwise(self) -> None:
        """compute_all() includes set-wise metrics."""
        from spanchor.evaluation.metrics import MetricRegistry

        registry = MetricRegistry()

        gold_spans = [(0, 100)]
        retrieved_spans = [(0, 50), (50, 100)]

        all_metrics = registry.compute_all(gold_spans, retrieved_spans)

        assert "span_concentration" in all_metrics
        assert "fragmentation_ratio" in all_metrics
        assert "pairwise_overlap" in all_metrics
        assert "recall@5" in all_metrics  # Standard metric still present
        assert "precision@5" in all_metrics
