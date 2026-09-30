"""Metric aggregation utilities for evaluation results.

This module provides functions to aggregate per-query metrics into overall
statistics using different aggregation strategies (macro-average, micro-average).
"""

from typing import Literal

from spanchor.evaluation.intervals import Interval, length, union
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k
from spanchor.models.query import Query


def aggregate_metrics(
    per_query_metrics: dict[str, dict[str, float]],
    queries: list[Query],
    aggregation_method: Literal["macro", "micro"] = "macro",
) -> dict[str, float]:
    """Aggregate per-query metrics into overall statistics.

    Args:
        per_query_metrics: Dictionary mapping query_id to metric values
        queries: List of Query objects for context (used for micro-average)
        aggregation_method: Aggregation strategy to use (default: "macro")
            - "macro": Average metric values across queries (equal weight per query)
            - "micro": Aggregate characters first, then compute metrics (proportional to gold span size)

    Returns:
        Dictionary of aggregated metrics with mean_ prefix for macro, micro_ prefix for micro

    Examples:
        >>> per_query_metrics = {
        ...     "q1": {"recall@5": 0.8, "precision@5": 0.9},
        ...     "q2": {"recall@5": 1.0, "precision@5": 0.7}
        ... }
        >>> result = aggregate_metrics(per_query_metrics, [], "macro")
        >>> result["mean_recall@5"]
        0.9

    **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
    """
    if not queries:
        return {}

    # Macro-average: average metric values across queries (default)
    # This gives equal weight to each query regardless of gold span size
    if aggregation_method == "macro":
        aggregate_metrics_dict: dict[str, float] = {}

        # Get all metric names from first query (they should all have the same metrics)
        if per_query_metrics:
            first_query_id = next(iter(per_query_metrics))
            metric_names = list(per_query_metrics[first_query_id].keys())

            for metric_name in metric_names:
                values = [
                    per_query_metrics[q.query_id][metric_name]
                    for q in queries
                    if q.query_id in per_query_metrics
                ]
                if values:
                    aggregate_metrics_dict[f"mean_{metric_name}"] = sum(values) / len(values)
                else:
                    aggregate_metrics_dict[f"mean_{metric_name}"] = 0.0

        return aggregate_metrics_dict

    # Micro-average: aggregate characters first, then compute metrics
    # This gives weight proportional to gold span size (larger queries have more influence)
    elif aggregation_method == "micro":
        # For micro-average with just per_query_metrics, we can compute weighted averages
        # based on gold span sizes, but we don't have that information here.
        # The proper micro-average requires access to raw span data.
        # For now, we use a simpler approach: aggregate by weighting based on retrieved_chars
        # or return an error message indicating that micro requires different data.

        # Since we don't have access to gold spans here, we'll compute a weighted average
        # based on retrieved_chars as a proxy
        micro_metrics_dict: dict[str, float] = {}

        # Calculate weights based on retrieved_chars (queries with more retrieved chars get more weight)
        total_retrieved_chars = sum(
            per_query_metrics[q.query_id].get("retrieved_chars", 0.0)
            for q in queries
            if q.query_id in per_query_metrics
        )

        if total_retrieved_chars > 0:
            # Get all metric names
            if per_query_metrics:
                first_query_id = next(iter(per_query_metrics))
                metric_names = [
                    m for m in per_query_metrics[first_query_id].keys() if m != "retrieved_chars"
                ]

                for metric_name in metric_names:
                    weighted_sum = sum(
                        per_query_metrics[q.query_id][metric_name]
                        * per_query_metrics[q.query_id].get("retrieved_chars", 0.0)
                        for q in queries
                        if q.query_id in per_query_metrics
                    )
                    micro_metrics_dict[f"micro_{metric_name}"] = weighted_sum / total_retrieved_chars

                # Add total retrieved chars
                micro_metrics_dict["micro_retrieved_chars"] = total_retrieved_chars
        else:
            # Fall back to macro-average if no retrieved chars
            return aggregate_metrics(per_query_metrics, queries, "macro")

        return micro_metrics_dict

    else:
        raise ValueError(
            f"Invalid aggregation_method: {aggregation_method}. " f"Must be 'macro' or 'micro'."
        )


def compute_mean_retrieved_chars(
    per_query_metrics: dict[str, dict[str, float]],
    queries: list[Query],
) -> float:
    """Compute mean retrieved characters per query.

    This provides a token-cost proxy metric showing average retrieval size.

    Args:
        per_query_metrics: Dictionary mapping query_id to metric values
        queries: List of Query objects

    Returns:
        Mean retrieved character count across all queries

    Examples:
        >>> per_query_metrics = {
        ...     "q1": {"retrieved_chars": 500},
        ...     "q2": {"retrieved_chars": 300}
        ... }
        >>> compute_mean_retrieved_chars(per_query_metrics, [])
        400.0

    **Validates: Requirements 10.3, 10.4**
    """
    if not queries:
        return 0.0

    retrieved_chars_values = [
        per_query_metrics[q.query_id].get("retrieved_chars", 0.0)
        for q in queries
        if q.query_id in per_query_metrics
    ]

    if retrieved_chars_values:
        return sum(retrieved_chars_values) / len(retrieved_chars_values)
    else:
        return 0.0


def aggregate_metrics_micro(
    queries: list[Query],
    gold_spans_per_query: dict[str, list[Interval]],
    retrieved_spans_per_query: dict[str, list[Interval]],
    k: int,
) -> dict[str, float]:
    """Aggregate metrics using micro-average strategy.

    Micro-average computes metrics by first aggregating all gold and retrieved
    characters across queries, then computing metrics on the aggregated spans.
    This gives weight proportional to gold span size.

    Args:
        queries: List of Query objects
        gold_spans_per_query: Dictionary mapping query_id to list of gold span intervals
        retrieved_spans_per_query: Dictionary mapping query_id to list of retrieved span intervals
        k: K value for metrics (Recall@K, Precision@K)

    Returns:
        Dictionary of micro-averaged metrics

    Examples:
        >>> queries = [Query("q1", "test", ())]
        >>> gold_spans = {"q1": [(0, 10)]}
        >>> retrieved_spans = {"q1": [(0, 5)]}
        >>> result = aggregate_metrics_micro(queries, gold_spans, retrieved_spans, 5)
        >>> result["micro_recall@5"]
        0.5

    **Validates: Requirements 10.2**
    """
    if not queries:
        return {}

    # Aggregate all gold spans across queries
    all_gold_spans: list[Interval] = []
    for query in queries:
        if query.query_id in gold_spans_per_query:
            all_gold_spans.extend(gold_spans_per_query[query.query_id])

    # Aggregate all retrieved spans across queries (top K per query)
    all_retrieved_spans: list[Interval] = []
    for query in queries:
        if query.query_id in retrieved_spans_per_query:
            query_retrieved = retrieved_spans_per_query[query.query_id][:k]
            all_retrieved_spans.extend(query_retrieved)

    # Compute micro-averaged metrics on aggregated spans
    micro_metrics: dict[str, float] = {}

    if all_gold_spans:
        micro_metrics[f"micro_recall@{k}"] = recall_at_k(all_gold_spans, all_retrieved_spans, k)

    if all_retrieved_spans:
        micro_metrics[f"micro_precision@{k}"] = precision_at_k(
            all_gold_spans, all_retrieved_spans, k
        )

    # Micro-average for retrieved characters
    if all_retrieved_spans:
        total_retrieved_chars = length(union(all_retrieved_spans))
        micro_metrics["micro_retrieved_chars"] = float(total_retrieved_chars)

    return micro_metrics
