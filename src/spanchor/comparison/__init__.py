"""Run comparison and regression detection.

Compares baseline and candidate runs to detect per-query regressions
with configurable policy thresholds.
"""

from spanchor.comparison.compare import ComparisonResult, compare
from spanchor.comparison.policy import RegressionPolicy, load_policy, merge_policy

__all__ = [
    "compare",
    "ComparisonResult",
    "RegressionPolicy",
    "load_policy",
    "merge_policy",
]
