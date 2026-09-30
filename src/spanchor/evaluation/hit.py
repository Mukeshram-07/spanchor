"""Hit@K and FullEvidence@K metrics for binary success evaluation.

This module provides binary success metrics that evaluate whether retrieved
spans meet minimum overlap thresholds with gold evidence spans.
"""

from spanchor.errors import EvaluationError
from spanchor.evaluation.intervals import Interval, intersection, length, union


def hit_at_k(
    gold_spans: list[Interval],
    retrieved_spans: list[Interval],
    k: int,
    min_overlap: float = 0.5,
) -> int:
    """Calculate Hit@K metric.

    Hit@K returns 1 if ANY gold span has at least min_overlap fraction
    of its characters covered by the top-K retrieved spans, else 0.

    For each gold span, computes: |gold_span ∩ R| / |gold_span|
    Returns 1 if any ratio >= min_overlap, else 0.

    Args:
        gold_spans: List of gold evidence intervals [start, end)
        retrieved_spans: List of retrieved intervals [start, end), ranked by retriever
        k: Number of top-ranked results to consider (must be positive)
        min_overlap: Minimum overlap fraction threshold (must be in [0, 1])

    Returns:
        1 if any gold span meets threshold, 0 otherwise

    Raises:
        EvaluationError: If K <= 0, gold_spans is empty, or min_overlap not in [0, 1]

    Examples:
        >>> hit_at_k([(0, 10)], [(0, 5)], k=1, min_overlap=0.5)
        1
        >>> hit_at_k([(0, 10)], [(0, 4)], k=1, min_overlap=0.5)
        0
        >>> hit_at_k([(0, 10), (20, 30)], [(0, 5)], k=1, min_overlap=0.5)
        1
    """
    # Validate K
    if k <= 0:
        raise EvaluationError(
            message="K must be positive",
            metric_name="Hit@K",
            values={"k": k},
        )

    # Validate min_overlap (Requirement 8.7)
    if not (0.0 <= min_overlap <= 1.0):
        raise EvaluationError(
            message="min_overlap must be between 0 and 1",
            metric_name="Hit@K",
            values={"min_overlap": min_overlap},
        )

    # Validate non-empty gold spans
    G = union(gold_spans)
    if length(G) == 0:
        raise EvaluationError(
            message="Gold spans cannot be empty",
            metric_name="Hit@K",
            values={"gold_spans": gold_spans},
        )

    # Compute union of top-K retrieved spans
    R = union(retrieved_spans[:k])

    # Check each gold span for minimum overlap (Requirements 8.1, 8.2)
    for gold_span in G:
        # Compute overlap fraction for this gold span
        overlap_intervals = intersection([gold_span], R)
        overlap_len = length(overlap_intervals)
        gold_len = gold_span[1] - gold_span[0]

        overlap_fraction = overlap_len / gold_len if gold_len > 0 else 0.0

        # If any gold span meets threshold, return 1 (Requirement 8.1)
        if overlap_fraction >= min_overlap:
            return 1

    # No gold span met threshold, return 0 (Requirement 8.2)
    return 0


def full_evidence_at_k(
    gold_spans: list[Interval],
    retrieved_spans: list[Interval],
    k: int,
    min_overlap: float = 0.5,
) -> int:
    """Calculate FullEvidence@K metric.

    FullEvidence@K returns 1 if ALL gold spans have at least min_overlap
    fraction of their characters covered by the top-K retrieved spans, else 0.

    For each gold span, computes: |gold_span ∩ R| / |gold_span|
    Returns 1 if all ratios >= min_overlap, else 0.

    Args:
        gold_spans: List of gold evidence intervals [start, end)
        retrieved_spans: List of retrieved intervals [start, end), ranked by retriever
        k: Number of top-ranked results to consider (must be positive)
        min_overlap: Minimum overlap fraction threshold (must be in [0, 1])

    Returns:
        1 if all gold spans meet threshold, 0 otherwise

    Raises:
        EvaluationError: If K <= 0, gold_spans is empty, or min_overlap not in [0, 1]

    Examples:
        >>> full_evidence_at_k([(0, 10)], [(0, 10)], k=1, min_overlap=0.5)
        1
        >>> full_evidence_at_k([(0, 10), (20, 30)], [(0, 10)], k=1, min_overlap=0.5)
        0
        >>> full_evidence_at_k([(0, 10), (20, 30)], [(0, 10), (20, 30)], k=2, min_overlap=1.0)
        1
    """
    # Validate K
    if k <= 0:
        raise EvaluationError(
            message="K must be positive",
            metric_name="FullEvidence@K",
            values={"k": k},
        )

    # Validate min_overlap (Requirement 8.7)
    if not (0.0 <= min_overlap <= 1.0):
        raise EvaluationError(
            message="min_overlap must be between 0 and 1",
            metric_name="FullEvidence@K",
            values={"min_overlap": min_overlap},
        )

    # Validate non-empty gold spans
    G = union(gold_spans)
    if length(G) == 0:
        raise EvaluationError(
            message="Gold spans cannot be empty",
            metric_name="FullEvidence@K",
            values={"gold_spans": gold_spans},
        )

    # Compute union of top-K retrieved spans
    R = union(retrieved_spans[:k])

    # Check ALL gold spans for minimum overlap (Requirements 8.3, 8.4)
    for gold_span in G:
        # Compute overlap fraction for this gold span
        overlap_intervals = intersection([gold_span], R)
        overlap_len = length(overlap_intervals)
        gold_len = gold_span[1] - gold_span[0]

        overlap_fraction = overlap_len / gold_len if gold_len > 0 else 0.0

        # If any gold span fails threshold, return 0 (Requirement 8.4)
        if overlap_fraction < min_overlap:
            return 0

    # All gold spans met threshold, return 1 (Requirement 8.3)
    return 1
