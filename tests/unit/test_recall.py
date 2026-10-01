"""Unit tests for Recall@K metric."""

import pytest

from spanchor.errors import EvaluationError
from spanchor.evaluation.recall import recall_at_k


class TestRecallAtK:
    """Tests for recall_at_k function."""

    def test_perfect_recall(self):
        """Perfect recall when retrieved fully covers gold."""
        gold = [(0, 10)]
        retrieved = [(0, 10)]
        assert recall_at_k(gold, retrieved, k=1) == 1.0

    def test_partial_recall(self):
        """Partial recall when retrieved covers half of gold."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]
        assert recall_at_k(gold, retrieved, k=1) == 0.5

    def test_zero_recall(self):
        """Zero recall when retrieved doesn't overlap gold."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        assert recall_at_k(gold, retrieved, k=1) == 0.0

    def test_multiple_gold_spans(self):
        """Recall with multiple gold spans (Requirement 7.1)."""
        gold = [(0, 10), (20, 30)]  # 20 characters total
        retrieved = [(0, 10)]  # Covers only first span
        assert recall_at_k(gold, retrieved, k=1) == 0.5

    def test_multiple_retrieved_spans(self):
        """Recall with multiple retrieved spans."""
        gold = [(0, 20)]
        retrieved = [(0, 5), (10, 15)]  # 10 characters covered
        assert recall_at_k(gold, retrieved, k=2) == 0.5

    def test_overlapping_gold_spans(self):
        """Overlapping gold spans are unioned before calculation."""
        gold = [(0, 10), (5, 15)]  # Union is [0, 15) = 15 chars
        retrieved = [(0, 15)]
        assert recall_at_k(gold, retrieved, k=1) == 1.0

    def test_overlapping_retrieved_spans(self):
        """Overlapping retrieved spans are unioned before calculation."""
        gold = [(0, 20)]
        retrieved = [(0, 10), (5, 15)]  # Union is [0, 15) = 15 chars
        assert recall_at_k(gold, retrieved, k=2) == 0.75

    def test_k_limits_retrieved_spans(self):
        """Only top-K retrieved spans are used (Requirement 7.1)."""
        gold = [(0, 20)]
        retrieved = [(0, 10), (10, 20), (20, 30)]
        # k=1: only first span [0, 10)
        assert recall_at_k(gold, retrieved, k=1) == 0.5
        # k=2: first two spans [0, 20)
        assert recall_at_k(gold, retrieved, k=2) == 1.0

    def test_k_greater_than_retrieved_count(self):
        """K greater than retrieved count uses all spans."""
        gold = [(0, 20)]
        retrieved = [(0, 10)]
        assert recall_at_k(gold, retrieved, k=100) == 0.5

    def test_empty_retrieved_spans(self):
        """Empty retrieved spans gives zero recall."""
        gold = [(0, 10)]
        retrieved = []
        assert recall_at_k(gold, retrieved, k=1) == 0.0

    def test_adjacent_spans(self):
        """Adjacent spans are merged correctly."""
        gold = [(0, 10)]
        retrieved = [(0, 5), (5, 10)]  # Adjacent, merge to [0, 10)
        assert recall_at_k(gold, retrieved, k=2) == 1.0

    def test_partial_overlap_multiple_spans(self):
        """Partial overlaps across multiple spans."""
        gold = [(0, 10), (20, 30), (40, 50)]  # 30 chars total
        retrieved = [(0, 5), (22, 28), (45, 50)]  # 5+6+5 = 16 chars covered
        result = recall_at_k(gold, retrieved, k=3)
        assert result == pytest.approx(16 / 30)

    def test_retrieved_beyond_gold(self):
        """Retrieved spans extending beyond gold only count overlap."""
        gold = [(0, 10)]
        retrieved = [(0, 20)]  # Extends beyond gold
        assert recall_at_k(gold, retrieved, k=1) == 1.0

    def test_recall_in_range(self):
        """Recall is always in [0, 1] range (Requirement 7.6)."""
        test_cases = [
            ([(0, 10)], [(0, 10)], 1),  # Perfect recall
            ([(0, 10)], [(0, 5)], 1),  # Partial recall
            ([(0, 10)], [], 1),  # Zero recall
            ([(0, 10)], [(5, 15)], 1),  # Partial overlap
        ]
        for gold, retrieved, k in test_cases:
            result = recall_at_k(gold, retrieved, k)
            assert 0.0 <= result <= 1.0


