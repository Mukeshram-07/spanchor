"""Unit tests for Precision@K metric."""

import pytest

from spanchor.errors import EvaluationError
from spanchor.evaluation.precision import precision_at_k


class TestPrecisionAtK:
    """Tests for precision_at_k function."""

    def test_perfect_precision(self):
        """Perfect precision when all retrieved is relevant."""
        gold = [(0, 10)]
        retrieved = [(0, 5)]  # All 5 chars are relevant
        assert precision_at_k(gold, retrieved, k=1) == 1.0

    def test_partial_precision(self):
        """Partial precision when some retrieved is irrelevant."""
        gold = [(0, 10)]
        retrieved = [(0, 15)]  # 10 relevant, 5 irrelevant
        result = precision_at_k(gold, retrieved, k=1)
        assert result == pytest.approx(10 / 15)

    def test_zero_precision(self):
        """Zero precision when retrieved doesn't overlap gold."""
        gold = [(0, 10)]
        retrieved = [(20, 30)]
        assert precision_at_k(gold, retrieved, k=1) == 0.0

    def test_empty_retrieved_returns_zero(self):
        """Empty retrieved spans returns 0.0 (Requirement 7.3)."""
        gold = [(0, 10)]
        retrieved = []
        assert precision_at_k(gold, retrieved, k=1) == 0.0

    def test_zero_length_retrieved_returns_zero(self):
        """Zero-length retrieved spans returns 0.0."""
        gold = [(0, 10)]
        retrieved = [(5, 5)]
        assert precision_at_k(gold, retrieved, k=1) == 0.0

    def test_multiple_gold_spans(self):
        """Precision with multiple gold spans (Requirement 7.2)."""
        gold = [(0, 10), (20, 30)]
        retrieved = [(0, 15)]  # 10 relevant, 5 irrelevant
        result = precision_at_k(gold, retrieved, k=1)
        assert result == pytest.approx(10 / 15)

    def test_multiple_retrieved_spans(self):
        """Precision with multiple retrieved spans."""
        gold = [(0, 10)]
        retrieved = [(0, 5), (10, 15)]  # 5 relevant, 5 irrelevant
        assert precision_at_k(gold, retrieved, k=2) == 0.5

    def test_overlapping_gold_spans(self):
        """Overlapping gold spans are unioned before calculation."""
        gold = [(0, 10), (5, 15)]  # Union is [0, 15)
        retrieved = [(0, 20)]  # 15 relevant, 5 irrelevant
        result = precision_at_k(gold, retrieved, k=1)
        assert result == pytest.approx(15 / 20)

    def test_overlapping_retrieved_spans(self):
        """Overlapping retrieved spans are unioned before calculation."""
        gold = [(0, 10)]
        retrieved = [(0, 15), (10, 20)]  # Union is [0, 20) = 20 chars
        # Overlap with gold is [0, 10) = 10 chars
        assert precision_at_k(gold, retrieved, k=2) == 0.5

    def test_k_limits_retrieved_spans(self):
        """Only top-K retrieved spans are used (Requirement 7.2)."""
        gold = [(0, 30)]
        retrieved = [(0, 10), (10, 20), (20, 40)]
        # k=1: only [0, 10), all relevant
        assert precision_at_k(gold, retrieved, k=1) == 1.0
        # k=2: [0, 20), all relevant
        assert precision_at_k(gold, retrieved, k=2) == 1.0
        # k=3: [0, 40), 30 relevant, 10 irrelevant
        assert precision_at_k(gold, retrieved, k=3) == 0.75

    def test_k_greater_than_retrieved_count(self):
        """K greater than retrieved count uses all spans."""
        gold = [(0, 10)]
        retrieved = [(0, 15)]
        result = precision_at_k(gold, retrieved, k=100)
        assert result == pytest.approx(10 / 15)

    def test_adjacent_spans(self):
        """Adjacent spans are merged correctly."""
        gold = [(0, 10)]
        retrieved = [(0, 5), (5, 15)]  # Adjacent, merge to [0, 15)
        # 10 relevant, 5 irrelevant
        result = precision_at_k(gold, retrieved, k=2)
        assert result == pytest.approx(10 / 15)

    def test_partial_overlap_multiple_spans(self):
        """Partial overlaps across multiple spans."""
        gold = [(0, 10), (20, 30)]  # 20 chars gold
        retrieved = [(0, 5), (5, 15), (25, 35)]  # Union: [0,15), [25,35) = 25 chars
        # Overlaps: [0,10)=10, [25,30)=5 = 15 relevant
        result = precision_at_k(gold, retrieved, k=3)
        assert result == pytest.approx(15 / 25)

    def test_all_retrieved_irrelevant(self):
        """All retrieved spans are completely irrelevant."""
        gold = [(0, 10)]
        retrieved = [(20, 30), (40, 50)]
        assert precision_at_k(gold, retrieved, k=2) == 0.0

    def test_precision_in_range(self):
        """Precision is always in [0, 1] range (Requirement 7.7)."""
        test_cases = [
            ([(0, 10)], [(0, 10)], 1),  # Perfect precision
            ([(0, 10)], [(0, 15)], 1),  # Partial precision
            ([(0, 10)], [], 1),  # Empty retrieved
            ([(0, 10)], [(20, 30)], 1),  # Zero precision
        ]
        for gold, retrieved, k in test_cases:
            result = precision_at_k(gold, retrieved, k)
            assert 0.0 <= result <= 1.0

    def test_empty_gold_spans(self):
        """Empty gold spans results in zero precision."""
        gold = []
        retrieved = [(0, 10)]
        assert precision_at_k(gold, retrieved, k=1) == 0.0

    def test_zero_length_gold_spans(self):
        """Zero-length gold spans result in zero precision."""
        gold = [(5, 5)]
        retrieved = [(0, 10)]
        assert precision_at_k(gold, retrieved, k=1) == 0.0


