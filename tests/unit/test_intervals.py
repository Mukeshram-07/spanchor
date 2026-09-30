"""Unit tests for interval algebra utilities."""

from spanchor.evaluation.intervals import intersection, length, union


class TestUnion:
    """Tests for union function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        assert union([]) == []

    def test_single_interval(self):
        """Single interval returns as-is."""
        assert union([(0, 5)]) == [(0, 5)]

    def test_non_overlapping_intervals(self):
        """Non-overlapping intervals remain separate."""
        result = union([(0, 5), (10, 15)])
        assert result == [(0, 5), (10, 15)]

    def test_overlapping_intervals(self):
        """Overlapping intervals are merged."""
        result = union([(0, 5), (3, 8)])
        assert result == [(0, 8)]

    def test_adjacent_intervals(self):
        """Adjacent intervals are merged (Requirement 6.4)."""
        result = union([(0, 5), (5, 10)])
        assert result == [(0, 10)]

    def test_multiple_overlapping_intervals(self):
        """Multiple overlapping intervals merge into one."""
        result = union([(0, 5), (3, 8), (7, 12)])
        assert result == [(0, 12)]

    def test_unsorted_input(self):
        """Input order doesn't matter - intervals are sorted."""
        result = union([(10, 15), (0, 5), (5, 10)])
        assert result == [(0, 15)]

    def test_subset_interval(self):
        """Interval fully contained in another is absorbed."""
        result = union([(0, 10), (2, 5)])
        assert result == [(0, 10)]

    def test_identical_intervals(self):
        """Identical intervals merge into one."""
        result = union([(0, 5), (0, 5), (0, 5)])
        assert result == [(0, 5)]

    def test_complex_scenario(self):
        """Complex scenario with multiple gaps and overlaps."""
        result = union([(0, 5), (10, 15), (3, 12), (20, 25)])
        assert result == [(0, 15), (20, 25)]

    def test_zero_length_interval(self):
        """Zero-length intervals [x, x) are handled."""
        result = union([(0, 0), (5, 5)])
        assert result == [(0, 0), (5, 5)]

    def test_zero_length_with_normal(self):
        """Zero-length interval at boundary merges."""
        result = union([(0, 5), (5, 5)])
        assert result == [(0, 5)]


class TestIntersection:
    """Tests for intersection function."""

    def test_empty_lists(self):
        """Two empty lists return empty."""
        assert intersection([], []) == []

    def test_one_empty_list(self):
        """One empty list returns empty."""
        assert intersection([(0, 5)], []) == []
        assert intersection([], [(0, 5)]) == []

    def test_no_overlap(self):
        """Non-overlapping intervals return empty."""
        result = intersection([(0, 5)], [(10, 15)])
        assert result == []

    def test_partial_overlap(self):
        """Partial overlap returns overlapping portion (Requirement 6.5)."""
        result = intersection([(0, 5)], [(3, 8)])
        assert result == [(3, 5)]

    def test_full_overlap(self):
        """One interval fully inside another returns smaller interval."""
        result = intersection([(0, 10)], [(2, 5)])
        assert result == [(2, 5)]

    def test_identical_intervals(self):
        """Identical intervals return the interval."""
        result = intersection([(0, 5)], [(0, 5)])
        assert result == [(0, 5)]

    def test_multiple_intersections(self):
        """Multiple intervals produce multiple intersection segments."""
        result = intersection([(0, 5), (10, 15)], [(3, 12)])
        assert result == [(3, 5), (10, 12)]

    def test_adjacent_no_overlap(self):
        """Adjacent but not overlapping returns empty."""
        result = intersection([(0, 5)], [(5, 10)])
        assert result == []

    def test_symmetry(self):
        """intersection(A, B) == intersection(B, A) (Requirement 6.7)."""
        a = [(0, 5), (10, 15)]
        b = [(3, 12), (20, 25)]
        assert intersection(a, b) == intersection(b, a)

    def test_complex_scenario(self):
        """Complex scenario with multiple intervals."""
        a = [(0, 10), (20, 30), (40, 50)]
        b = [(5, 15), (25, 35), (45, 55)]
        result = intersection(a, b)
        assert result == [(5, 10), (25, 30), (45, 50)]

    def test_zero_length_intervals(self):
        """Zero-length intervals produce no intersection."""
        result = intersection([(5, 5)], [(5, 5)])
        assert result == []


