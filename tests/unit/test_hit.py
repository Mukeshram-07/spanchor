"""Unit tests for Hit@K and FullEvidence@K metrics."""

import pytest

from spanchor.errors import EvaluationError
from spanchor.evaluation.hit import full_evidence_at_k, hit_at_k


class TestHitAtK:
    """Tests for hit_at_k function."""

    def test_single_gold_span_meets_threshold(self):
        """Hit@K returns 1 when gold span meets min_overlap (Requirement 8.1)."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]  # 50% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

    def test_single_gold_span_fails_threshold(self):
        """Hit@K returns 0 when gold span fails min_overlap (Requirement 8.2)."""
        gold = [(0, 10)]
        retrieved = [(0, 4)]  # 40% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0

    def test_any_gold_span_meets_threshold(self):
        """Hit@K returns 1 if ANY gold span meets threshold (Requirement 8.1)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 5)]  # Only first span has 50% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

    def test_no_gold_span_meets_threshold(self):
        """Hit@K returns 0 if NO gold span meets threshold (Requirement 8.2)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 4)]  # Only 40% overlap with first span
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0

    def test_default_min_overlap(self):
        """Default min_overlap is 0.5 (Requirement 8.5)."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]  # Exactly 50% overlap
        # Should succeed with default min_overlap=0.5
        assert hit_at_k(gold, retrieved, k=1) == 1
        # Should fail with slightly less overlap
        retrieved_less = [(0, 4)]  # 40% overlap
        assert hit_at_k(gold, retrieved_less, k=1) == 0

    def test_custom_min_overlap_low(self):
        """Custom min_overlap values work (Requirement 8.6)."""
        gold = [(0, 10)]
        retrieved = [(0, 3)]  # 30% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.3) == 1
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.4) == 0

    def test_custom_min_overlap_high(self):
        """High min_overlap thresholds work (Requirement 8.6)."""
        gold = [(0, 10)]
        retrieved = [(0, 9)]  # 90% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.9) == 1
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.95) == 0

    def test_perfect_overlap(self):
        """Perfect overlap meets any threshold."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]
        assert hit_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1

    def test_zero_overlap(self):
        """Zero overlap fails any positive threshold."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.1) == 0

    def test_k_limits_retrieved_spans(self):
        """Only top-K retrieved spans are used."""
        gold = [(0, 20)]
        retrieved = [(0, 5), (5, 20)]  # Together would give 100% coverage
        # k=1: only first span, 25% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0
        # k=2: both spans, 100% overlap
        assert hit_at_k(gold, retrieved, k=2, min_overlap=0.5) == 1

    def test_multiple_retrieved_spans_union(self):
        """Multiple retrieved spans are unioned."""
        gold = [(0, 10)]
        retrieved = [(0, 3), (3, 6)]  # Union covers [0, 6), 60% overlap
        assert hit_at_k(gold, retrieved, k=2, min_overlap=0.5) == 1

    def test_overlapping_gold_spans_merged(self):
        """Overlapping gold spans are merged before checking."""
        gold = [(0, 10), (5, 15)]  # Union is [0, 15)
        retrieved = [(0, 8)]  # 8/15 ≈ 53% of merged span
        # First span [0, 10): 80% overlap ✓
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

    def test_empty_retrieved_spans(self):
        """Empty retrieved spans gives 0."""
        gold = [(0, 10)]
        retrieved = []
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0

    def test_k_greater_than_retrieved_count(self):
        """K greater than retrieved count uses all spans."""
        gold = [(0, 10)]
        retrieved = [(0, 3)]  # 30% overlap
        assert hit_at_k(gold, retrieved, k=100, min_overlap=0.3) == 1

    def test_multiple_gold_spans_second_meets_threshold(self):
        """Second gold span meeting threshold returns 1."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(22, 32)]  # 80% overlap with second span
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.7) == 1

    def test_partial_overlap_multiple_spans(self):
        """Complex partial overlaps."""
        gold = [(0, 10), (20, 30), (40, 50)]
        retrieved = [(5, 10), (20, 25), (45, 50)]  # Various overlaps
        # First gold: 50%, Second gold: 50%, Third gold: 50%
        assert hit_at_k(gold, retrieved, k=3, min_overlap=0.5) == 1


class TestFullEvidenceAtK:
    """Tests for full_evidence_at_k function."""

    def test_all_gold_spans_meet_threshold(self):
        """FullEvidence@K returns 1 when all gold spans meet threshold (Requirement 8.3)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (20, 30)]  # 100% overlap for both
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.5) == 1

    def test_any_gold_span_fails_threshold(self):
        """FullEvidence@K returns 0 when any gold span fails threshold (Requirement 8.4)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (20, 24)]  # Second span only 40% overlap
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.5) == 0

    def test_single_gold_span_meets_threshold(self):
        """Single gold span meeting threshold returns 1."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]  # 50% overlap
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

    def test_single_gold_span_fails_threshold(self):
        """Single gold span failing threshold returns 0."""
        gold = [(0, 10)]
        retrieved = [(0, 4)]  # 40% overlap
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0

    def test_default_min_overlap(self):
        """Default min_overlap is 0.5 (Requirement 8.5)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 5), (20, 25)]  # Both exactly 50% overlap
        assert full_evidence_at_k(gold, retrieved, k=2) == 1

    def test_custom_min_overlap(self):
        """Custom min_overlap values work (Requirement 8.6)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 8), (20, 28)]  # Both 80% overlap
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.8) == 1
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.9) == 0

    def test_perfect_overlap_all_spans(self):
        """Perfect overlap on all spans."""
        gold = [(0, 10), (20, 30), (40, 50)]
        retrieved = [(0, 10), (20, 30), (40, 50)]
        assert full_evidence_at_k(gold, retrieved, k=3, min_overlap=1.0) == 1

    def test_first_span_fails(self):
        """First gold span failing causes return 0."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 4), (20, 30)]  # First span only 40%
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.5) == 0

    def test_last_span_fails(self):
        """Last gold span failing causes return 0."""
        gold = [(0, 10), (20, 30), (40, 50)]
        retrieved = [(0, 10), (20, 30), (40, 44)]  # Last span only 40%
        assert full_evidence_at_k(gold, retrieved, k=3, min_overlap=0.5) == 0

    def test_k_limits_retrieved_spans(self):
        """Only top-K retrieved spans are used."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (20, 30), (40, 50)]  # Third span irrelevant
        # k=1: only first span covered
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0
        # k=2: both spans covered
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.5) == 1

    def test_multiple_retrieved_cover_one_gold(self):
        """Multiple retrieved spans can combine to cover one gold span."""
        gold = [(0, 10)]
        retrieved = [(0, 3), (3, 6), (6, 10)]  # Together 100%
        assert full_evidence_at_k(gold, retrieved, k=3, min_overlap=1.0) == 1

    def test_overlapping_gold_spans_merged(self):
        """Overlapping gold spans are merged before checking."""
        gold = [(0, 10), (5, 15)]  # Merges to [0, 15)
        retrieved = [(0, 15)]
        # Both merged spans need full coverage
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1

    def test_empty_retrieved_spans(self):
        """Empty retrieved spans gives 0."""
        gold = [(0, 10)]
        retrieved = []
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.1) == 0

    def test_zero_overlap_all_spans(self):
        """Zero overlap on any span returns 0."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10), (40, 50)]  # Second gold has zero overlap
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=0.5) == 0


class TestHitAtKErrors:
    """Tests for hit_at_k error conditions."""

    def test_empty_gold_spans_raises_error(self):
        """Empty gold spans raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)
        assert "Hit@K" in str(exc_info.value)

    def test_zero_length_gold_spans_raises_error(self):
        """Zero-length gold spans raise EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(5, 5)], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)

    def test_k_zero_raises_error(self):
        """K = 0 raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(0, 10)], [(0, 5)], k=0)
        assert "K must be positive" in str(exc_info.value)
        assert "Hit@K" in str(exc_info.value)

    def test_k_negative_raises_error(self):
        """Negative K raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(0, 10)], [(0, 5)], k=-1)
        assert "K must be positive" in str(exc_info.value)

    def test_min_overlap_below_zero_raises_error(self):
        """min_overlap < 0 raises EvaluationError (Requirement 8.7)."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(0, 10)], [(0, 5)], k=1, min_overlap=-0.1)
        assert "min_overlap must be between 0 and 1" in str(exc_info.value)
        assert "Hit@K" in str(exc_info.value)

    def test_min_overlap_above_one_raises_error(self):
        """min_overlap > 1 raises EvaluationError (Requirement 8.7)."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(0, 10)], [(0, 5)], k=1, min_overlap=1.1)
        assert "min_overlap must be between 0 and 1" in str(exc_info.value)

    def test_min_overlap_exactly_zero_allowed(self):
        """min_overlap = 0.0 is valid (Requirement 8.7)."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]  # No overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.0) == 1  # 0% >= 0%

    def test_min_overlap_exactly_one_allowed(self):
        """min_overlap = 1.0 is valid (Requirement 8.7)."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]  # Perfect overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1

    def test_error_includes_values(self):
        """Error messages include relevant values."""
        with pytest.raises(EvaluationError) as exc_info:
            hit_at_k([(0, 10)], [(0, 5)], k=0, min_overlap=0.5)
        error = exc_info.value
        assert error.metric_name == "Hit@K"
        assert error.values == {"k": 0}


class TestFullEvidenceAtKErrors:
    """Tests for full_evidence_at_k error conditions."""

    def test_empty_gold_spans_raises_error(self):
        """Empty gold spans raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)
        assert "FullEvidence@K" in str(exc_info.value)

    def test_zero_length_gold_spans_raises_error(self):
        """Zero-length gold spans raise EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(5, 5)], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)

    def test_k_zero_raises_error(self):
        """K = 0 raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(0, 10)], [(0, 5)], k=0)
        assert "K must be positive" in str(exc_info.value)
        assert "FullEvidence@K" in str(exc_info.value)

    def test_k_negative_raises_error(self):
        """Negative K raises EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(0, 10)], [(0, 5)], k=-1)
        assert "K must be positive" in str(exc_info.value)

    def test_min_overlap_below_zero_raises_error(self):
        """min_overlap < 0 raises EvaluationError (Requirement 8.7)."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(0, 10)], [(0, 5)], k=1, min_overlap=-0.1)
        assert "min_overlap must be between 0 and 1" in str(exc_info.value)
        assert "FullEvidence@K" in str(exc_info.value)

    def test_min_overlap_above_one_raises_error(self):
        """min_overlap > 1 raises EvaluationError (Requirement 8.7)."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(0, 10)], [(0, 5)], k=1, min_overlap=1.1)
        assert "min_overlap must be between 0 and 1" in str(exc_info.value)

    def test_min_overlap_exactly_zero_allowed(self):
        """min_overlap = 0.0 is valid (Requirement 8.7)."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]  # No overlap
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.0) == 1

    def test_min_overlap_exactly_one_allowed(self):
        """min_overlap = 1.0 is valid (Requirement 8.7)."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1

    def test_error_includes_values(self):
        """Error messages include relevant values."""
        with pytest.raises(EvaluationError) as exc_info:
            full_evidence_at_k([(0, 10)], [(0, 5)], k=-5, min_overlap=0.5)
        error = exc_info.value
        assert error.metric_name == "FullEvidence@K"
        assert error.values == {"k": -5}


class TestHitVsFullEvidenceComparison:
    """Tests comparing Hit@K and FullEvidence@K behavior."""

    def test_single_gold_span_same_result(self):
        """For single gold span, Hit@K and FullEvidence@K give same result."""
        gold = [(0, 10)]
        retrieved = [(0, 6)]  # 60% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

        retrieved_low = [(0, 3)]  # 30% overlap
        assert hit_at_k(gold, retrieved_low, k=1, min_overlap=0.5) == 0
        assert full_evidence_at_k(gold, retrieved_low, k=1, min_overlap=0.5) == 0

    def test_hit_easier_than_full_evidence(self):
        """Hit@K is easier to achieve than FullEvidence@K with multiple gold spans."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 10)]  # Only first span covered
        # Hit@K: ANY span meets threshold ✓
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1
        # FullEvidence@K: ALL spans must meet threshold ✗
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0

    def test_both_succeed_all_spans_covered(self):
        """Both metrics succeed when all spans are well covered."""
        gold = [(0, 10), (20, 30), (40, 50)]
        retrieved = [(0, 10), (20, 30), (40, 50)]
        assert hit_at_k(gold, retrieved, k=3, min_overlap=1.0) == 1
        assert full_evidence_at_k(gold, retrieved, k=3, min_overlap=1.0) == 1

    def test_both_fail_no_spans_covered(self):
        """Both metrics fail when no spans meet threshold."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(100, 110)]  # No overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 0


class TestEdgeCases:
    """Edge case tests for both metrics."""

    def test_large_offsets(self):
        """Large offset values work correctly."""
        gold = [(1000000, 1000010)]
        retrieved = [(1000000, 1000005)]  # 50% overlap
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1

    def test_single_character_spans(self):
        """Single character spans [i, i+1) work correctly."""
        gold = [(0, 1), (2, 3)]
        retrieved = [(0, 1)]  # First char covered
        assert hit_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=1.0) == 0

    def test_many_small_gold_spans(self):
        """Many small gold spans."""
        gold = [(i, i + 1) for i in range(0, 20, 2)]  # 10 single-char spans
        retrieved = [(0, 10)]  # Covers first 5 spans
        assert hit_at_k(gold, retrieved, k=1, min_overlap=1.0) == 1
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=1.0) == 0

    def test_overlapping_retrieved_spans(self):
        """Overlapping retrieved spans are unioned."""
        gold = [(0, 10)]
        retrieved = [(0, 7), (3, 10)]  # Union is [0, 10)
        assert hit_at_k(gold, retrieved, k=2, min_overlap=1.0) == 1
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=1.0) == 1

    def test_retrieved_beyond_gold_boundaries(self):
        """Retrieved spans extending beyond gold only count overlap."""
        gold = [(10, 20)]
        retrieved = [(0, 15), (15, 30)]  # Both extend beyond
        # Overlap is [10, 15) + [15, 20) = 10 chars = 100%
        assert hit_at_k(gold, retrieved, k=2, min_overlap=1.0) == 1
        assert full_evidence_at_k(gold, retrieved, k=2, min_overlap=1.0) == 1

    def test_boundary_precision(self):
        """Boundary cases for threshold comparison."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]  # Exactly 50% overlap
        # Exactly at threshold should succeed
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.5) == 1
        # Just above threshold should fail
        assert hit_at_k(gold, retrieved, k=1, min_overlap=0.50001) == 0
        assert full_evidence_at_k(gold, retrieved, k=1, min_overlap=0.50001) == 0
