"""Precision@K metric computation for character-level span coverage.

This module provides character-level precision calculation comparing retrieved spans
against gold standard spans using interval algebra.
"""

from spanchor.errors import EvaluationError
from spanchor.evaluation.intervals import Interval, intersection, length, union


def precision_at_k(
    gold_spans: list[Interval],
    retrieved_spans: list[Interval],
    k: int,
) -> float:
    """Calculate character-level Precision@K.

    Precision@K measures what fraction of retrieved characters are relevant
    (overlap with gold evidence): |G ∩ R| / |R|

    Args:
        gold_spans: List of gold evidence intervals [start, end)
        retrieved_spans: List of retrieved intervals [start, end), ranked by retriever
        k: Number of top-ranked results to consider (must be positive)

    Returns:
        Precision value in range [0.0, 1.0]

    Raises:
        EvaluationError: If K <= 0

    Examples:
        >>> precision_at_k([(0, 10)], [(0, 5)], k=1)
        1.0
        >>> precision_at_k([(0, 10)], [(0, 15)], k=1)
        0.666...
        >>> precision_at_k([(0, 10)], [], k=1)
        0.0
    """
    # Validate K (Requirement 7.5)
    if k <= 0:
        raise EvaluationError(
            message="K must be positive",
            metric_name="Precision@K",
            values={"k": k},
        )

    # Compute union of gold spans
    G = union(gold_spans)

    # Compute union of top-K retrieved spans (Requirement 7.2)
    R = union(retrieved_spans[:k])
    r_len = length(R)

    # Handle empty retrieved set (Requirement 7.3)
    if r_len == 0:
        return 0.0

    # Calculate overlap
    overlap_intervals = intersection(G, R)
    overlap_length = length(overlap_intervals)

    # Return precision (Requirement 7.7: ensures result in [0, 1])
    return overlap_length / r_len