class TestRecallAtKErrors:
    """Tests for recall_at_k error conditions."""

    def test_empty_gold_spans_raises_error(self):
        """Empty gold spans raises EvaluationError (Requirement 7.4)."""
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k([], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)
        assert "Recall@K" in str(exc_info.value)

    def test_zero_length_gold_spans_raises_error(self):
        """Zero-length gold spans raise EvaluationError."""
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k([(5, 5)], [(0, 10)], k=1)
        assert "Gold spans cannot be empty" in str(exc_info.value)

    def test_k_zero_raises_error(self):
        """K = 0 raises EvaluationError (Requirement 7.5)."""
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k([(0, 10)], [(0, 5)], k=0)
        assert "K must be positive" in str(exc_info.value)
        assert "Recall@K" in str(exc_info.value)

    def test_k_negative_raises_error(self):
        """Negative K raises EvaluationError (Requirement 7.5)."""
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k([(0, 10)], [(0, 5)], k=-1)
        assert "K must be positive" in str(exc_info.value)

    def test_error_includes_values(self):
        """Error messages include relevant values."""
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k([(0, 10)], [(0, 5)], k=0)
        error = exc_info.value
        assert error.metric_name == "Recall@K"
        assert error.values == {"k": 0}


class TestRecallEdgeCases:
    """Edge case tests for recall_at_k."""

    def test_large_offsets(self):
        """Large offset values work correctly."""
        gold = [(1000000, 1000010)]
        retrieved = [(1000000, 1000005)]
        assert recall_at_k(gold, retrieved, k=1) == 0.5

    def test_single_character_spans(self):
        """Single character spans [i, i+1) work correctly."""
        gold = [(0, 1), (2, 3), (4, 5)]  # 3 chars
        retrieved = [(0, 1), (4, 5)]  # 2 chars covered
        result = recall_at_k(gold, retrieved, k=2)
        assert result == pytest.approx(2 / 3)

    def test_many_small_spans(self):
        """Many small overlapping spans."""
        gold = [(0, 100)]
        # 10 overlapping spans that together cover [0, 55)
        retrieved = [(i, i + 10) for i in range(0, 50, 5)]
        assert recall_at_k(gold, retrieved, k=10) == 0.55

    def test_disjoint_retrieved_spans(self):
        """Multiple disjoint retrieved spans."""
        gold = [(0, 100)]
        retrieved = [(10, 20), (30, 40), (50, 60)]  # 30 chars covered
        assert recall_at_k(gold, retrieved, k=3) == 0.3

    def test_complex_overlap_scenario(self):
        """Complex scenario with multiple overlaps and gaps."""
        gold = [(0, 20), (30, 50), (60, 80)]  # 60 chars total
        retrieved = [(5, 15), (35, 45), (70, 90)]  # Partial overlaps
        # Overlaps: [5,15)=10, [35,45)=10, [70,80)=10 = 30 chars
        assert recall_at_k(gold, retrieved, k=3) == 0.5


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Helpers / strategies
# ---------------------------------------------------------------------------

# Strategy for a single valid half-open interval [start, end) with end > start.
_interval_st = st.integers(min_value=0, max_value=10_000).flatmap(
    lambda start: st.integers(min_value=start + 1, max_value=start + 1_000).map(
        lambda end: (start, end)
    )
)


class TestRecallMonotonicityProperty:
    """Property-based tests for Recall@K monotonicity (Requirement 7.8)."""

    @settings(max_examples=200)
    @given(
        gold_spans=st.lists(_interval_st, min_size=1, max_size=10),
        retrieved_spans=st.lists(_interval_st, min_size=2, max_size=20),
        k=st.integers(min_value=1),
    )
    def test_recall_monotonicity(
        self,
        gold_spans: list[tuple[int, int]],
        retrieved_spans: list[tuple[int, int]],
        k: int,
    ) -> None:
        """Property 22: Recall Monotonicity.

        **Validates: Requirements 7.8**

        For any gold and retrieved span sets, and any K where K < len(retrieved_spans),
        Recall@(K+1) SHALL be greater than or equal to Recall@K.

        Adding more retrieved spans can only keep recall the same or improve it —
        it can never decrease, because the top-(K+1) set is a superset of the top-K set.
        """
        # Only test when K < len(retrieved_spans) so that K+1 is still a meaningful
        # step (i.e., we actually add one more span to the consideration set).
        if k >= len(retrieved_spans):
            return

        recall_k = recall_at_k(gold_spans, retrieved_spans, k)
        recall_k1 = recall_at_k(gold_spans, retrieved_spans, k + 1)

        assert recall_k1 >= recall_k, (
            f"Monotonicity violated: Recall@{k + 1}={recall_k1} < Recall@{k}={recall_k}\n"
            f"gold_spans={gold_spans}\n"
            f"retrieved_spans={retrieved_spans}"
        )
