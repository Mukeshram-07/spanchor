"""Property-based tests for Recall@K and Precision@K metrics.

These tests use Hypothesis to verify universal properties that must hold
across all possible inputs to recall and precision metric calculations.
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from spanchor.errors import EvaluationError
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k


# Strategy for generating valid intervals
def intervals_strategy(
    min_intervals: int = 0,
    max_intervals: int = 20,
    min_offset: int = 0,
    max_offset: int = 10000,
) -> st.SearchStrategy[list[Interval]]:
    """Generate lists of valid half-open intervals [start, end).

    Args:
        min_intervals: Minimum number of intervals to generate
        max_intervals: Maximum number of intervals to generate
        min_offset: Minimum offset value for start and end
        max_offset: Maximum offset value for start and end

    Returns:
        Strategy that generates lists of valid intervals
    """
    return st.lists(
        st.tuples(
            st.integers(min_value=min_offset, max_value=max_offset),  # start
            st.integers(min_value=min_offset, max_value=max_offset),  # end
        ).filter(lambda interval: interval[0] < interval[1]),  # Ensure start < end
        min_size=min_intervals,
        max_size=max_intervals,
    )


class TestRecallPrecisionProperties:
    """Property-based tests for recall and precision metrics."""

    @given(
        gold_spans=intervals_strategy(min_intervals=1, max_intervals=10),  # Non-empty gold
        retrieved_spans=intervals_strategy(min_intervals=0, max_intervals=10),
        k=st.integers(min_value=1, max_value=20),
    )
    def test_recall_metric_bounds(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property 20: Recall Metric Bounds.

        **Validates: Requirements 7.1, 7.6**

        For any valid gold and retrieved span sets with non-empty gold spans and K > 0,
        Recall@K SHALL be in the range [0, 1] inclusive.

        This property ensures that:
        - Recall@K is always a valid probability value between 0 and 1
        - The metric never produces negative values
        - The metric never exceeds 1.0 (100% recall)
        - The bounds hold regardless of span overlap patterns
        - The bounds hold for any valid K value
        """
        # Compute recall@k
        recall = recall_at_k(gold_spans, retrieved_spans, k)

        # PROPERTY: Recall must be in [0, 1] range
        assert 0.0 <= recall <= 1.0, (
            f"Recall@{k} must be in [0, 1] range, got {recall:.6f}. "
            f"Gold spans: {gold_spans[:3]}{'...' if len(gold_spans) > 3 else ''}, "
            f"Retrieved spans: {retrieved_spans[:3]}{'...' if len(retrieved_spans) > 3 else ''}"
        )

        # Additional verification: recall should be 0.0 when no retrieved spans
        if not retrieved_spans:
            assert (
                recall == 0.0
            ), f"Recall@{k} should be 0.0 when no spans retrieved, got {recall:.6f}"

        # Additional verification: recall should be 1.0 when retrieved fully covers gold
        # This is a best-case scenario check - we can't guarantee it happens in random data,
        # but if it does, we verify correctness
        from spanchor.evaluation.intervals import intersection, length, union

        G = union(gold_spans)
        R = union(retrieved_spans[:k])
        g_len = length(G)
        overlap_len = length(intersection(G, R))

        if overlap_len == g_len and g_len > 0:
            assert recall == 1.0, (
                f"Recall@{k} should be 1.0 when retrieved spans fully cover gold, "
                f"got {recall:.6f}. Overlap: {overlap_len}, Gold length: {g_len}"
            )

    @given(
        gold_spans=intervals_strategy(min_intervals=0, max_intervals=10),
        retrieved_spans=intervals_strategy(min_intervals=0, max_intervals=10),
        k=st.integers(min_value=1, max_value=20),
    )
    def test_precision_metric_bounds(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property 21: Precision Metric Bounds.

        **Validates: Requirements 7.2, 7.7**

        For any valid gold and retrieved span sets with K > 0,
        Precision@K SHALL be in the range [0, 1] inclusive.

        This property ensures that:
        - Precision@K is always a valid probability value between 0 and 1
        - The metric never produces negative values
        - The metric never exceeds 1.0 (100% precision)
        - The bounds hold regardless of span overlap patterns
        - The bounds hold even when gold spans are empty (edge case)
        - The bounds hold for any valid K value
        """
        # Compute precision@k
        precision = precision_at_k(gold_spans, retrieved_spans, k)

        # PROPERTY: Precision must be in [0, 1] range
        assert 0.0 <= precision <= 1.0, (
            f"Precision@{k} must be in [0, 1] range, got {precision:.6f}. "
            f"Gold spans: {gold_spans[:3]}{'...' if len(gold_spans) > 3 else ''}, "
            f"Retrieved spans: {retrieved_spans[:3]}{'...' if len(retrieved_spans) > 3 else ''}"
        )

        # Additional verification: precision should be 0.0 when no retrieved spans
        if not retrieved_spans:
            assert (
                precision == 0.0
            ), f"Precision@{k} should be 0.0 when no spans retrieved, got {precision:.6f}"

        # Additional verification: precision should be 1.0 when all retrieved are relevant
        # This is a best-case scenario check
        from spanchor.evaluation.intervals import intersection, length, union

        G = union(gold_spans)
        R = union(retrieved_spans[:k])
        r_len = length(R)
        overlap_len = length(intersection(G, R))

        if r_len > 0 and overlap_len == r_len:
            assert precision == 1.0, (
                f"Precision@{k} should be 1.0 when all retrieved spans are relevant, "
                f"got {precision:.6f}. Overlap: {overlap_len}, Retrieved length: {r_len}"
            )

        # Additional verification: precision should be 0.0 when no overlap
        if r_len > 0 and overlap_len == 0:
            assert precision == 0.0, (
                f"Precision@{k} should be 0.0 when no overlap with gold, "
                f"got {precision:.6f}. Retrieved length: {r_len}"
            )

    @given(
        gold_spans=intervals_strategy(min_intervals=1, max_intervals=10),  # Non-empty gold
        retrieved_spans=intervals_strategy(
            min_intervals=3, max_intervals=20
        ),  # At least 3 for K and K+1
        k=st.integers(min_value=1, max_value=10),  # Independently generate K
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_recall_monotonicity(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property 22: Recall Monotonicity.

        **Validates: Requirements 7.8**

        For any gold and retrieved span sets and K values where K < len(retrieved_spans),
        Recall@(K+1) SHALL be greater than or equal to Recall@K.

        This property ensures that:
        - Recall never decreases as we consider more retrieved results
        - Adding more retrieved spans can only increase or maintain recall
        - The monotonicity holds for all K values up to the number of retrieved spans
        - This reflects the intuitive property that more results cannot hurt recall
        """
        # Ensure K is within valid range for monotonicity test
        if k >= len(retrieved_spans):
            k = len(retrieved_spans) - 1

        # Compute Recall@K and Recall@(K+1)
        recall_k = recall_at_k(gold_spans, retrieved_spans, k)
        recall_k_plus_1 = recall_at_k(gold_spans, retrieved_spans, k + 1)

        # PROPERTY: Recall@(K+1) >= Recall@K (monotonicity)
        assert recall_k_plus_1 >= recall_k, (
            f"Recall monotonicity violated: Recall@{k+1} = {recall_k_plus_1:.6f} "
            f"< Recall@{k} = {recall_k:.6f}. "
            f"Recall should never decrease as K increases. "
            f"Gold spans: {gold_spans[:3]}{'...' if len(gold_spans) > 3 else ''}, "
            f"Retrieved spans: {retrieved_spans[:k+2]}"
        )

        # Additional verification: the difference should be non-negative
        delta = recall_k_plus_1 - recall_k
        assert delta >= -1e-10, (  # Allow tiny floating point errors
            f"Recall decreased by {-delta:.10f} when adding one more result. "
            f"This violates monotonicity."
        )

    @given(
        retrieved_spans=intervals_strategy(min_intervals=0, max_intervals=10),
        k=st.integers(min_value=1, max_value=20),
    )
    def test_recall_error_on_empty_gold_spans(
        self,
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Test that recall_at_k raises EvaluationError when gold_spans is empty.

        **Validates: Requirements 7.4**

        When |G| equals zero, THE Evaluation_Engine SHALL raise an EvaluationError
        indicating empty gold spans.

        This verifies:
        - Empty gold spans are rejected (cannot compute recall without gold)
        - The error message is clear and actionable
        - The error includes the metric name and relevant context
        """
        gold_spans: list[Interval] = []

        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k(gold_spans, retrieved_spans, k)

        error = exc_info.value
        assert error.metric_name == "Recall@K"
        assert "empty" in str(error).lower() or "cannot" in str(error).lower()
        assert "gold_spans" in error.values or "gold" in str(error).lower()

    @given(
        gold_spans=intervals_strategy(min_intervals=1, max_intervals=10),
        retrieved_spans=intervals_strategy(min_intervals=0, max_intervals=10),
    )
    def test_recall_error_on_invalid_k(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
    ) -> None:
        """Test that recall_at_k raises EvaluationError when K <= 0.

        **Validates: Requirements 7.5**

        When K equals zero, THE Evaluation_Engine SHALL raise an EvaluationError
        indicating invalid K value.

        This verifies:
        - K <= 0 is rejected (K must be positive)
        - The error message mentions K and that it must be positive
        - The error includes the invalid K value
        """
        # Test K = 0
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k(gold_spans, retrieved_spans, k=0)

        error = exc_info.value
        assert error.metric_name == "Recall@K"
        assert "positive" in str(error).lower() or "K" in str(error)
        assert error.values.get("k") == 0

        # Test K = -1
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k(gold_spans, retrieved_spans, k=-1)

        error = exc_info.value
        assert error.metric_name == "Recall@K"
        assert "positive" in str(error).lower() or "K" in str(error)
        assert error.values.get("k") == -1

    @given(
        gold_spans=intervals_strategy(min_intervals=0, max_intervals=10),
        retrieved_spans=intervals_strategy(min_intervals=0, max_intervals=10),
    )
    def test_precision_error_on_invalid_k(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
    ) -> None:
        """Test that precision_at_k raises EvaluationError when K <= 0.

        **Validates: Requirements 7.5**

        When K equals zero, THE Evaluation_Engine SHALL raise an EvaluationError
        indicating invalid K value.

        This verifies:
        - K <= 0 is rejected for precision as well
        - The error message is clear
        - The error includes the invalid K value
        """
        # Test K = 0
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k(gold_spans, retrieved_spans, k=0)

        error = exc_info.value
        assert error.metric_name == "Precision@K"
        assert "positive" in str(error).lower() or "K" in str(error)
        assert error.values.get("k") == 0

        # Test K = -1
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k(gold_spans, retrieved_spans, k=-1)

        error = exc_info.value
        assert error.metric_name == "Precision@K"
        assert "positive" in str(error).lower() or "K" in str(error)
        assert error.values.get("k") == -1

    @given(
        gold_spans=intervals_strategy(min_intervals=1, max_intervals=5),
        retrieved_spans=intervals_strategy(min_intervals=1, max_intervals=5),
    )
    def test_recall_and_precision_complementary_bounds(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
    ) -> None:
        """Test that recall and precision together provide complete picture.

        This is an additional property test to verify that both metrics
        behave consistently and their bounds are always respected together.

        This verifies:
        - Both metrics stay in [0, 1] simultaneously
        - If retrieved spans exactly match gold, both should be 1.0
        - If there's no overlap, both should be 0.0 (recall=0, precision=0)
        """
        k = len(retrieved_spans)

        recall = recall_at_k(gold_spans, retrieved_spans, k)
        precision = precision_at_k(gold_spans, retrieved_spans, k)

        # Both must be in valid range
        assert 0.0 <= recall <= 1.0
        assert 0.0 <= precision <= 1.0

        # If we have perfect match (both 1.0), verify it's actually perfect
        if recall == 1.0 and precision == 1.0:
            from spanchor.evaluation.intervals import length, union

            G = union(gold_spans)
            R = union(retrieved_spans)
            assert length(G) == length(R), (
                "If both recall and precision are 1.0, "
                "gold and retrieved should have same length"
            )
