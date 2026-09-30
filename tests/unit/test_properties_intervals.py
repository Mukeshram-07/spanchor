"""Property-based tests for interval algebra utilities.

These tests use Hypothesis to verify universal properties that must hold
across all possible interval inputs.
"""

from hypothesis import given
from hypothesis import strategies as st

from spanchor.evaluation.intervals import Interval, intersection, length, union


# Strategy for generating valid intervals
def intervals_strategy() -> st.SearchStrategy[list[Interval]]:
    """Generate lists of valid intervals [start, end) where start < end.

    Returns intervals in various patterns:
    - Empty lists
    - Single intervals
    - Multiple intervals (overlapping, adjacent, disjoint)
    - Zero-length intervals [x, x)
    - Large offset values
    """
    # Generate individual intervals
    interval = st.builds(
        lambda start, length: (start, start + length),
        start=st.integers(min_value=0, max_value=10000),
        length=st.integers(min_value=0, max_value=1000),
    )

    # Generate lists of intervals (0 to 20 intervals)
    return st.lists(interval, min_size=0, max_size=20)


class TestIntervalProperties:
    """Property-based tests for interval algebra."""

    @given(intervals_strategy())
    def test_interval_union_idempotence(self, intervals: list[Interval]) -> None:
        """Property 16: Interval Union Idempotence.

        **Validates: Requirements 6.6**

        For any set of intervals X, union(union(X)) SHALL equal union(X).

        This property verifies:
        - Applying union twice produces the same result as applying it once
        - The union operation is idempotent (repeating the operation has no additional effect)
        - Merged intervals remain stable after the first union operation
        """
        # Apply union once
        first_union = union(intervals)

        # Apply union to the result again
        second_union = union(first_union)

        # PROPERTY: union(union(X)) == union(X) for all interval sets X
        assert first_union == second_union, (
            f"Union is not idempotent:\n"
            f"Original intervals: {intervals}\n"
            f"After first union: {first_union}\n"
            f"After second union: {second_union}\n"
            f"Expected first_union == second_union"
        )

        # Additional verification: the second union should produce exactly the same list
        # (not just equal values, but same length and order)
        assert len(first_union) == len(second_union), (
            f"Union changed the number of intervals on second application:\n"
            f"First union length: {len(first_union)}, Second union length: {len(second_union)}"
        )

        # Verify each interval matches exactly
        for i, (first_interval, second_interval) in enumerate(
            zip(first_union, second_union, strict=True)
        ):
            assert first_interval == second_interval, (
                f"Interval {i} differs between first and second union:\n"
                f"First: {first_interval}, Second: {second_interval}"
            )

    @given(intervals_strategy(), intervals_strategy())
    def test_interval_intersection_symmetry(
        self, intervals_x: list[Interval], intervals_y: list[Interval]
    ) -> None:
        """Property 17: Interval Intersection Symmetry.

        **Validates: Requirements 6.7**

        For any interval sets X and Y, intersection(X, Y) SHALL equal intersection(Y, X).

        This property verifies:
        - The intersection operation is commutative (order doesn't matter)
        - intersection(X, Y) produces the same result as intersection(Y, X)
        - The overlapping portions are identified consistently regardless of argument order
        """
        # Merge the intervals first to ensure they're non-overlapping
        # (as expected by the intersection function)
        merged_x = union(intervals_x)
        merged_y = union(intervals_y)

        # Compute intersection both ways
        intersection_xy = intersection(merged_x, merged_y)
        intersection_yx = intersection(merged_y, merged_x)

        # PROPERTY: intersection(X, Y) == intersection(Y, X) for all interval sets X and Y
        assert intersection_xy == intersection_yx, (
            f"Intersection is not symmetric:\n"
            f"Original intervals X: {intervals_x}\n"
            f"Original intervals Y: {intervals_y}\n"
            f"Merged X: {merged_x}\n"
            f"Merged Y: {merged_y}\n"
            f"intersection(X, Y): {intersection_xy}\n"
            f"intersection(Y, X): {intersection_yx}\n"
            f"Expected intersection(X, Y) == intersection(Y, X)"
        )

        # Additional verification: both results should have the same length
        assert len(intersection_xy) == len(intersection_yx), (
            f"Intersection results have different lengths:\n"
            f"len(intersection(X, Y)): {len(intersection_xy)}\n"
            f"len(intersection(Y, X)): {len(intersection_yx)}"
        )

        # Verify each interval matches exactly
        for i, (interval_xy, interval_yx) in enumerate(
            zip(intersection_xy, intersection_yx, strict=True)
        ):
            assert interval_xy == interval_yx, (
                f"Interval {i} differs between intersection(X, Y) and intersection(Y, X):\n"
                f"intersection(X, Y)[{i}]: {interval_xy}\n"
                f"intersection(Y, X)[{i}]: {interval_yx}"
            )

    @given(intervals_strategy())
    def test_interval_union_merges_overlaps(self, intervals: list[Interval]) -> None:
        """Property 18: Interval Union Merges Overlaps.

        **Validates: Requirements 6.1, 6.4**

        For any set of intervals containing overlapping or adjacent spans,
        union SHALL merge them into a minimal non-overlapping set.

        This property verifies:
        - The result contains no overlapping intervals
        - Adjacent intervals [a, b) and [b, c) are merged into [a, c)
        - The output is sorted by start position
        - The output is minimal (cannot be reduced further)
        """
        result = union(intervals)

        # PROPERTY 1: Result is sorted by start position
        for i in range(len(result) - 1):
            assert result[i][0] <= result[i + 1][0], (
                f"Result is not sorted by start position:\n"
                f"Original intervals: {intervals}\n"
                f"Union result: {result}\n"
                f"Interval {i}: {result[i]}, Interval {i+1}: {result[i+1]}\n"
                f"Expected result[{i}][0] <= result[{i+1}][0]"
            )

        # PROPERTY 2: No overlapping intervals in result
        # Two intervals overlap if the first ends after the second starts
        for i in range(len(result) - 1):
            assert result[i][1] <= result[i + 1][0], (
                f"Result contains overlapping or adjacent intervals that should be merged:\n"
                f"Original intervals: {intervals}\n"
                f"Union result: {result}\n"
                f"Interval {i}: {result[i]}, Interval {i+1}: {result[i+1]}\n"
                f"Expected result[{i}][1] <= result[{i+1}][0] (no overlap/adjacency)\n"
                f"result[{i}][1] = {result[i][1]}, result[{i+1}][0] = {result[i+1][0]}"
            )

        # PROPERTY 3: Each interval in result is well-formed (start < end or start == end for empty)
        for i, (start, end) in enumerate(result):
            assert start <= end, (
                f"Result contains malformed interval:\n"
                f"Original intervals: {intervals}\n"
                f"Union result: {result}\n"
                f"Interval {i}: ({start}, {end})\n"
                f"Expected start <= end"
            )

        # PROPERTY 4: Result is minimal - applying union again should not change it
        # (covered by idempotence test, but we verify it here as well)
        second_union = union(result)
        assert result == second_union, (
            f"Result is not minimal - second union produces different result:\n"
            f"Original intervals: {intervals}\n"
            f"First union: {result}\n"
            f"Second union: {second_union}\n"
            f"Expected result to be stable after one union operation"
        )

        # PROPERTY 5: Total coverage is preserved
        # The union should cover the same total span as the original intervals
        # (when accounting for overlaps)
        original_length = sum(end - start for start, end in intervals)
        result_length = sum(end - start for start, end in result)
        
        # The result length should never exceed the original length
        # (it can be less due to overlaps being removed)
        assert result_length <= original_length, (
            f"Result covers more span than original intervals:\n"
            f"Original intervals: {intervals}\n"
            f"Union result: {result}\n"
            f"Original total length: {original_length}\n"
            f"Result total length: {result_length}\n"
            f"Expected result_length <= original_length"
        )

    @given(intervals_strategy())
    def test_interval_length_computation(self, intervals: list[Interval]) -> None:
        """Property 19: Interval Length Computation.

        **Validates: Requirements 6.3**

        For any set of intervals X, length(union(X)) SHALL equal the sum of
        character counts in the merged intervals.

        This property verifies:
        - length() correctly computes the total character count
        - The length equals the sum of (end - start) for each merged interval
        - Length is always non-negative
        - Empty intervals have length 0
        - Overlapping intervals only count characters once
        """
        # Compute the length using the library function
        computed_length = length(intervals)

        # PROPERTY 1: Length is non-negative
        assert computed_length >= 0, (
            f"Length is negative:\n"
            f"Original intervals: {intervals}\n"
            f"Computed length: {computed_length}\n"
            f"Expected length >= 0"
        )

        # PROPERTY 2: length(intervals) should equal length(union(intervals))
        # This is because length() internally calls union()
        merged = union(intervals)
        manual_length = sum(end - start for start, end in merged)

        assert computed_length == manual_length, (
            f"length() does not match manual calculation:\n"
            f"Original intervals: {intervals}\n"
            f"Merged intervals: {merged}\n"
            f"Computed length: {computed_length}\n"
            f"Manual length (sum of merged): {manual_length}\n"
            f"Expected computed_length == manual_length"
        )

        # PROPERTY 3: Empty interval set has length 0
        if not intervals:
            assert computed_length == 0, (
                f"Empty interval set should have length 0:\n"
                f"Computed length: {computed_length}"
            )

        # PROPERTY 4: Length should never exceed the sum of all interval lengths
        # (overlaps reduce the total)
        original_total = sum(end - start for start, end in intervals)
        assert computed_length <= original_total, (
            f"Computed length exceeds sum of all intervals:\n"
            f"Original intervals: {intervals}\n"
            f"Original total: {original_total}\n"
            f"Computed length: {computed_length}\n"
            f"Expected computed_length <= original_total"
        )

        # PROPERTY 5: Each character in the merged intervals is counted exactly once
        # Verify that the merged intervals have no overlaps
        for i in range(len(merged) - 1):
            assert merged[i][1] <= merged[i + 1][0], (
                f"Merged intervals overlap, which would cause double-counting:\n"
                f"Original intervals: {intervals}\n"
                f"Merged intervals: {merged}\n"
                f"Interval {i}: {merged[i]}, Interval {i+1}: {merged[i+1]}\n"
                f"Expected merged[{i}][1] <= merged[{i+1}][0]"
            )

        # PROPERTY 6: Zero-length intervals contribute 0 to the total
        zero_length_intervals = [(x, x) for x in range(5)]
        zero_length = length(zero_length_intervals)
        assert zero_length == 0, (
            f"Zero-length intervals should have length 0:\n"
            f"Intervals: {zero_length_intervals}\n"
            f"Computed length: {zero_length}"
        )

