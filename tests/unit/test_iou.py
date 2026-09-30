"""Unit tests for IoU (Intersection-over-Union) diagnostic metric."""

import pytest

from spanchor.evaluation.iou import iou


class TestIoUBasicCases:
    """Basic test cases for IoU metric."""

    def test_empty_both_sets(self):
        """IoU returns 0.0 when both sets are empty (Requirement 9.3)."""
        assert iou([], []) == 0.0

    def test_empty_gold_spans(self):
        """IoU returns 0.0 when gold spans are empty."""
        assert iou([], [(0, 10)]) == 0.0

    def test_empty_retrieved_spans(self):
        """IoU returns 0.0 when retrieved spans are empty."""
        assert iou([(0, 10)], []) == 0.0

    def test_perfect_overlap_single_span(self):
        """IoU returns 1.0 for identical single spans."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]
        assert iou(gold, retrieved) == 1.0

    def test_perfect_overlap_multiple_spans(self):
        """IoU returns 1.0 when multiple spans match perfectly."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (20, 30)]
        assert iou(gold, retrieved) == 1.0

    def test_no_overlap(self):
        """IoU returns 0.0 when there is no overlap."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        assert iou(gold, retrieved) == 0.0

    def test_partial_overlap_half(self):
        """IoU computes correctly for 50% overlap."""
        gold = [(0, 10)]
        retrieved = [(5, 15)]
        # Intersection: [5, 10) = 5 chars
        # Union: [0, 15) = 15 chars
        # IoU = 5/15 ≈ 0.333...
        assert abs(iou(gold, retrieved) - 0.3333333333333333) < 1e-9

    def test_contained_span(self):
        """IoU when retrieved is contained within gold."""
        gold = [(0, 20)]
        retrieved = [(5, 15)]
        # Intersection: [5, 15) = 10 chars
        # Union: [0, 20) = 20 chars
        # IoU = 10/20 = 0.5
        assert iou(gold, retrieved) == 0.5

    def test_gold_contained_in_retrieved(self):
        """IoU when gold is contained within retrieved."""
        gold = [(5, 15)]
        retrieved = [(0, 20)]
        # Intersection: [5, 15) = 10 chars
        # Union: [0, 20) = 20 chars
        # IoU = 10/20 = 0.5
        assert iou(gold, retrieved) == 0.5


class TestIoUSymmetry:
    """Tests for IoU symmetry property (Requirement 9.4)."""

    def test_symmetry_partial_overlap(self):
        """IoU(G, R) == IoU(R, G) for partial overlap."""
        gold = [(0, 10)]
        retrieved = [(5, 15)]
        assert iou(gold, retrieved) == iou(retrieved, gold)

    def test_symmetry_no_overlap(self):
        """IoU(G, R) == IoU(R, G) for no overlap."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        assert iou(gold, retrieved) == iou(retrieved, gold)

    def test_symmetry_perfect_overlap(self):
        """IoU(G, R) == IoU(R, G) for perfect overlap."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (20, 30)]
        assert iou(gold, retrieved) == iou(retrieved, gold)

    def test_symmetry_contained(self):
        """IoU(G, R) == IoU(R, G) when one set is contained."""
        gold = [(0, 20)]
        retrieved = [(5, 15)]
        assert iou(gold, retrieved) == iou(retrieved, gold)

    def test_symmetry_multiple_overlaps(self):
        """IoU(G, R) == IoU(R, G) with complex overlaps."""
        gold = [(0, 5), (10, 15), (20, 25)]
        retrieved = [(3, 12), (22, 30)]
        result_forward = iou(gold, retrieved)
        result_backward = iou(retrieved, gold)
        assert abs(result_forward - result_backward) < 1e-9

    def test_symmetry_empty_sets(self):
        """IoU(G, R) == IoU(R, G) for empty sets."""
        gold = []
        retrieved = [(0, 10)]
        assert iou(gold, retrieved) == iou(retrieved, gold)


class TestIoUBounds:
    """Tests that IoU is always in [0, 1] (Requirement 9.2)."""

    def test_bounds_zero(self):
        """IoU >= 0 for no overlap."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        result = iou(gold, retrieved)
        assert result >= 0.0
        assert result == 0.0

    def test_bounds_one(self):
        """IoU <= 1 for perfect overlap."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]
        result = iou(gold, retrieved)
        assert result <= 1.0
        assert result == 1.0

    def test_bounds_partial(self):
        """0 <= IoU <= 1 for partial overlap."""
        gold = [(0, 10)]
        retrieved = [(5, 15)]
        result = iou(gold, retrieved)
        assert 0.0 <= result <= 1.0

    def test_bounds_multiple_spans(self):
        """0 <= IoU <= 1 for multiple spans."""
        gold = [(0, 5), (10, 15), (20, 25)]
        retrieved = [(3, 8), (12, 18), (22, 27)]
        result = iou(gold, retrieved)
        assert 0.0 <= result <= 1.0

    def test_bounds_disjoint_multiple(self):
        """0 <= IoU <= 1 for disjoint multiple spans."""
        gold = [(0, 5), (10, 15)]
        retrieved = [(20, 25), (30, 35)]
        result = iou(gold, retrieved)
        assert 0.0 <= result <= 1.0
        assert result == 0.0


class TestIoUOverlappingSpans:
    """Tests with overlapping spans that need merging."""

    def test_overlapping_gold_spans(self):
        """IoU merges overlapping gold spans."""
        gold = [(0, 10), (5, 15)]  # Merges to [0, 15)
        retrieved = [(0, 15)]
        # After merge: gold = [(0, 15)], retrieved = [(0, 15)]
        # IoU = 15/15 = 1.0
        assert iou(gold, retrieved) == 1.0

    def test_overlapping_retrieved_spans(self):
        """IoU merges overlapping retrieved spans."""
        gold = [(0, 15)]
        retrieved = [(0, 10), (5, 15)]  # Merges to [0, 15)
        # After merge: gold = [(0, 15)], retrieved = [(0, 15)]
        # IoU = 15/15 = 1.0
        assert iou(gold, retrieved) == 1.0

    def test_overlapping_both_sets(self):
        """IoU merges overlapping spans in both sets."""
        gold = [(0, 10), (5, 15)]  # Merges to [0, 15)
        retrieved = [(10, 20), (15, 25)]  # Merges to [10, 25)
        # gold = [(0, 15)], retrieved = [(10, 25)]
        # Intersection: [10, 15) = 5 chars
        # Union: [0, 25) = 25 chars
        # IoU = 5/25 = 0.2
        assert iou(gold, retrieved) == 0.2

    def test_adjacent_spans_merged(self):
        """Adjacent spans [a,b) and [b,c) are merged."""
        gold = [(0, 5), (5, 10)]  # Merges to [0, 10)
        retrieved = [(0, 10)]
        assert iou(gold, retrieved) == 1.0


class TestIoUMultipleSpans:
    """Tests with multiple non-overlapping spans."""

    def test_multiple_disjoint_gold(self):
        """IoU with multiple disjoint gold spans."""
        gold = [(0, 5), (10, 15), (20, 25)]  # Total: 15 chars
        retrieved = [(0, 25)]  # Total: 25 chars
        # Intersection: [0, 5) + [10, 15) + [20, 25) = 15 chars
        # Union: [0, 25) = 25 chars
        # IoU = 15/25 = 0.6
        assert iou(gold, retrieved) == 0.6

    def test_multiple_disjoint_retrieved(self):
        """IoU with multiple disjoint retrieved spans."""
        gold = [(0, 25)]  # Total: 25 chars
        retrieved = [(0, 5), (10, 15), (20, 25)]  # Total: 15 chars
        # Intersection: [0, 5) + [10, 15) + [20, 25) = 15 chars
        # Union: [0, 25) = 25 chars
        # IoU = 15/25 = 0.6
        assert iou(gold, retrieved) == 0.6

    def test_partial_coverage_multiple_spans(self):
        """IoU with partial coverage across multiple spans."""
        gold = [(0, 10), (20, 30)]  # Total: 20 chars
        retrieved = [(5, 15), (25, 35)]  # Total: 20 chars
        # gold merged: [(0, 10), (20, 30)] = 20 chars
        # retrieved merged: [(5, 15), (25, 35)] = 20 chars
        # Intersection: [5, 10) + [25, 30) = 5 + 5 = 10 chars
        # Union: [0, 15) + [20, 35) = 15 + 15 = 30 chars
        # IoU = 10/30 ≈ 0.333...
        assert abs(iou(gold, retrieved) - 0.3333333333333333) < 1e-9

    def test_some_spans_overlap_some_dont(self):
        """IoU with mixed overlap patterns."""
        gold = [(0, 10), (20, 30), (40, 50)]
        retrieved = [(5, 15), (20, 25), (60, 70)]
        # gold: [0, 10), [20, 30), [40, 50) = 30 chars total
        # retrieved: [5, 15), [20, 25), [60, 70) = 25 chars total
        # Intersection: [5, 10) + [20, 25) = 5 + 5 = 10 chars
        # Union: [0, 15), [20, 30), [40, 50), [60, 70) = 15 + 10 + 10 + 10 = 45 chars
        # IoU = 10/45 ≈ 0.222...
        result = iou(gold, retrieved)
        expected = 10 / 45
        assert abs(result - expected) < 1e-9


class TestIoUEdgeCases:
    """Edge case tests for IoU."""

    def test_single_character_spans(self):
        """IoU with single character spans [i, i+1)."""
        gold = [(0, 1), (2, 3)]
        retrieved = [(0, 1)]
        # Intersection: [0, 1) = 1 char
        # Union: [0, 1), [2, 3) = 2 chars
        # IoU = 1/2 = 0.5
        assert iou(gold, retrieved) == 0.5

    def test_large_offsets(self):
        """IoU works with large offset values."""
        gold = [(1000000, 1000010)]
        retrieved = [(1000005, 1000015)]
        # Intersection: [1000005, 1000010) = 5 chars
        # Union: [1000000, 1000015) = 15 chars
        # IoU = 5/15 ≈ 0.333...
        assert abs(iou(gold, retrieved) - 0.3333333333333333) < 1e-9

    def test_many_small_spans(self):
        """IoU with many small spans."""
        gold = [(i, i + 1) for i in range(0, 20, 2)]  # 10 single-char spans at even positions
        retrieved = [(i, i + 1) for i in range(1, 20, 2)]  # 9 single-char spans at odd positions
        # No overlap, union = 19 chars (0-19 except position 19)
        # Actually: gold = [0,1), [2,3), ..., [18,19)
        #          retrieved = [1,2), [3,4), ..., [17,18)
        # Union merges all adjacent: [0, 19)
        # Intersection: none (adjacent but not overlapping in half-open intervals)
        assert iou(gold, retrieved) == 0.0

    def test_retrieved_much_larger_than_gold(self):
        """IoU when retrieved spans are much larger."""
        gold = [(10, 20)]  # 10 chars
        retrieved = [(0, 100)]  # 100 chars
        # Intersection: [10, 20) = 10 chars
        # Union: [0, 100) = 100 chars
        # IoU = 10/100 = 0.1
        assert iou(gold, retrieved) == 0.1

    def test_gold_much_larger_than_retrieved(self):
        """IoU when gold spans are much larger."""
        gold = [(0, 100)]  # 100 chars
        retrieved = [(10, 20)]  # 10 chars
        # Intersection: [10, 20) = 10 chars
        # Union: [0, 100) = 100 chars
        # IoU = 10/100 = 0.1
        assert iou(gold, retrieved) == 0.1


class TestIoUComputationDetails:
    """Tests verifying correct computation steps."""

    def test_union_before_intersection(self):
        """IoU unions spans before computing intersection."""
        # Overlapping gold spans should be merged first
        gold = [(0, 5), (3, 8)]  # Merges to [0, 8)
        retrieved = [(0, 4)]
        # Intersection with merged gold: [0, 4) = 4 chars
        # Union: [0, 8) = 8 chars
        # IoU = 4/8 = 0.5
        assert iou(gold, retrieved) == 0.5

    def test_formula_g_intersect_r_over_g_union_r(self):
        """IoU = |G ∩ R| / |G ∪ R| (Requirement 9.1)."""
        gold = [(0, 10), (20, 30)]  # 20 chars total
        retrieved = [(5, 15), (25, 35)]  # 20 chars total

        # Manual computation:
        # G merged: [(0, 10), (20, 30)]
        # R merged: [(5, 15), (25, 35)]
        # G ∩ R: [(5, 10), (25, 30)] = 5 + 5 = 10 chars
        # G ∪ R: [(0, 15), (20, 35)] = 15 + 15 = 30 chars
        # IoU = 10/30

        expected = 10 / 30
        assert abs(iou(gold, retrieved) - expected) < 1e-9

    def test_zero_length_union_gives_zero(self):
        """When |G ∪ R| = 0, IoU = 0 (Requirement 9.3)."""
        # Both empty
        assert iou([], []) == 0.0

        # Zero-length spans (invalid but testing edge case)
        # Note: In practice, zero-length spans shouldn't occur
        gold = [(5, 5)]  # Zero-length
        retrieved = []
        # Union length = 0
        result = iou(gold, retrieved)
        assert result == 0.0


class TestIoUDiagnosticNature:
    """Tests emphasizing IoU is diagnostic only."""

    def test_iou_not_bounded_by_recall(self):
        """IoU can be high even with low recall."""
        gold = [(0, 100)]
        retrieved = [(0, 10)]
        # Recall = 10/100 = 0.1
        # IoU = 10/100 = 0.1
        # (In this case they happen to be equal, but different concept)
        result = iou(gold, retrieved)
        assert result == 0.1

    def test_iou_not_bounded_by_precision(self):
        """IoU can be high even with low precision."""
        gold = [(0, 10)]
        retrieved = [(0, 100)]
        # Precision = 10/100 = 0.1
        # IoU = 10/100 = 0.1
        # (Again, equal here but conceptually different)
        result = iou(gold, retrieved)
        assert result == 0.1

    def test_iou_different_from_recall_precision(self):
        """IoU gives different information than Recall/Precision."""
        gold = [(0, 10)]
        retrieved = [(5, 15)]
        # Intersection: [5, 10) = 5
        # Recall = 5/10 = 0.5
        # Precision = 5/10 = 0.5
        # IoU = 5/15 ≈ 0.333
        result = iou(gold, retrieved)
        assert abs(result - 0.3333333333333333) < 1e-9
        # IoU is lower than both Recall and Precision in this case

    def test_iou_overall_alignment_quality(self):
        """IoU measures overall alignment, not directional coverage."""
        # Scenario: good recall, poor precision
        gold = [(0, 10)]
        retrieved = [(0, 100)]
        # Recall = 10/10 = 1.0 (perfect)
        # Precision = 10/100 = 0.1 (poor)
        # IoU = 10/100 = 0.1 (reflects poor alignment)
        result = iou(gold, retrieved)
        assert result == 0.1

        # Scenario: poor recall, good precision
        gold = [(0, 100)]
        retrieved = [(0, 10)]
        # Recall = 10/100 = 0.1 (poor)
        # Precision = 10/10 = 1.0 (perfect)
        # IoU = 10/100 = 0.1 (reflects poor alignment)
        result = iou(gold, retrieved)
        assert result == 0.1

        # IoU treats both scenarios the same (symmetric)


class TestIoURealWorldScenarios:
    """Real-world-like test scenarios."""

    def test_partial_retrieval_multiple_documents(self):
        """Simulating retrieval across multiple documents."""
        # Gold: relevant passages in doc1 and doc2
        gold = [(0, 100), (500, 600)]  # 200 chars total
        # Retrieved: found both but with noise
        retrieved = [(0, 150), (450, 650)]  # 350 chars total
        # Intersection: [0, 100) + [500, 600) = 200 chars
        # Union: [0, 150) + [450, 650) = 350 chars
        # IoU = 200/350 ≈ 0.571
        result = iou(gold, retrieved)
        expected = 200 / 350
        assert abs(result - expected) < 1e-9

    def test_over_retrieval_scenario(self):
        """Scenario where system retrieves too much."""
        gold = [(100, 200)]  # 100 chars
        retrieved = [(0, 500)]  # 500 chars
        # Intersection: [100, 200) = 100 chars
        # Union: [0, 500) = 500 chars
        # IoU = 100/500 = 0.2
        assert iou(gold, retrieved) == 0.2

    def test_under_retrieval_scenario(self):
        """Scenario where system retrieves too little."""
        gold = [(0, 500)]  # 500 chars
        retrieved = [(100, 200)]  # 100 chars
        # Intersection: [100, 200) = 100 chars
        # Union: [0, 500) = 500 chars
        # IoU = 100/500 = 0.2
        assert iou(gold, retrieved) == 0.2

    def test_mixed_quality_retrieval(self):
        """Mixed quality across multiple queries."""
        # Gold evidence spans
        gold = [(0, 50), (100, 150), (200, 250)]  # 150 chars total
        # Some perfect hits, some misses
        retrieved = [(0, 50), (125, 175), (300, 350)]  # 125 chars total
        # Intersection: [0, 50) + [125, 150) = 50 + 25 = 75 chars
        # Union: [0, 50), [100, 175), [200, 250), [300, 350)
        #      = 50 + 75 + 50 + 50 = 225 chars
        # IoU = 75/225 ≈ 0.333
        result = iou(gold, retrieved)
        expected = 75 / 225
        assert abs(result - expected) < 1e-9
