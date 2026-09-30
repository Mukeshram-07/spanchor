"""Run model representing a complete evaluation result.

A Run captures the results of evaluating a set of queries against a retrieval
system, including per-query metrics, aggregate metrics, and mapping statistics.
"""

from dataclasses import dataclass
from typing import Any

from spanchor.models.query import Query


@dataclass(frozen=True, slots=True)
class Run:
    """Complete evaluation result with metrics and statistics.

    A Run represents the output of evaluating a retrieval system against a
    gold set of queries. It includes:
    - The timestamp when the evaluation was performed
    - The queries that were evaluated (immutable tuple)
    - Per-query metrics (e.g., recall@k, precision@k for each query)
    - Aggregate metrics (e.g., mean recall@k across all queries)
    - Configuration parameters used during evaluation
    - Mapper statistics tracking chunk-to-span mapping outcomes

    Attributes:
        timestamp: ISO format timestamp (e.g., "2024-01-15T10:30:00Z")
        queries: Tuple of Query objects that were evaluated (immutable)
        per_query_metrics: Dict mapping query_id to metrics dict
            Example: {"q1": {"recall@5": 0.85, "precision@5": 0.90}}
        aggregate_metrics: Dict of aggregate metrics across all queries
            Example: {"mean_recall@5": 0.78, "mean_precision@5": 0.82}
        config: Configuration parameters used during evaluation
            Example: {"k_values": [5, 10], "min_overlap": 0.5}
        mapper_stats: Chunk-to-span mapping statistics
            Example: {"MAPPED_EXACT": 42, "MAPPED_NORMALIZED": 8,
                     "AMBIGUOUS": 2, "UNMAPPED": 3}
        schema_version: Schema version for forward compatibility
    """

    timestamp: str
    queries: tuple[Query, ...]
    per_query_metrics: dict[str, dict[str, float]]
    aggregate_metrics: dict[str, float]
    config: dict[str, Any]
    mapper_stats: dict[str, int]
    schema_version: str = "0.1.0"