class TestLength:
    """Tests for length function."""

    def test_empty_list(self):
        """Empty list has length 0."""
        assert length([]) == 0

    def test_single_interval(self):
        """Single interval returns its length."""
        assert length([(0, 5)]) == 5

    def test_non_overlapping_intervals(self):
        """Non-overlapping intervals sum their lengths."""
        assert length([(0, 5), (10, 15)]) == 10

    def test_overlapping_intervals(self):
        """Overlapping intervals count each character once (Requirement 6.3)."""
        # [0,5) and [3,8) overlap in [3,5), total unique chars: 0-8 = 8
        assert length([(0, 5), (3, 8)]) == 8

    def test_adjacent_intervals(self):
        """Adjacent intervals sum correctly."""
        assert length([(0, 5), (5, 10)]) == 10

    def test_multiple_overlapping(self):
        """Multiple overlapping intervals counted correctly."""
        # [0,5), [10,15), [3,12) -> union is [0,15)
        assert length([(0, 5), (10, 15), (3, 12)]) == 15

    def test_subset_interval(self):
        """Subset interval doesn't add to length."""
        # [2,5) is subset of [0,10), total length is 10
        assert length([(0, 10), (2, 5)]) == 10

    def test_identical_intervals(self):
        """Identical intervals counted once."""
        assert length([(0, 5), (0, 5)]) == 5

    def test_zero_length_interval(self):
        """Zero-length intervals contribute 0."""
        assert length([(5, 5)]) == 0
        assert length([(0, 5), (5, 5), (10, 15)]) == 10


class TestIntervalProperties:
    """Property-based tests for interval algebra."""

    def test_union_idempotence(self):
        """union(union(X)) == union(X) (Requirement 6.6)."""
        intervals = [(0, 5), (3, 8), (10, 15)]
        once = union(intervals)
        twice = union(once)
        assert once == twice

    def test_union_with_empty(self):
        """Union with empty list returns union of non-empty."""
        intervals = [(0, 5), (10, 15)]
        assert union(intervals + []) == union(intervals)

    def test_intersection_symmetry(self):
        """intersection(X, Y) == intersection(Y, X) (Requirement 6.7)."""
        a = [(0, 10), (20, 30)]
        b = [(5, 15), (25, 35)]
        assert intersection(a, b) == intersection(b, a)

    def test_intersection_subset_property(self):
        """Intersection is always subset of both inputs."""
        a = [(0, 10), (20, 30)]
        b = [(5, 15), (25, 35)]
        result = intersection(a, b)
        # Length of intersection should not exceed length of either input
        assert length(result) <= length(a)
        assert length(result) <= length(b)

    def test_union_length_monotonicity(self):
        """Adding intervals to union doesn't decrease length."""
        base = [(0, 5)]
        extended = [(0, 5), (10, 15)]
        assert length(extended) >= length(base)

    def test_disjoint_intersection_empty(self):
        """Intersection of disjoint sets is empty."""
        a = [(0, 5), (10, 15)]
        b = [(20, 25), (30, 35)]
        assert intersection(a, b) == []
        assert length(intersection(a, b)) == 0

    def test_length_non_negative(self):
        """Length is always non-negative."""
        test_cases = [
            [],
            [(0, 5)],
            [(0, 5), (3, 8)],
            [(5, 5)],  # Zero-length
        ]
        for intervals in test_cases:
            assert length(intervals) >= 0


class TestEdgeCases:
    """Edge case tests."""

    def test_large_intervals(self):
        """Large offset values work correctly."""
        result = union([(1000000, 1000010), (1000005, 1000015)])
        assert result == [(1000000, 1000015)]
        assert length(result) == 15

    def test_many_small_intervals(self):
        """Many small intervals merge correctly."""
        # Create 100 overlapping intervals
        intervals = [(i, i + 2) for i in range(100)]
        result = union(intervals)
        assert result == [(0, 101)]  # Should merge into one
        assert length(intervals) == 101

    def test_reverse_sorted_input(self):
        """Reverse sorted input works correctly."""
        intervals = [(50, 60), (40, 50), (30, 40), (20, 30), (10, 20)]
        result = union(intervals)
        assert result == [(10, 60)]

    def test_single_character_intervals(self):
        """Single character intervals [i, i+1) work correctly."""
        intervals = [(0, 1), (2, 3), (4, 5)]
        assert union(intervals) == [(0, 1), (2, 3), (4, 5)]
        assert length(intervals) == 3
