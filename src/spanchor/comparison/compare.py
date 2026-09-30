"""Comparison engine for regression detection between evaluation runs.

Compares a baseline Run against a candidate Run, computing per-query metric
deltas and classifying each query as IMPROVED, REGRESSION, or UNCHANGED based
on configurable per-metric thresholds (policy).
"""

from dataclasses import dataclass
from typing import Literal

from spanchor.errors import ComparisonError
from spanchor.models.run import Run


@dataclass
class ComparisonResult:
    """Result of comparing a baseline run against a candidate run.

    Attributes:
        per_query_deltas: Per-query metric deltas (candidate - baseline).
            Maps query_id -> metric_name -> delta value.
            Example: {"q1": {"recall@5": -0.1, "precision@5": 0.05}}

        per_query_status: Classification for each query.
            Maps query_id -> "IMPROVED" | "REGRESSION" | "UNCHANGED".
            Example: {"q1": "REGRESSION", "q2": "IMPROVED"}

        aggregate_deltas: Macro-average delta for each metric across all queries.
            Example: {"recall@5": -0.02, "precision@5": 0.01}

        has_regression: True if ANY query is classified as REGRESSION.
    """

    per_query_deltas: dict[str, dict[str, float]]
    per_query_status: dict[str, Literal["IMPROVED", "REGRESSION", "UNCHANGED"]]
    aggregate_deltas: dict[str, float]
    has_regression: bool


def compare(
    baseline: Run,
    candidate: Run,
    policy: dict[str, float],
    min_query_count: int | None = None,
) -> ComparisonResult:
    """Compare two evaluation runs and classify per-query metric changes.

    Computes the delta (candidate - baseline) for every metric on every query
    that exists in both runs, then classifies each query using the policy
    thresholds:

    - REGRESSION  : any metric delta < -max_drop (drops more than allowed)
    - IMPROVED    : any metric delta >  max_drop (improves beyond threshold)
    - UNCHANGED   : all metric deltas are within [-max_drop, +max_drop]

    When policy is empty ({}), every query is UNCHANGED (no thresholds enforced).

    Aggregate deltas are computed as the macro-average of per-query deltas for
    each metric that appears in at least one query.

    Args:
        baseline: The baseline Run to compare against.
        candidate: The candidate Run being evaluated.
        policy: Per-metric max_drop thresholds.
            Example: {"recall@5": 0.05, "hit@5": 0.10}
            An empty dict means no thresholds — all queries are UNCHANGED.
        min_query_count: Optional minimum number of common queries required for
            the comparison to proceed. If the number of common queries is below
            this value, ComparisonError is raised with a clear message.

    Returns:
        ComparisonResult with per-query and aggregate information.

    Raises:
        ComparisonError: If the runs share no common queries, making comparison
            meaningless, or if the common query count is below min_query_count.

    Example:
        >>> result = compare(baseline_run, candidate_run, {"recall@5": 0.05})
        >>> result.has_regression
        True
        >>> result.per_query_status["q1"]
        'REGRESSION'
    """
    baseline_metrics = baseline.per_query_metrics
    candidate_metrics = candidate.per_query_metrics

    common_query_ids = set(baseline_metrics.keys()) & set(candidate_metrics.keys())

    if not common_query_ids:
        raise ComparisonError(
            message=(
                "No common queries found between baseline and candidate runs. "
                "Both runs must share at least one query_id to be comparable."
            ),
            baseline_info={
                "query_count": len(baseline_metrics),
                "query_ids_sample": list(baseline_metrics.keys())[:5],
            },
            candidate_info={
                "query_count": len(candidate_metrics),
                "query_ids_sample": list(candidate_metrics.keys())[:5],
            },
        )

    # --- Minimum-query-count guard (Req 13.5, 13.6) ---
    if min_query_count is not None and len(common_query_ids) < min_query_count:
        raise ComparisonError(
            message=(
                f"Minimum query count not met: expected at least {min_query_count} "
                f"common queries but found {len(common_query_ids)}. "
                "Increase the gold set size or lower the min_query_count threshold."
            ),
            baseline_info={
                "query_count": len(baseline_metrics),
            },
            candidate_info={
                "query_count": len(candidate_metrics),
                "common_query_count": len(common_query_ids),
                "min_query_count_required": min_query_count,
            },
        )

    # --- Step 1: Compute per-query deltas ---
    per_query_deltas: dict[str, dict[str, float]] = {}

    for qid in sorted(common_query_ids):
        baseline_q = baseline_metrics[qid]
        candidate_q = candidate_metrics[qid]

        # Only compute deltas for metrics present in both runs for this query
        common_metrics = set(baseline_q.keys()) & set(candidate_q.keys())
        deltas: dict[str, float] = {}
        for metric in sorted(common_metrics):
            deltas[metric] = candidate_q[metric] - baseline_q[metric]

        per_query_deltas[qid] = deltas

    # --- Step 2: Classify each query ---
    per_query_status: dict[str, Literal["IMPROVED", "REGRESSION", "UNCHANGED"]] = {}

    for qid, deltas in per_query_deltas.items():
        status: Literal["IMPROVED", "REGRESSION", "UNCHANGED"] = "UNCHANGED"

        for metric, delta in deltas.items():
            if metric not in policy:
                # Metric has no configured threshold — skip classification for it.
                # An empty policy dict means no thresholds at all, so every query
                # stays UNCHANGED unless another metric in the policy triggers a change.
                continue

            threshold = policy[metric]

            # Round the delta to 10 decimal places to avoid floating-point
            # noise causing boundary values to misclassify.  All meaningful
            # metric differences are much larger than 1e-10.
            rounded_delta = round(delta, 10)
            if rounded_delta < -threshold:
                # Metric dropped more than allowed → REGRESSION wins immediately
                status = "REGRESSION"
                break
            elif rounded_delta > threshold:
                # Metric improved beyond threshold — mark as IMPROVED but keep
                # checking other metrics for a potential REGRESSION
                status = "IMPROVED"

        per_query_status[qid] = status

    # --- Step 3: Compute aggregate deltas (macro-average across queries) ---
    # Collect all metric names that appeared in at least one query's deltas
    all_metrics: set[str] = set()
    for deltas in per_query_deltas.values():
        all_metrics.update(deltas.keys())

    aggregate_deltas: dict[str, float] = {}
    for metric in sorted(all_metrics):
        values = [deltas[metric] for deltas in per_query_deltas.values() if metric in deltas]
        if values:
            aggregate_deltas[metric] = sum(values) / len(values)

    # --- Step 4: Set has_regression flag ---
    has_regression = any(status == "REGRESSION" for status in per_query_status.values())

    return ComparisonResult(
        per_query_deltas=per_query_deltas,
        per_query_status=per_query_status,
        aggregate_deltas=aggregate_deltas,
        has_regression=has_regression,
    )
