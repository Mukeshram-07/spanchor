"""Set-wise retrieval evaluation metrics (structural diagnostics).

This module provides three structural metrics that describe the organization
and redundancy patterns of retrieved span sets, independent of rank order.

These metrics are DESCRIPTIVE PROPERTIES of retrieval sets, NOT quality scores.
They complement the quality metrics (Recall@K, Precision@K, etc.) by providing
insight into retrieval behavior and structure.

Key properties:
- Set-wise (rank-independent): reordering results does not change metric values
- Per-document: offsets from different documents are never mixed
- Deterministic: repeated computation produces identical results
- No semantic claims: all measurements are based on character-span intervals

Three metrics:
1. span_concentration: Fraction of coverage in the largest contiguous region
2. fragmentation_ratio: Relative number of disjoint fragments
3. pairwise_overlap: Average normalized overlap among span pairs
"""

from collections import defaultdict
from typing import TypeAlias

from spanchor.evaluation.intervals import Interval, length, union

# Type alias for retrieved spans: can be either:
# - (start, end) — plain intervals
# - (document_id, start, end) — intervals with document IDs
RetrievedSpan: TypeAlias = tuple[int, int] | tuple[str, int, int]


def _partition_by_document(
    spans: list[RetrievedSpan],
) -> tuple[dict[str, list[Interval]], bool]:
    """Partition spans by document ID if present.

    Args:
        spans: List of (start, end) or (document_id, start, end) tuples

    Returns:
        Tuple of (dict mapping doc_id to intervals, has_doc_ids_flag)
    """
    if not spans:
        return {}, False

    first_span = spans[0]
    if len(first_span) == 3:
        # Format: (document_id, start, end)
        by_doc: dict[str, list[Interval]] = defaultdict(list)
        for doc_id, start, end in spans:  # type: ignore
            by_doc[doc_id].append((start, end))
        return dict(by_doc), True
    else:
        # Format: (start, end) — treat as single pseudo-document
        return {"_single": list(spans)}, False  # type: ignore


def span_concentration(retrieved_spans: list[RetrievedSpan]) -> float:
    """Compute span concentration (structural clustering metric).

    Measures the fraction of total coverage occupied by the largest contiguous
    region. High concentration indicates evidence clustered in one region;
    low concentration indicates scattered evidence.

    Formula:
        max_cluster_size / total_coverage

    Handles both plain intervals and intervals with document IDs.
    If document IDs are present, computes per-document then returns mean.

    Args:
        retrieved_spans: List of (start, end) or (document_id, start, end) tuples

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if no spans provided.

    Examples:
        >>> span_concentration([])
        0.0
        >>> span_concentration([(0, 50)])
        1.0
        >>> span_concentration([(0, 50), (100, 150)])
        0.5
        >>> span_concentration([(0, 50), (25, 75)])
        1.0
    """
    if not retrieved_spans:
        return 0.0

    by_doc, _ = _partition_by_document(retrieved_spans)

    if not by_doc:
        return 0.0

    # Compute metric per document
    results = []
    for doc_spans in by_doc.values():
        if not doc_spans:
            continue

        # Merge overlapping/adjacent intervals
        merged = union(doc_spans)

        if not merged:
            results.append(0.0)
            continue

        # Find largest cluster size
        max_cluster_size = max(end - start for start, end in merged)

        # Total coverage
        total_coverage = length(merged)

        if total_coverage == 0:
            results.append(0.0)
        else:
            results.append(max_cluster_size / total_coverage)

    # Return mean across documents
    return sum(results) / len(results) if results else 0.0


def fragmentation_ratio(retrieved_spans: list[RetrievedSpan]) -> float:
    """Compute fragmentation ratio (structural spread metric).

    Measures the relative number of disjoint fragments in the union of
    retrieved spans. High fragmentation indicates evidence spread across
    many separate regions; low fragmentation indicates concentrated regions.

    Formula:
        (num_fragments - 1) / (num_results - 1)

    Normalization (- 1 in both numerator and denominator) ensures:
    - Range: [0.0, 1.0]
    - Zero fragmentation when all results merge into one region
    - Maximum fragmentation when each result is a separate region
    - Undefined cases (< 2 spans) return 0.0

    Handles both plain intervals and intervals with document IDs.
    If document IDs are present, computes per-document then returns mean.

    Args:
        retrieved_spans: List of (start, end) or (document_id, start, end) tuples

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if fewer than 2 spans.

    Examples:
        >>> fragmentation_ratio([])
        0.0
        >>> fragmentation_ratio([(0, 50)])
        0.0
        >>> fragmentation_ratio([(0, 50), (100, 150)])
        1.0
        >>> fragmentation_ratio([(0, 50), (25, 75)])
        0.0
    """
    if not retrieved_spans:
        return 0.0

    by_doc, _ = _partition_by_document(retrieved_spans)

    if not by_doc:
        return 0.0

    # Compute metric per document
    results = []
    for doc_spans in by_doc.values():
        num_results = len(doc_spans)

        # Edge case: fewer than 2 results
        if num_results < 2:
            results.append(0.0)
            continue

        # Merge overlapping/adjacent intervals
        merged = union(doc_spans)

        num_fragments = len(merged)

        # Normalize by (- 1) to ensure [0, 1] range and correct semantics
        results.append((num_fragments - 1) / (num_results - 1))

    # Return mean across documents
    return sum(results) / len(results) if results else 0.0


