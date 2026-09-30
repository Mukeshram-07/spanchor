"""Property-based tests for evaluation metrics.

These tests use Hypothesis to verify universal properties that must hold
across all possible metric inputs.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from spanchor.errors import EvaluationError
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k


# Strategy for generating valid intervals
def intervals_strategy(
    min_size: int = 0, max_size: int = 20, allow_empty: bool = True
) -> st.SearchStrategy[list[Interval]]:
    """Generate lists of valid intervals [start, end) where start <= end.

    Args:
        min_size: Minimum number of intervals in the list
        max_size: Maximum number of intervals in the list
        allow_empty: Whether to allow zero-length intervals [x, x)

    Returns:
        Strategy for generating lists of intervals
    """
    # Generate individual intervals
    if allow_empty:
        # Allow zero-length intervals
        interval = st.builds(
            lambda start, length: (start, start + length),
            start=st.integers(min_value=0, max_value=10000),
            length=st.integers(min_value=0, max_value=1000),
        )
    else:
        # Require at least 1 character
        interval = st.builds(
            lambda start, length: (start, start + length),
            start=st.integers(min_value=0, max_value=10000),
            length=st.integers(min_value=1, max_value=1000),
        )

    # Generate lists of intervals
    return st.lists(interval, min_size=min_size, max_size=max_size)


class TestMetricProperties:
    """Property-based tests for evaluation metrics."""

    @given(
        gold_spans=intervals_strategy(min_size=1, allow_empty=False),  # Non-empty gold spans
        retrieved_spans=intervals_strategy(min_size=0, allow_empty=True),  # Any retrieved spans
        k=st.integers(min_value=1, max_value=100),  # K > 0
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

        This property verifies:
        - Recall@K always returns a value in [0.0, 1.0]
        - The bound holds for any combination of gold/retrieved spans
        - The bound holds for any valid K value
        - No edge case produces out-of-bounds recall values
        """
        # Compute recall
        recall = recall_at_k(gold_spans, retrieved_spans, k)

        # PROPERTY: Recall@K must be in the range [0.0, 1.0] inclusive
        assert 0.0 <= recall <= 1.0, (
            f"Recall@K is out of bounds [0, 1]:\n"
            f"Gold spans: {gold_spans}\n"
            f"Retrieved spans: {retrieved_spans}\n"
            f"K: {k}\n"
            f"Computed Recall@{k}: {recall}\n"
            f"Expected 0.0 <= recall <= 1.0"
        )

        # Additional verification: recall should be a float
        assert isinstance(recall, float), (
            f"Recall@K should return a float:\n" f"Type: {type(recall)}\n" f"Value: {recall}"
        )

        # Additional verification: perfect recall (1.0) only when all gold is covered
        # This is a sanity check that the metric behaves correctly at the boundary
        if recall == 1.0:
            # When recall is 1.0, all gold characters must be covered
            # This is a logical consequence of the metric definition
            # We don't verify this explicitly here (that's the unit test's job),
            # but we document the expectation
            pass

        # Additional verification: zero recall (0.0) when no gold is covered
        if recall == 0.0:
            # When recall is 0.0, either:
            # - Retrieved spans are empty, OR
            # - Retrieved spans don't overlap with gold at all
            # Again, this is a logical consequence we document
            pass

    @given(
        gold_spans=intervals_strategy(min_size=0, allow_empty=True),  # Any gold spans
        retrieved_spans=intervals_strategy(min_size=0, allow_empty=True),  # Any retrieved spans
        k=st.integers(min_value=1, max_value=100),  # K > 0
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

        This property verifies:
        - Precision@K always returns a value in [0.0, 1.0]
        - The bound holds for any combination of gold/retrieved spans
        - The bound holds for any valid K value
        - Empty gold spans don't cause out-of-bounds values
        - No edge case produces out-of-bounds precision values
        """
        # Compute precision
        precision = precision_at_k(gold_spans, retrieved_spans, k)

        # PROPERTY: Precision@K must be in the range [0.0, 1.0] inclusive
        assert 0.0 <= precision <= 1.0, (
            f"Precision@K is out of bounds [0, 1]:\n"
            f"Gold spans: {gold_spans}\n"
            f"Retrieved spans: {retrieved_spans}\n"
            f"K: {k}\n"
            f"Computed Precision@{k}: {precision}\n"
            f"Expected 0.0 <= precision <= 1.0"
        )

        # Additional verification: precision should be a float
        assert isinstance(precision, float), (
            f"Precision@K should return a float:\n"
            f"Type: {type(precision)}\n"
            f"Value: {precision}"
        )

        # Additional verification: perfect precision (1.0) only when all
        # retrieved is relevant. This is a sanity check that the metric
        # behaves correctly at the boundary
        if precision == 1.0:
            # When precision is 1.0, either:
            # - All retrieved characters overlap with gold, OR
            # - Retrieved spans are empty (0.0 is returned by the
            #   implementation for empty retrieved)
            # Actually, the implementation returns 0.0 for empty retrieved,
            # so precision == 1.0 means all retrieved characters are relevant
            pass

        # Additional verification: zero precision (0.0) when no retrieved
        # is relevant or retrieved is empty
        if precision == 0.0:
            # When precision is 0.0, either:
            # - Retrieved spans are empty, OR
            # - Retrieved spans don't overlap with gold at all
            pass

    @given(
        gold_spans=st.just([]),  # Empty gold spans
        retrieved_spans=intervals_strategy(min_size=0, allow_empty=True),
        k=st.integers(min_value=1, max_value=100),
    )
    def test_recall_rejects_empty_gold_spans(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property: Recall@K rejects empty gold spans.

        **Validates: Requirements 7.4**

        For any retrieved span set and K > 0, if gold_spans is empty,
        recall_at_k SHALL raise EvaluationError.

        This property verifies:
        - Empty gold spans are detected and rejected
        - The error type is EvaluationError
        - The error message identifies the problem
        """
        # PROPERTY: Empty gold spans must raise EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k(gold_spans, retrieved_spans, k)

        # Verify the error message mentions empty gold spans
        error = exc_info.value
        error_msg = str(error)
        assert "gold" in error_msg.lower() and (
            "empty" in error_msg.lower() or "cannot be empty" in error_msg.lower()
        ), f"Error message should mention empty gold spans:\n" f"Error message: {error_msg}"

        # Verify the metric name is included
        assert error.metric_name == "Recall@K", (
            f"Error metric_name should be 'Recall@K':\n" f"Got: {error.metric_name}"
        )

    @given(
        gold_spans=intervals_strategy(min_size=1, allow_empty=False),
        retrieved_spans=intervals_strategy(min_size=0, allow_empty=True),
        k=st.integers(max_value=0),  # K <= 0
    )
    def test_recall_rejects_invalid_k(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property: Recall@K rejects K <= 0.

        **Validates: Requirements 7.5**

        For any valid span sets, if K <= 0, recall_at_k SHALL raise EvaluationError.

        This property verifies:
        - K <= 0 is detected and rejected
        - The error type is EvaluationError
        - The error message identifies the invalid K value
        """
        # PROPERTY: K <= 0 must raise EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            recall_at_k(gold_spans, retrieved_spans, k)

        # Verify the error message mentions K validation
        error = exc_info.value
        error_msg = str(error)
        assert "K" in error_msg or "k" in error_msg, (
            f"Error message should mention K:\n" f"Error message: {error_msg}"
        )

        assert "positive" in error_msg.lower(), (
            f"Error message should mention K must be positive:\n" f"Error message: {error_msg}"
        )

        # Verify the metric name is included
        assert error.metric_name == "Recall@K", (
            f"Error metric_name should be 'Recall@K':\n" f"Got: {error.metric_name}"
        )

        # Verify the invalid K value is included in the error
        assert error.values.get("k") == k, (
            f"Error should include the invalid K value:\n"
            f"Expected: {k}\n"
            f"Got: {error.values.get('k')}"
        )

    @given(
        gold_spans=intervals_strategy(min_size=0, allow_empty=True),
        retrieved_spans=intervals_strategy(min_size=0, allow_empty=True),
        k=st.integers(max_value=0),  # K <= 0
    )
    def test_precision_rejects_invalid_k(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
        k: int,
    ) -> None:
        """Property: Precision@K rejects K <= 0.

        **Validates: Requirements 7.5**

        For any valid span sets, if K <= 0, precision_at_k SHALL raise EvaluationError.

        This property verifies:
        - K <= 0 is detected and rejected
        - The error type is EvaluationError
        - The error message identifies the invalid K value
        """
        # PROPERTY: K <= 0 must raise EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            precision_at_k(gold_spans, retrieved_spans, k)

        # Verify the error message mentions K validation
        error = exc_info.value
        error_msg = str(error)
        assert "K" in error_msg or "k" in error_msg, (
            f"Error message should mention K:\n" f"Error message: {error_msg}"
        )

        assert "positive" in error_msg.lower(), (
            f"Error message should mention K must be positive:\n" f"Error message: {error_msg}"
        )

        # Verify the metric name is included
        assert error.metric_name == "Precision@K", (
            f"Error metric_name should be 'Precision@K':\n" f"Got: {error.metric_name}"
        )

        # Verify the invalid K value is included in the error
        assert error.values.get("k") == k, (
            f"Error should include the invalid K value:\n"
            f"Expected: {k}\n"
            f"Got: {error.values.get('k')}"
        )
