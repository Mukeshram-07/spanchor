"""Recall@K metric computation for character-level span coverage.

This module provides character-level recall calculation comparing retrieved spans
against gold standard spans using interval algebra.
"""

from spanchor.errors import EvaluationError
from spanchor.evaluation.intervals import Interval, intersection, length, union


def recall_at_k(
    gold_spans: list[Interval],
    retrieved_spans: list[Interval],
    k: int,
) -> float:
    """Calculate character-level Recall@K.

    Recall@K measures what fraction of gold evidence characters are covered
    by the top-K retrieved spans: |G ∩ R| / |G|

    Args:
        gold_spans: List of gold evidence intervals [start, end)
        retrieved_spans: List of retrieved intervals [start, end), ranked by retriever
        k: Number of top-ranked results to consider (must be positive)

    Returns:
        Recall value in range [0.0, 1.0]

    Raises:
        EvaluationError: If K <= 0 or gold_spans is empty

    Examples:
        >>> recall_at_k([(0, 10)], [(0, 5)], k=1)
        0.5
        >>> recall_at_k([(0, 10)], [(0, 10)], k=1)
        1.0
        >>> recall_at_k([(0, 10), (20, 30)], [(0, 10)], k=1)
        0.5
    """
    # Validate K (Requirement 7.5)
    if k <= 0:
        raise EvaluationError(
            message="K must be positive",
            metric_name="Recall@K",
            values={"k": k},
        )

    # Compute union of gold spans
    G = union(gold_spans)
    g_len = length(G)

    # Validate non-empty gold spans (Requirement 7.4)
    if g_len == 0:
        raise EvaluationError(
            message="Gold spans cannot be empty",
            metric_name="Recall@K",
            values={"gold_spans": gold_spans},
        )

    # Compute union of top-K retrieved spans (Requirement 7.1)
    R = union(retrieved_spans[:k])

    # Calculate overlap
    overlap_intervals = intersection(G, R)
    overlap_length = length(overlap_intervals)

    # Return recall (Requirement 7.6: ensures result in [0, 1])
    return overlap_length / g_len
