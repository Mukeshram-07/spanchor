"""Statistical regression analysis for paired-query comparison.

This module implements bootstrap-based confidence intervals for quantifying
uncertainty in metric changes across paired queries.

**Design:**
- Unit of analysis: per-query metric deltas
- Bootstrap method: Deterministic resampling with seeded PRNG
- No scipy/numpy dependencies (standard library only)
- Backward compatible (disabled by default)
"""

import statistics as stats
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True, slots=True)
class StatisticsConfig:
    """Configuration for statistical regression analysis.

    Attributes:
        enabled: Enable statistical analysis (default: False for backward compat)
        confidence_level: Confidence level for CI (0.0, 1.0), default 0.95
        num_resamples: Number of bootstrap resamples, default 10,000
        random_seed: Seed for deterministic PRNG (None = use hash of inputs)
        min_paired_queries: Minimum paired queries required (None = no minimum)
    """

    enabled: bool = False
    confidence_level: float = 0.95
    num_resamples: int = 10_000
    random_seed: int | None = None
    min_paired_queries: int | None = None

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if not (0.0 < self.confidence_level < 1.0):
            raise ValueError(f"confidence_level must be in (0, 1), got {self.confidence_level}")
        if self.num_resamples <= 0:
            raise ValueError(f"num_resamples must be positive, got {self.num_resamples}")
        if self.random_seed is not None and self.random_seed < 0:
            raise ValueError(f"random_seed must be non-negative, got {self.random_seed}")


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    """Result of bootstrap analysis for a single metric.

    Attributes:
        metric_name: Name of the metric (e.g., 'recall@5')
        num_paired_queries: Number of (query, delta) pairs in bootstrap
        mean_delta: Mean of per-query deltas
        lower_ci: Lower confidence interval bound
        upper_ci: Upper confidence interval bound
        ci_level: Confidence level used (e.g., 0.95)
        num_resamples: Number of bootstrap resamples performed
        seed: Seed used for reproducibility (None if auto-generated)
    """

    metric_name: str
    num_paired_queries: int
    mean_delta: float
    lower_ci: float
    upper_ci: float
    ci_level: float
    num_resamples: int
    seed: int | None


def _compute_deltas(
    baseline_metrics: dict[str, dict[str, float]],
    candidate_metrics: dict[str, dict[str, float]],
    metric_name: str,
) -> tuple[list[float], list[str]]:
    """Extract per-query deltas for a specific metric from paired runs.

    Args:
        baseline_metrics: Per-query metrics from baseline run
        candidate_metrics: Per-query metrics from candidate run
        metric_name: Name of metric to extract (e.g., 'recall@5')

    Returns:
        Tuple of (deltas list, paired query IDs list)
        Only includes queries present in both runs.
    """
    deltas: list[float] = []
    paired_query_ids: list[str] = []

    for query_id in baseline_metrics.keys():
        if query_id not in candidate_metrics:
            continue

        baseline_val = baseline_metrics[query_id].get(metric_name)
        candidate_val = candidate_metrics[query_id].get(metric_name)

        if baseline_val is not None and candidate_val is not None:
            delta = candidate_val - baseline_val
            deltas.append(delta)
            paired_query_ids.append(query_id)

    return deltas, paired_query_ids


def _deterministic_seed(deltas: list[float], seed_override: int | None = None) -> int:
    """Generate deterministic seed from deltas or use provided seed.

    Args:
        deltas: List of delta values to hash
        seed_override: If provided, use this seed directly

    Returns:
        Deterministic seed for PRNG
    """
    if seed_override is not None:
        return seed_override

    # Hash the deltas to create a deterministic seed
    # Convert to tuple for hashability, then to int
    delta_tuple = tuple(deltas)
    seed = hash(delta_tuple) % (2**31)  # Keep it in valid range
    return abs(seed)  # Ensure non-negative


def _percentile(sorted_values: list[float], percentile: float) -> float:
    """Compute percentile of sorted values.

    Args:
        sorted_values: List of values (assumed to be sorted)
        percentile: Percentile value (0.0-100.0)

    Returns:
        Value at the given percentile
    """
    if not sorted_values:
        return 0.0

    if len(sorted_values) == 1:
        return sorted_values[0]

    # Linear interpolation method
    index = (percentile / 100.0) * (len(sorted_values) - 1)
    lower_idx = int(index)
    upper_idx = min(lower_idx + 1, len(sorted_values) - 1)
    fraction = index - lower_idx

    lower_val = sorted_values[lower_idx]
    upper_val = sorted_values[upper_idx]

    return lower_val + fraction * (upper_val - lower_val)


def compute_bootstrap_ci(
    metric_name: str,
    baseline_metrics: dict[str, dict[str, float]],
    candidate_metrics: dict[str, dict[str, float]],
    config: StatisticsConfig,
) -> BootstrapResult:
    """Compute bootstrap confidence interval for paired-query metric deltas.

    Algorithm:
    1. Extract per-query deltas (candidate - baseline)
    2. Resample deltas with replacement num_resamples times
    3. Compute mean of each resample
    4. Sort bootstrap means
    5. Extract CI from percentiles

    Args:
        metric_name: Name of metric (e.g., 'recall@5')
        baseline_metrics: Per-query metrics from baseline run
        candidate_metrics: Per-query metrics from candidate run
        config: StatisticsConfig with CI parameters

    Returns:
        BootstrapResult with CI bounds and metadata

    Raises:
        ValueError: If no paired queries or invalid configuration
    """
    # Extract deltas
    deltas, paired_query_ids = _compute_deltas(baseline_metrics, candidate_metrics, metric_name)

    num_paired = len(deltas)

    # Handle edge cases
    if num_paired == 0:
        raise ValueError(f"No paired queries for metric '{metric_name}'")

    if config.min_paired_queries and num_paired < config.min_paired_queries:
        raise ValueError(
            f"Only {num_paired} paired queries, but {config.min_paired_queries} required"
        )

    # Compute point estimate (mean delta)
    mean_delta = stats.mean(deltas) if deltas else 0.0

    # Deterministic seed
    seed = _deterministic_seed(deltas, config.random_seed)
    rng = Random(seed)

    # Bootstrap resampling
    bootstrap_means: list[float] = []
    for _ in range(config.num_resamples):
        # Resample with replacement
        resample = [rng.choice(deltas) for _ in range(num_paired)]
        resample_mean = stats.mean(resample)
        bootstrap_means.append(resample_mean)

    # Sort for percentile computation
    bootstrap_means.sort()

    # Compute CI from percentiles
    alpha = 1.0 - config.confidence_level
    lower_percentile = (alpha / 2.0) * 100.0
    upper_percentile = (1.0 - alpha / 2.0) * 100.0

    lower_ci = _percentile(bootstrap_means, lower_percentile)
    upper_ci = _percentile(bootstrap_means, upper_percentile)

    return BootstrapResult(
        metric_name=metric_name,
        num_paired_queries=num_paired,
        mean_delta=mean_delta,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        ci_level=config.confidence_level,
        num_resamples=config.num_resamples,
        seed=seed,
    )
