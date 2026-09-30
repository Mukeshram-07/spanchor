"""Interval algebra utilities for span overlap and union operations.

This module provides efficient interval operations using sorted-interval merging
with O(n log n) complexity. All intervals are half-open [start, end) where start
is inclusive and end is exclusive.

All offsets are Unicode code-point offsets.
"""

Interval = tuple[int, int]  # [start, end) half-open interval


def union(intervals: list[Interval]) -> list[Interval]:
    """Merge overlapping or adjacent intervals.

    Takes a list of intervals and returns a sorted list of non-overlapping
    intervals representing their union. Adjacent intervals (e.g., [0,5) and [5,10))
    are merged into a single interval.

    Complexity: O(n log n) due to sorting.

    Args:
        intervals: List of half-open intervals [start, end)

    Returns:
        Sorted list of merged, non-overlapping intervals

    Examples:
        >>> union([])
        []
        >>> union([(0, 5)])
        [(0, 5)]
        >>> union([(0, 5), (3, 8)])
        [(0, 8)]
        >>> union([(0, 5), (5, 10)])  # Adjacent intervals merge
        [(0, 10)]
        >>> union([(0, 5), (10, 15), (3, 12)])
        [(0, 15)]
        >>> union([(5, 10), (0, 3), (15, 20)])  # Order doesn't matter
        [(0, 3), (5, 10), (15, 20)]
    """
    if not intervals:
        return []

    # Sort by start position
    sorted_intervals = sorted(intervals)
    merged: list[Interval] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last = merged[-1]
        # Check for overlap or adjacency
        if current[0] <= last[1]:
            # Merge by extending the end to the maximum
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            # No overlap or adjacency, add as new interval
            merged.append(current)

    return merged


def intersection(a: list[Interval], b: list[Interval]) -> list[Interval]:
    """Compute the intersection of two interval sets.

    Returns only the portions where intervals from both sets overlap.
    Both input lists should be sorted and non-overlapping (i.e., output from union()).

    Args:
        a: First list of intervals (should be merged)
        b: Second list of intervals (should be merged)

    Returns:
        Sorted list of intervals representing the intersection

    Examples:
        >>> intersection([], [])
        []
        >>> intersection([(0, 5)], [])
        []
        >>> intersection([(0, 5)], [(3, 8)])
        [(3, 5)]
        >>> intersection([(0, 5), (10, 15)], [(3, 12)])
        [(3, 5), (10, 12)]
        >>> intersection([(0, 10)], [(20, 30)])  # No overlap
        []
        >>> intersection([(0, 5), (10, 15)], [(5, 10)])  # Adjacent but not overlapping
        []
    """
    if not a or not b:
        return []

    result: list[Interval] = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        # Find the overlapping portion
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])

        # If there's a valid overlap, add it
        if start < end:
            result.append((start, end))

        # Advance the pointer for the interval that ends first
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1

    return result


def length(intervals: list[Interval]) -> int:
    """Compute total character count in intervals.

    First merges overlapping intervals, then sums their lengths.
    This ensures overlapping regions are only counted once.

    Args:
        intervals: List of half-open intervals [start, end)

    Returns:
        Total number of characters covered by the intervals

    Examples:
        >>> length([])
        0
        >>> length([(0, 5)])
        5
        >>> length([(0, 5), (5, 10)])  # Adjacent intervals
        10
        >>> length([(0, 5), (3, 8)])  # Overlapping intervals
        8
        >>> length([(0, 5), (10, 15), (3, 12)])  # Multiple overlaps
        15
    """
    merged = union(intervals)
    return sum(end - start for start, end in merged)
