"""JSON report generation for evaluation and comparison results.

Generates machine-readable JSON reports for:
- Evaluation runs: aggregate metrics, per-query metrics, configuration, mapper stats
- Comparison results: per-query deltas/statuses, aggregate deltas, regression flag

Supports redaction mode to omit source text (query question text) for privacy.

Validates: Requirements 22.1, 22.2, 22.3, 22.4, 22.5, 22.6
"""

from spanchor.comparison.compare import ComparisonResult
from spanchor.models.run import Run


def generate_evaluation_json(run: Run, redact: bool = False) -> dict[str, object]:
    """Generate a machine-readable JSON dict from an evaluation Run.

    The returned dict includes:
    - All aggregate metrics (Req 22.1)
    - All per-query metrics (Req 22.2)
    - Configuration parameters (Req 22.3)
    - Mapper statistics
    - Evaluation timestamp
    - Schema version

    If redact=True, the query ``question`` field is omitted from the
    per-query section so source text is never exposed in the output (Req 22.6).

    Args:
        run: The evaluation Run containing metrics and statistics.
        redact: If True, omit source text (question text) from the output.

    Returns:
        A dict suitable for serialisation with ``json.dumps``.

    Validates: Requirements 22.1, 22.2, 22.3, 22.6
    """
    # Build per-query section, optionally including question text
    per_query: dict[str, dict[str, object]] = {}
    # Build a quick lookup so we can include question text when not redacting
    query_map: dict[str, str] = {q.query_id: q.question for q in run.queries}

    for query_id, metrics in run.per_query_metrics.items():
        entry: dict[str, object] = {"metrics": dict(metrics)}
        if not redact:
            question = query_map.get(query_id)
            if question is not None:
                entry["question"] = question
        per_query[query_id] = entry

    return {
        "schema_version": run.schema_version,
        "timestamp": run.timestamp,
        "config": dict(run.config),
        "aggregate_metrics": dict(run.aggregate_metrics),
        "per_query_metrics": per_query,
        "mapper_stats": dict(run.mapper_stats),
    }


def generate_comparison_json(
    comparison: ComparisonResult,
    baseline: Run,
    candidate: Run,
    redact: bool = False,
) -> dict[str, object]:
    """Generate a machine-readable JSON dict from a ComparisonResult.

    The returned dict includes:
    - Per-query deltas and statuses (Req 22.4)
    - Aggregate deltas (Req 22.5)
    - has_regression flag
    - Baseline and candidate timestamps / configs
    - Schema versions for both runs

    If redact=True, query question text is omitted from the per-query
    entries so source text is never exposed in the output (Req 22.6).

    Args:
        comparison: The ComparisonResult from comparing two runs.
        baseline: The baseline Run used as reference.
        candidate: The candidate Run being evaluated.
        redact: If True, omit source text (question text) from the output.

    Returns:
        A dict suitable for serialisation with ``json.dumps``.

    Validates: Requirements 22.4, 22.5, 22.6
    """
    # Build a question lookup from both runs (baseline takes priority)
    query_map: dict[str, str] = {}
    if not redact:
        for query in candidate.queries:
            query_map[query.query_id] = query.question
        # baseline overwrites candidate for shared queries
        for query in baseline.queries:
            query_map[query.query_id] = query.question

    # Build the per-query section combining deltas and status
    per_query: dict[str, dict[str, object]] = {}
    for query_id, deltas in comparison.per_query_deltas.items():
        entry: dict[str, object] = {
            "status": comparison.per_query_status.get(query_id, "UNCHANGED"),
            "deltas": dict(deltas),
        }
        if not redact:
            question = query_map.get(query_id)
            if question is not None:
                entry["question"] = question
        per_query[query_id] = entry

    return {
        "has_regression": comparison.has_regression,
        "aggregate_deltas": dict(comparison.aggregate_deltas),
        "per_query": per_query,
        "baseline": {
            "schema_version": baseline.schema_version,
            "timestamp": baseline.timestamp,
            "config": dict(baseline.config),
        },
        "candidate": {
            "schema_version": candidate.schema_version,
            "timestamp": candidate.timestamp,
            "config": dict(candidate.config),
        },
    }
