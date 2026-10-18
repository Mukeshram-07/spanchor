"""Pluggable metric registry for evaluation.

This module provides a registry pattern for metrics, allowing users to register
custom metrics while preserving backward compatibility by providing default
implementations of the 5 standard metrics (Recall@K, Precision@K, Hit@K,
FullEvidence@K, IoU).

The registry is optional - if not provided to evaluate(), a default registry
is automatically created with all standard metrics.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from spanchor.evaluation.hit import full_evidence_at_k, hit_at_k
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.iou import iou
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k
from spanchor.evaluation.setwise import (
    fragmentation_ratio,
    pairwise_overlap,
    span_concentration,
)


@dataclass
class MetricDefinition:
    """Definition of a single metric.

    A metric definition specifies:
    - name: Unique metric identifier (e.g., "recall@5")
    - compute_fn: Callable that computes the metric
    - result_type: Python type of the result (float or int)

    The compute_fn signature depends on the metric type. Common patterns:
    - Per-query metrics: (gold_spans, retrieved_spans, k, min_overlap=0.5) -> float | int
    - Diagnostic metrics: (gold_spans, retrieved_spans) -> float

    Examples:
        >>> recall_def = MetricDefinition(
        ...     name="recall@5",
        ...     compute_fn=lambda g, r, k: recall_at_k(g, r, k),
        ...     result_type=float,
        ... )
    """

    name: str
    compute_fn: Callable[..., Any]
    result_type: type


class MetricRegistry:
    """Registry for pluggable metrics.

    The registry maintains a mapping of metric names to metric definitions.
    Users can:
    - Register new metrics
    - Override existing metrics
    - Compute all registered metrics for a given query

    The default registry includes the 5 standard metrics:
    - recall@{k}
    - precision@{k}
    - hit@{k}
    - full_evidence@{k}
    - iou

    Examples:
        >>> # Use default registry (all 5 standard metrics)
        >>> registry = MetricRegistry(k=5, min_overlap=0.5)
        >>> registry.register(
        ...     MetricDefinition(
        ...         name="custom_metric",
        ...         compute_fn=lambda g, r: 0.5,
        ...         result_type=float,
        ...     )
        ... )
        >>> len(registry.get_all_metrics())
        6  # 5 standard + 1 custom

        >>> # Custom metric computation
        >>> result = registry.compute_metric(
        ...     metric_name="recall@5",
        ...     gold_spans=[(0, 10)],
        ...     retrieved_spans=[(0, 5)],
        ... )
        >>> result
        0.5
    """

    def __init__(self, k: int = 5, min_overlap: float = 0.5):
        """Initialize registry with default 5 standard metrics.

        Args:
            k: Default K value for @K metrics (default: 5)
            min_overlap: Default min_overlap for Hit@K and FullEvidence@K (default: 0.5)
        """
        self._metrics: dict[str, MetricDefinition] = {}
        self._k: int = k
        self._min_overlap: float = min_overlap
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the 5 standard metrics with defaults."""
        k = self._k
        min_overlap = self._min_overlap

        # Create closures that capture K and min_overlap
        def make_recall() -> Callable[..., float]:
            return lambda g, r: recall_at_k(g, r, k)

        def make_precision() -> Callable[..., float]:
            return lambda g, r: precision_at_k(g, r, k)

        def make_hit() -> Callable[..., int]:
            return lambda g, r: hit_at_k(g, r, k, min_overlap)

        def make_full_evidence() -> Callable[..., int]:
            return lambda g, r: full_evidence_at_k(g, r, k, min_overlap)

        # Register standard 5 metrics
        self._metrics[f"recall@{k}"] = MetricDefinition(
            name=f"recall@{k}",
            compute_fn=make_recall(),
            result_type=float,
        )

        self._metrics[f"precision@{k}"] = MetricDefinition(
            name=f"precision@{k}",
            compute_fn=make_precision(),
            result_type=float,
        )

        self._metrics[f"hit@{k}"] = MetricDefinition(
            name=f"hit@{k}",
            compute_fn=make_hit(),
            result_type=int,
        )

        self._metrics[f"full_evidence@{k}"] = MetricDefinition(
            name=f"full_evidence@{k}",
            compute_fn=make_full_evidence(),
            result_type=int,
        )

        self._metrics["iou"] = MetricDefinition(
            name="iou",
            compute_fn=iou,
            result_type=float,
        )

        # Register set-wise structural metrics (Feature 5)
        # Note: These metrics take only retrieved_spans, not gold_spans
        # We use lambda to adapt the signature
        self._metrics["span_concentration"] = MetricDefinition(
            name="span_concentration",
            compute_fn=lambda g, r: span_concentration(r),  # Only uses retrieved
            result_type=float,
        )

        self._metrics["fragmentation_ratio"] = MetricDefinition(
            name="fragmentation_ratio",
            compute_fn=lambda g, r: fragmentation_ratio(r),  # Only uses retrieved
            result_type=float,
        )

        self._metrics["pairwise_overlap"] = MetricDefinition(
            name="pairwise_overlap",
            compute_fn=lambda g, r: pairwise_overlap(r),  # Only uses retrieved
            result_type=float,
        )

    def register(self, metric_definition: MetricDefinition) -> None:
        """Register a metric definition.

        If a metric with the same name already exists, it is overridden.

        Args:
            metric_definition: MetricDefinition to register
        """
        self._metrics[metric_definition.name] = metric_definition

    def get(self, metric_name: str) -> MetricDefinition | None:
        """Get a metric definition by name.

        Args:
            metric_name: Name of the metric

        Returns:
            MetricDefinition if found, None otherwise
        """
        return self._metrics.get(metric_name)

    def get_all_metrics(self) -> dict[str, MetricDefinition]:
        """Get all registered metrics.

        Returns:
            Dictionary mapping metric names to MetricDefinition objects
        """
        return self._metrics.copy()

    def compute_metric(
        self,
        metric_name: str,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
    ) -> float | int:
        """Compute a single metric value.

        Args:
            metric_name: Name of the metric to compute
            gold_spans: List of gold evidence spans [start, end)
            retrieved_spans: List of retrieved spans [start, end)

        Returns:
            Computed metric value

        Raises:
            KeyError: If metric_name not registered
        """
        metric_def = self.get(metric_name)
        if metric_def is None:
            raise KeyError(f"Metric '{metric_name}' not registered")

        # Call the compute function with appropriate arguments
        compute_fn = metric_def.compute_fn
        result: Any = compute_fn(gold_spans, retrieved_spans)
        return result  # type: ignore[no-any-return]

    def compute_all(
        self,
        gold_spans: list[Interval],
        retrieved_spans: list[Interval],
    ) -> dict[str, float | int]:
        """Compute all registered metrics for a query.

        Args:
            gold_spans: List of gold evidence spans [start, end)
            retrieved_spans: List of retrieved spans [start, end)

        Returns:
            Dictionary mapping metric names to computed values
        """
        results: dict[str, float | int] = {}

        for metric_name in self._metrics:
            try:
                results[metric_name] = self.compute_metric(
                    metric_name=metric_name,
                    gold_spans=gold_spans,
                    retrieved_spans=retrieved_spans,
                )
            except Exception:
                # Skip metrics that fail (e.g., empty gold spans)
                # This allows partial metric computation
                pass

        return results
