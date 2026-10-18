"""Comparison engine for regression detection between evaluation runs.

Compares a baseline Run against a candidate Run, computing per-query metric
deltas and classifying each query as IMPROVED, REGRESSION, or UNCHANGED based
on configurable per-metric thresholds (policy).
"""

import warnings
from dataclasses import dataclass
from typing import Literal

from spanchor.comparison.statistics import (
    BootstrapResult,
    StatisticsConfig,
    compute_bootstrap_ci,
)
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

        statistics_enabled: Whether statistical analysis was performed (v0.4.0+).
        bootstrap_results: Per-metric bootstrap CI results (v0.4.0+).
            Maps metric_name -> BootstrapResult.
            None if statistics disabled.
        num_paired_queries: Number of paired queries in bootstrap (v0.4.0+).

        setwise_deltas: Optional per-query set-wise metric deltas (v0.4.0+).
            Maps query_id -> metric_name -> delta value.
            Includes: span_concentration, fragmentation_ratio, pairwise_overlap deltas.
            Example: {"q1": {"span_concentration": -0.05, "fragmentation_ratio": 0.1}}
            None if set-wise metrics disabled or unavailable.

        setwise_aggregate_deltas: Optional aggregate set-wise metric deltas (v0.4.0+).
            Macro-average delta for each set-wise metric across queries.
            Example: {"span_concentration": -0.02, "fragmentation_ratio": 0.05}
            None if set-wise metrics disabled or unavailable.
    """

    per_query_deltas: dict[str, dict[str, float]]
    per_query_status: dict[str, Literal["IMPROVED", "REGRESSION", "UNCHANGED"]]
    aggregate_deltas: dict[str, float]
    has_regression: bool
    statistics_enabled: bool = False
    bootstrap_results: dict[str, BootstrapResult] | None = None
    num_paired_queries: int = 0
    setwise_deltas: dict[str, dict[str, float]] | None = None
    setwise_aggregate_deltas: dict[str, float] | None = None


def compare(
    baseline: Run,
    candidate: Run,
    policy: dict[str, float],
    min_query_count: int | None = None,
    statistics_config: StatisticsConfig | None = None,
    include_setwise: bool = False,
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
        statistics_config: Optional StatisticsConfig for bootstrap CI analysis.
            If provided and enabled, compute confidence intervals for metric deltas
            (v0.4.0+). Default: None (statistics disabled, backward compatible).
        include_setwise: Optional flag to include set-wise metrics computation.
            If True and both runs have per-query retrieval results, compute
            set-wise metric deltas (span_concentration, fragmentation_ratio, pairwise_overlap).
            Default: False (backward compatible, setwise disabled).

    Returns:
        ComparisonResult with per-query, aggregate, and optional statistical and
        set-wise information.

    Raises:
        ComparisonError: If the runs share no common queries, making comparison
            meaningless, if the common query count is below min_query_count, or if
            statistics are enabled but insufficient paired queries exist.

    Example:
        >>> result = compare(baseline_run, candidate_run, {"recall@5": 0.05})
        >>> result.has_regression
        True
        >>> result.per_query_status["q1"]
        'REGRESSION'
        >>> result.setwise_deltas is None  # Not enabled by default
        True
        >>> result = compare(baseline_run, candidate_run, {}, include_setwise=True)
        >>> result.setwise_deltas  # Set-wise metrics included
        {"q1": {"span_concentration": -0.05, ...}, ...}
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

    # --- Step 5: Compute bootstrap CI (if enabled) ---
    bootstrap_results: dict[str, BootstrapResult] | None = None
    num_paired_queries: int = 0

    if statistics_config and statistics_config.enabled:
        # Identify paired queries (in both baseline and candidate)
        paired_query_ids_set = set(baseline.per_query_metrics.keys()) & set(
            candidate.per_query_metrics.keys()
        )
        num_paired_queries = len(paired_query_ids_set)

        # Check minimum requirement
        if (
            statistics_config.min_paired_queries
            and num_paired_queries < statistics_config.min_paired_queries
        ):
            raise ComparisonError(
                message=(
                    f"Insufficient paired queries for statistical analysis: "
                    f"found {num_paired_queries}, "
                    f"but {statistics_config.min_paired_queries} required"
                ),
                baseline_info={"query_count": len(baseline.per_query_metrics)},
                candidate_info={
                    "query_count": len(candidate.per_query_metrics),
                    "paired_query_count": num_paired_queries,
                },
            )

        # Warn if small sample
        if num_paired_queries < 30 and num_paired_queries > 0:
            warnings.warn(
                f"Statistical analysis with only {num_paired_queries} paired queries; "
                f"CI may be unreliable (consider >=30 queries)",
                UserWarning,
                stacklevel=2,
            )

        # Compute CI for each metric
        bootstrap_results = {}
        all_metrics_set: set[str] = set()
        for deltas in per_query_deltas.values():
            all_metrics_set.update(deltas.keys())

        for metric_name in sorted(all_metrics_set):
            try:
                ci_result = compute_bootstrap_ci(
                    metric_name,
                    baseline.per_query_metrics,
                    candidate.per_query_metrics,
                    statistics_config,
                )
                bootstrap_results[metric_name] = ci_result
            except ValueError:
                # Skip metrics with no paired queries
                pass

    # --- Step 6: Compute set-wise metric deltas (if enabled and data available) ---
    setwise_deltas: dict[str, dict[str, float]] | None = None
    setwise_aggregate_deltas: dict[str, float] | None = None

    if include_setwise:
        # Import here to avoid circular dependency
        from spanchor.evaluation.setwise import compute_setwise_metrics

        # Check that both runs have retrieval results
        if (
            baseline.per_query_retrieval_results is not None
            and candidate.per_query_retrieval_results is not None
        ):
            setwise_deltas = {}

            for qid in common_query_ids:
                baseline_results = baseline.per_query_retrieval_results.get(qid)
                candidate_results = candidate.per_query_retrieval_results.get(qid)

                if baseline_results is not None and candidate_results is not None:
                    # Convert RetrievalResult objects to (document_id, start, end) tuples
                    baseline_spans: list[tuple[str, int, int]] = [
                        (r.document_id, r.start, r.end)
                        for r in baseline_results
                        if r.document_id is not None and r.start is not None and r.end is not None
                    ]
                    candidate_spans: list[tuple[str, int, int]] = [
                        (r.document_id, r.start, r.end)
                        for r in candidate_results
                        if r.document_id is not None and r.start is not None and r.end is not None
                    ]

                    # Compute set-wise metrics for baseline and candidate
                    # Cast to Union type for setwise metrics function
                    baseline_setwise = compute_setwise_metrics(
                        baseline_spans  # type: ignore[arg-type]
                    )
                    candidate_setwise = compute_setwise_metrics(
                        candidate_spans  # type: ignore[arg-type]
                    )

                    # Compute deltas
                    deltas_setwise: dict[str, float] = {}
                    for metric_name in baseline_setwise.keys():
                        if metric_name in candidate_setwise:
                            deltas_setwise[metric_name] = (
                                candidate_setwise[metric_name] - baseline_setwise[metric_name]
                            )

                    if deltas_setwise:
                        setwise_deltas[qid] = deltas_setwise

            # Compute aggregate set-wise deltas (macro-average)
            if setwise_deltas:
                all_setwise_metrics: set[str] = set()
                for deltas in setwise_deltas.values():
                    all_setwise_metrics.update(deltas.keys())

                setwise_aggregate_deltas = {}
                for metric_name in sorted(all_setwise_metrics):
                    values = [
                        deltas[metric_name]
                        for deltas in setwise_deltas.values()
                        if metric_name in deltas
                    ]
                    if values:
                        setwise_aggregate_deltas[metric_name] = sum(values) / len(values)

    return ComparisonResult(
        per_query_deltas=per_query_deltas,
        per_query_status=per_query_status,
        aggregate_deltas=aggregate_deltas,
        has_regression=has_regression,
        statistics_enabled=bool(bootstrap_results),
        bootstrap_results=bootstrap_results,
        num_paired_queries=num_paired_queries,
        setwise_deltas=setwise_deltas,
        setwise_aggregate_deltas=setwise_aggregate_deltas,
    )
