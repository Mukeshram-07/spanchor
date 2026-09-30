"""Pytest integration helper for spanchor regression testing.

Provides assert_no_regression() for use in test suites to assert that a
candidate retrieval run does not regress against a baseline run.

Requirements: 23.1, 23.2, 23.3, 23.4, 23.5

Example::

    from spanchor.testing import assert_no_regression

    def test_retrieval_does_not_regress(baseline_run, candidate_run):
        assert_no_regression(
            baseline=baseline_run,
            candidate=candidate_run,
            policy={"recall@5": 0.05, "hit@5": 0.10},
        )
"""

from __future__ import annotations

from spanchor.comparison.compare import compare
from spanchor.models.run import Run


def assert_no_regression(
    baseline: Run,
    candidate: Run,
    policy: dict[str, float],
    min_query_count: int | None = None,
) -> None:
    """Assert that the candidate run does not regress against the baseline.

    Compares *baseline* against *candidate* using the given *policy* thresholds.
    If any query is classified as REGRESSION, raises :class:`AssertionError`
    with a detailed message listing the regressed queries, metrics, values, and
    thresholds.

    Passes silently when all queries are UNCHANGED or IMPROVED (req 23.4).

    Args:
        baseline: The baseline :class:`~spanchor.models.run.Run` to compare against.
        candidate: The candidate :class:`~spanchor.models.run.Run` being evaluated.
        policy: Per-metric max_drop thresholds.
            Example: ``{"recall@5": 0.05, "hit@5": 0.10}``.
            A query is a REGRESSION when any policy metric drops by more than
            the configured threshold.
        min_query_count: Optional minimum number of common queries required.
            Passed through to :func:`~spanchor.comparison.compare.compare`.

    Raises:
        AssertionError: If any query shows REGRESSION status (req 23.3).
            The message includes query_id, metric name, baseline value,
            candidate value, and delta for each regression (req 23.5).
        :class:`~spanchor.errors.ComparisonError`: If the runs share no common
            queries or ``min_query_count`` is not met.

    Example::

        assert_no_regression(
            baseline=baseline_run,
            candidate=candidate_run,
            policy={"recall@5": 0.05},
        )
    """
    result = compare(
        baseline=baseline,
        candidate=candidate,
        policy=policy,
        min_query_count=min_query_count,
    )

    # Req 23.4 – pass silently when no regressions
    if not result.has_regression:
        return

    # Req 23.3, 23.5 – build detailed failure message
    regressed_query_ids = [
        qid for qid, status in result.per_query_status.items() if status == "REGRESSION"
    ]

    details: list[str] = []
    for qid in regressed_query_ids:
        deltas = result.per_query_deltas.get(qid, {})
        baseline_metrics = baseline.per_query_metrics.get(qid, {})
        candidate_metrics = candidate.per_query_metrics.get(qid, {})

        for metric, delta in sorted(deltas.items()):
            threshold = policy.get(metric)
            if threshold is None:
                continue
            # Only report metrics that actually triggered the regression
            if delta >= -threshold:
                continue

            baseline_val = baseline_metrics.get(metric, float("nan"))
            candidate_val = candidate_metrics.get(metric, float("nan"))

            # Req 23.5: include query_id, metric, baseline, candidate, delta
            details.append(
                f"  {qid}: {metric} "
                f"baseline={baseline_val:.4f} → candidate={candidate_val:.4f} "
                f"(delta={delta:+.4f}, threshold=-{threshold:.4f})"
            )

    n = len(regressed_query_ids)
    failure_message = (
        f"Regression detected in {n} quer{'y' if n == 1 else 'ies'}:\n" + "\n".join(details)
    )

    raise AssertionError(failure_message)
