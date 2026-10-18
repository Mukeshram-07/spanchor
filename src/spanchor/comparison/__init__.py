"""Run comparison and regression detection.

Compares baseline and candidate runs to detect per-query regressions
with configurable policy thresholds. Supports optional bootstrap-based
statistical analysis for confidence intervals (v0.4.0+).
"""

from spanchor.comparison.compare import ComparisonResult, compare
from spanchor.comparison.policy import RegressionPolicy, load_policy, merge_policy
from spanchor.comparison.statistics import BootstrapResult, StatisticsConfig

__all__ = [
    "compare",
    "ComparisonResult",
    "RegressionPolicy",
    "load_policy",
    "merge_policy",
    "StatisticsConfig",
    "BootstrapResult",
]
