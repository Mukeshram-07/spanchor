"""Intersection-over-Union (IoU) diagnostic metric.

This module provides IoU as a diagnostic measure of overall span alignment quality.
Unlike Recall and Precision which measure directional coverage, IoU gives a single
symmetric score for how well two span sets align.

IoU is DIAGNOSTIC ONLY and should not be used for correctness determination or
regression policy enforcement.
"""

from spanchor.evaluation.intervals import Interval, intersection, length, union


def iou(gold_spans: list[Interval], retrieved_spans: list[Interval]) -> float:
    """Compute Intersection-over-Union between gold and retrieved spans.

    IoU measures overall alignment quality as: |G ∩ R| / |G ∪ R|
    where G is the union of gold spans and R is the union of retrieved spans.

    **This is a DIAGNOSTIC metric only.** It should not be used for:
    - Correctness determination
    - Regression policy enforcement
    - Quality thresholds in CI

    Use Recall@K and Precision@K for evaluation and regression testing.

    Properties:
    - Range: [0, 1] inclusive
    - Symmetry: iou(G, R) == iou(R, G)
    - Zero when |G ∪ R| = 0 (both sets empty)

    Args:
        gold_spans: List of gold evidence spans [start, end)
        retrieved_spans: List of retrieved spans [start, end)

    Returns:
        IoU score in [0, 1]. Returns 0.0 when both sets are empty.

    Examples:
        >>> iou([], [])
        0.0
        >>> iou([(0, 10)], [(0, 10)])
        1.0
        >>> iou([(0, 10)], [(5, 15)])  # Half overlap
        0.5
        >>> iou([(0, 10)], [(20, 30)])  # No overlap
        0.0
        >>> iou([(0, 5), (10, 15)], [(0, 15)])  # Partial coverage
        0.6666666666666666

    **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    """
    # Merge gold and retrieved spans
    G = union(gold_spans)
    R = union(retrieved_spans)

    # Compute union of both sets
    G_union_R = union(G + R)
    union_len = length(G_union_R)

    # Edge case: both sets empty (Requirement 9.3)
    if union_len == 0:
        return 0.0

    # Compute intersection
    overlap = length(intersection(G, R))

    # IoU = |G ∩ R| / |G ∪ R| (Requirements 9.1, 9.2)
    result = overlap / union_len

    # Ensure result is in [0, 1] (numerical stability)
    return max(0.0, min(1.0, result))