class TestPrecisionAtKErrors:
    """Tests for precision_at_k error conditions."""

    def test_k_zero_raises_error(self):
        """K = 0 raises EvaluationError (Requirement 7.5)."""
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k([(0, 10)], [(0, 5)], k=0)
        assert "K must be positive" in str(exc_info.value)
        assert "Precision@K" in str(exc_info.value)

    def test_k_negative_raises_error(self):
        """Negative K raises EvaluationError (Requirement 7.5)."""
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k([(0, 10)], [(0, 5)], k=-1)
        assert "K must be positive" in str(exc_info.value)

    def test_error_includes_values(self):
        """Error messages include relevant values."""
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k([(0, 10)], [(0, 5)], k=0)
        error = exc_info.value
        assert error.metric_name == "Precision@K"
        assert error.values == {"k": 0}


class TestPrecisionEdgeCases:
    """Edge case tests for precision_at_k."""

    def test_large_offsets(self):
        """Large offset values work correctly."""
        gold = [(1000000, 1000010)]
        retrieved = [(1000000, 1000015)]
        result = precision_at_k(gold, retrieved, k=1)
        assert result == pytest.approx(10 / 15)

    def test_single_character_spans(self):
        """Single character spans [i, i+1) work correctly."""
        gold = [(0, 1), (2, 3), (4, 5)]  # 3 chars
        retrieved = [(0, 1), (1, 2), (4, 5)]  # 3 chars, 2 relevant
        result = precision_at_k(gold, retrieved, k=3)
        assert result == pytest.approx(2 / 3)

    def test_many_small_spans(self):
        """Many small overlapping spans."""
        gold = [(0, 50)]
        # 10 overlapping spans covering [0, 110)
        retrieved = [(i, i + 20) for i in range(0, 100, 10)]
        result = precision_at_k(gold, retrieved, k=10)
        # Union of retrieved is [0, 110) = 110 chars
        # Overlap with gold is [0, 50) = 50 chars
        assert result == pytest.approx(50 / 110)

    def test_disjoint_retrieved_spans(self):
        """Multiple disjoint retrieved spans."""
        gold = [(10, 30)]  # 20 chars
        retrieved = [(0, 10), (20, 30), (40, 50)]  # 30 chars, 10 relevant
        result = precision_at_k(gold, retrieved, k=3)
        assert result == pytest.approx(10 / 30)

    def test_complex_overlap_scenario(self):
        """Complex scenario with multiple overlaps and gaps."""
        gold = [(0, 20), (40, 60)]  # 40 chars
        retrieved = [(10, 30), (50, 70)]  # [10,30) and [50,70) = 40 chars
        # Overlaps: [10,20)=10, [50,60)=10 = 20 relevant
        assert precision_at_k(gold, retrieved, k=2) == 0.5