def pairwise_overlap(retrieved_spans: list[RetrievedSpan]) -> float:
    """Compute pairwise overlap (internal redundancy metric).

    Measures average normalized intersection across all distinct pairs of
    retrieved spans. High overlap indicates redundant results; low overlap
    indicates complementary results.

    Normalization: MIN(|A|, |B|) — conservative (Jaccard-like)
    - 0.0 = no overlap (disjoint)
    - 1.0 = complete overlap (smaller span fully contained in larger)
    - Values represent fraction of smaller span overlapped

    Formula (per pair):
        overlap_ij = |intersection(R_i, R_j)| / min(|R_i|, |R_j|)

    Formula (aggregate):
        PairwiseOverlap = mean([overlap_ij for all pairs i < j])

    Handles both plain intervals and intervals with document IDs.
    If document IDs are present, computes per-document then returns mean.

    Args:
        retrieved_spans: List of (start, end) or (document_id, start, end) tuples

    Returns:
        Float in [0.0, 1.0]. Returns 0.0 if fewer than 2 spans.

    Examples:
        >>> pairwise_overlap([])
        0.0
        >>> pairwise_overlap([(0, 50)])
        0.0
        >>> pairwise_overlap([(0, 50), (100, 150)])
        0.0
        >>> pairwise_overlap([(0, 50), (0, 50)])
        1.0
        >>> pairwise_overlap([(0, 100), (50, 150)])
        0.5
    """
    if not retrieved_spans:
        return 0.0

    by_doc, _ = _partition_by_document(retrieved_spans)

    if not by_doc:
        return 0.0

    # Compute metric per document
    results = []
    for doc_spans in by_doc.values():
        n = len(doc_spans)

        # Edge case: fewer than 2 spans
        if n < 2:
            results.append(0.0)
            continue

        overlaps = []

        # Compute all pairwise overlaps
        for i in range(n):
            for j in range(i + 1, n):
                span_i = doc_spans[i]
                span_j = doc_spans[j]

                # Compute intersection
                start_i, end_i = span_i
                start_j, end_j = span_j

                intersection_start = max(start_i, start_j)
                intersection_end = min(end_i, end_j)

                # Check if intersection is valid
                if intersection_start < intersection_end:
                    intersection_size = intersection_end - intersection_start
                else:
                    intersection_size = 0

                # Compute normalized overlap using MIN normalization
                size_i = end_i - start_i
                size_j = end_j - start_j
                min_size = min(size_i, size_j)

                if min_size == 0:
                    # Edge case: zero-length span
                    overlap_ratio = 0.0
                else:
                    overlap_ratio = intersection_size / min_size

                overlaps.append(overlap_ratio)

        # Return mean of all pairwise overlaps for this document
        if overlaps:
            results.append(sum(overlaps) / len(overlaps))
        else:
            results.append(0.0)

    # Return mean across documents
    return sum(results) / len(results) if results else 0.0


def compute_setwise_metrics(
    retrieved_spans: list[RetrievedSpan],
) -> dict[str, float]:
    """Compute all three set-wise metrics in one pass.

    Convenience function for computing all set-wise metrics together,
    useful for integration with MetricRegistry.

    Args:
        retrieved_spans: List of (start, end) or (document_id, start, end) tuples

    Returns:
        Dictionary with keys: "span_concentration", "fragmentation_ratio", "pairwise_overlap"
    """
    return {
        "span_concentration": span_concentration(retrieved_spans),
        "fragmentation_ratio": fragmentation_ratio(retrieved_spans),
        "pairwise_overlap": pairwise_overlap(retrieved_spans),
    }
