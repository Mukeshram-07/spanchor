"""Markdown report generation for evaluation and comparison results.

Generates human-readable markdown reports with tables for:
- Aggregate metrics
- Per-query metrics
- Retrieved character counts
- Mapper statistics
- Comparison deltas with regression statuses

Supports redaction mode to omit source text for privacy.
"""

from spanchor.comparison.compare import ComparisonResult
from spanchor.models.run import Run


def _fmt(value: float) -> str:
    """Format a float value for display in tables."""
    return f"{value:.4f}"


def _fmt_delta(value: float) -> str:
    """Format a delta value with sign for display in comparison tables."""
    if value > 0:
        return f"+{value:.4f}"
    return f"{value:.4f}"


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a markdown table string.

    Args:
        headers: Column header names.
        rows: List of rows, each row a list of string values (same length as headers).

    Returns:
        A markdown table as a string (without trailing newline).
    """
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def _fmt_row(cells: list[str]) -> str:
        parts = [f" {cell:<{col_widths[i]}} " for i, cell in enumerate(cells)]
        return "|" + "|".join(parts) + "|"

    separator_parts = ["-" * (col_widths[i] + 2) for i in range(len(headers))]
    separator = "|" + "|".join(separator_parts) + "|"

    lines = [_fmt_row(headers), separator]
    for row in rows:
        lines.append(_fmt_row(row))
    return "\n".join(lines)


def generate_evaluation_report(run: Run, redact: bool = False) -> str:
    """Generate a markdown evaluation report from a Run.

    The report includes:
    - Aggregate metrics table (all mean_* metrics)
    - Per-query metrics table (all queries with their individual metrics)
    - Retrieved character counts per query
    - Mapper statistics table (MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, UNMAPPED)

    If redact=True, source text (query questions) is omitted from the report.

    Args:
        run: The evaluation Run containing metrics and statistics.
        redact: If True, omit source text (question text) from the report.

    Returns:
        A markdown string representing the evaluation report.

    Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.7
    """
    sections: list[str] = []

    sections.append("# Evaluation Report\n")
    sections.append(f"**Timestamp:** {run.timestamp}\n")

    # -------------------------------------------------------------------
    # 1. Aggregate Metrics Table (Req 21.1)
    # -------------------------------------------------------------------
    sections.append("## Aggregate Metrics\n")

    agg_metrics = dict(run.aggregate_metrics.items())
    if agg_metrics:
        headers = ["Metric", "Value"]
        rows = [[metric, _fmt(value)] for metric, value in sorted(agg_metrics.items())]
        sections.append(_md_table(headers, rows))
    else:
        sections.append("*No aggregate metrics available.*")

    sections.append("")

    # -------------------------------------------------------------------
    # 2. Per-Query Metrics Table (Req 21.2) + Retrieved Char Counts (Req 21.3)
    # -------------------------------------------------------------------
    sections.append("## Per-Query Metrics\n")

    per_query = run.per_query_metrics
    if per_query:
        # Collect all metric names across all queries (sorted for stable output)
        all_metric_names = sorted(
            {metric for q_metrics in per_query.values() for metric in q_metrics}
        )

        # Build a lookup from query_id -> question for non-redacted mode
        query_map: dict[str, str] = {}
        if not redact:
            for query in run.queries:
                query_map[query.query_id] = query.question

        if redact:
            headers = ["Query ID"] + all_metric_names
        else:
            headers = ["Query ID", "Question"] + all_metric_names

        rows = []
        for qid in sorted(per_query.keys()):
            q_metrics = per_query[qid]
            metric_values = [
                _fmt(q_metrics[m]) if m in q_metrics else "N/A" for m in all_metric_names
            ]
            if redact:
                row = [qid] + metric_values
            else:
                question = query_map.get(qid, "")
                row = [qid, question] + metric_values
            rows.append(row)

        sections.append(_md_table(headers, rows))
    else:
        sections.append("*No per-query metrics available.*")

    sections.append("")

    # -------------------------------------------------------------------
    # 3. Retrieved Character Counts (Req 21.3)
    # -------------------------------------------------------------------
    sections.append("## Retrieved Character Counts\n")

    # Look for retrieved_chars or retrieved_char_count metrics in per_query
    char_count_keys = [
        k
        for k in (next(iter(per_query.values()), {}).keys() if per_query else [])
        if "char" in k.lower() or "retrieved" in k.lower()
    ]

    # Also check aggregate metrics for mean_retrieved_chars
    mean_chars_keys = [k for k in run.aggregate_metrics if "char" in k.lower()]

    if char_count_keys and per_query:
        headers = ["Query ID"] + char_count_keys
        rows = []
        for qid in sorted(per_query.keys()):
            q_metrics = per_query[qid]
            values = [str(int(q_metrics[k])) if k in q_metrics else "N/A" for k in char_count_keys]
            rows.append([qid] + values)
        sections.append(_md_table(headers, rows))
    elif mean_chars_keys:
        headers = ["Metric", "Value"]
        rows = [[k, _fmt(run.aggregate_metrics[k])] for k in sorted(mean_chars_keys)]
        sections.append(_md_table(headers, rows))
    else:
        # Show all aggregate metrics that look like counts
        count_metrics = {
            k: v for k, v in run.aggregate_metrics.items() if "chars" in k or "count" in k
        }
        if count_metrics:
            headers = ["Metric", "Value"]
            rows = [[k, str(v)] for k, v in sorted(count_metrics.items())]
            sections.append(_md_table(headers, rows))
        else:
            sections.append("*No retrieved character count data available.*")

    sections.append("")

    # -------------------------------------------------------------------
    # 4. Mapper Statistics Table (Req 21.4)
    # -------------------------------------------------------------------
    sections.append("## Mapper Statistics\n")

    mapper_stats = run.mapper_stats
    # Show all four canonical statuses, defaulting to 0 if absent
    canonical_statuses = ["MAPPED_EXACT", "MAPPED_NORMALIZED", "AMBIGUOUS", "UNMAPPED"]

    stats_to_show: dict[str, int] = {}
    for status in canonical_statuses:
        stats_to_show[status] = mapper_stats.get(status, 0)

    # Also include any other stats present in mapper_stats
    for key, value in mapper_stats.items():
        if key not in stats_to_show:
            stats_to_show[key] = value

    headers = ["Status", "Count"]
    rows = [[status, str(count)] for status, count in stats_to_show.items()]
    sections.append(_md_table(headers, rows))

    total = sum(stats_to_show.values())
    unmapped = stats_to_show.get("UNMAPPED", 0)
    if total > 0:
        unmapped_rate = unmapped / total
        sections.append(f"\n**Total chunks mapped:** {total}")
        sections.append(f"**Unmapped rate:** {unmapped_rate:.2%}")

    sections.append("")

    return "\n".join(sections)


def generate_comparison_report(
    comparison: ComparisonResult,
    baseline: Run,
    candidate: Run,
    redact: bool = False,
    policy: dict[str, float] | None = None,
) -> str:
    """Generate a markdown comparison report between two evaluation runs.

    The report includes:
    - Summary counts (improved / regressed / unchanged)
    - Per-query delta table with IMPROVED/REGRESSION/UNCHANGED statuses
    - Aggregate summary table with baseline, candidate, and delta values
    - Optional: Regressions section with severity and policy thresholds (Feature 8.2)
    - Optional: Improvements section (Feature 8.2)
    - Optional: Bootstrap confidence intervals (Feature 8.1)

    If redact=True, source text (query questions) is omitted from the report.

    Args:
        comparison: The ComparisonResult from comparing two runs.
        baseline: The baseline Run used as reference.
        candidate: The candidate Run being evaluated.
        redact: If True, omit source text (question text) from the report.
        policy: Optional per-metric policy thresholds used during comparison.
            When provided, threshold violations are displayed for regressions.
            Example: {"recall@5": 0.05, "hit@5": 0.10}
            If None, only actual deltas are shown (backward compatible).

    Returns:
        A markdown string representing the comparison report.

    Validates: Requirements 21.5, 21.6, 21.7, 23.2 (with policy)
    """
    sections: list[str] = []

    sections.append("# Comparison Report\n")
    sections.append(f"**Baseline timestamp:** {baseline.timestamp}")
    sections.append(f"**Candidate timestamp:** {candidate.timestamp}\n")

    # -------------------------------------------------------------------
    # 1. Summary Counts (Req 21.5 — part of per-query delta section)
    # -------------------------------------------------------------------
    improved = sum(1 for s in comparison.per_query_status.values() if s == "IMPROVED")
    regressed = sum(1 for s in comparison.per_query_status.values() if s == "REGRESSION")
    unchanged = sum(1 for s in comparison.per_query_status.values() if s == "UNCHANGED")
    total_queries = len(comparison.per_query_status)

    sections.append("## Summary\n")
    sections.append("| Status | Count |")
    sections.append("|--------|-------|")
    sections.append(f"| ✅ IMPROVED | {improved} |")
    sections.append(f"| ❌ REGRESSION | {regressed} |")
    sections.append(f"| — UNCHANGED | {unchanged} |")
    sections.append(f"| **Total** | **{total_queries}** |")
    sections.append("")

    if comparison.has_regression:
        sections.append(f"> ⚠️ **{regressed} regression(s) detected.**\n")
    else:
        sections.append("> ✅ **No regressions detected.**\n")

    # -------------------------------------------------------------------
    # 2. Per-Query Delta Table (Req 21.5)
    # -------------------------------------------------------------------
    sections.append("## Per-Query Deltas\n")

    per_query_deltas = comparison.per_query_deltas
    per_query_status = comparison.per_query_status

    if per_query_deltas:
        # Collect all metric names that appear in any query's deltas
        all_metric_names = sorted(
            {metric for q_deltas in per_query_deltas.values() for metric in q_deltas}
        )

        # Build query_id -> question lookup for non-redacted mode
        query_map: dict[str, str] = {}
        if not redact:
            for query in baseline.queries:
                query_map[query.query_id] = query.question
            # Also check candidate for any queries only in candidate
            for query in candidate.queries:
                if query.query_id not in query_map:
                    query_map[query.query_id] = query.question

        delta_headers = [f"{m} Δ" for m in all_metric_names]
        if redact:
            headers = ["Query ID", "Status"] + delta_headers
        else:
            headers = ["Query ID", "Question", "Status"] + delta_headers

        rows = []
        for qid in sorted(per_query_deltas.keys()):
            q_deltas = per_query_deltas[qid]
            status = per_query_status.get(qid, "UNCHANGED")
            delta_values = [
                _fmt_delta(q_deltas[m]) if m in q_deltas else "N/A" for m in all_metric_names
            ]
            if redact:
                row = [qid, status] + delta_values
            else:
                question = query_map.get(qid, "")
                row = [qid, question, status] + delta_values
            rows.append(row)

        sections.append(_md_table(headers, rows))
    else:
        sections.append("*No per-query delta data available.*")

    sections.append("")

    # -------------------------------------------------------------------
    # 3. Aggregate Summary Table (Req 21.6)
    # -------------------------------------------------------------------
    sections.append("## Aggregate Summary\n")

    aggregate_deltas = comparison.aggregate_deltas
    if aggregate_deltas:
        # Collect all aggregate metric names from both runs
        all_agg_metrics = sorted(set(baseline.aggregate_metrics) | set(candidate.aggregate_metrics))

        headers = ["Metric", "Baseline", "Candidate", "Delta"]
        rows = []
        for metric in all_agg_metrics:
            baseline_val = baseline.aggregate_metrics.get(metric)
            candidate_val = candidate.aggregate_metrics.get(metric)

            baseline_str = _fmt(baseline_val) if baseline_val is not None else "N/A"
            candidate_str = _fmt(candidate_val) if candidate_val is not None else "N/A"

            # Map mean_* metric name to corresponding delta key
            # aggregate_deltas uses non-prefixed metric names (e.g., "recall@5")
            # while aggregate_metrics uses "mean_recall@5"
            delta_key = metric
            if metric.startswith("mean_"):
                delta_key = metric[len("mean_") :]

            delta_val = aggregate_deltas.get(delta_key)
            delta_str = _fmt_delta(delta_val) if delta_val is not None else "N/A"

            rows.append([metric, baseline_str, candidate_str, delta_str])

        sections.append(_md_table(headers, rows))
    else:
        # Fallback: show baseline vs candidate without deltas
        all_agg_metrics = sorted(set(baseline.aggregate_metrics) | set(candidate.aggregate_metrics))
        if all_agg_metrics:
            headers = ["Metric", "Baseline", "Candidate"]
            rows = []
            for metric in all_agg_metrics:
                b = baseline.aggregate_metrics.get(metric)
                c = candidate.aggregate_metrics.get(metric)
                rows.append(
                    [
                        metric,
                        _fmt(b) if b is not None else "N/A",
                        _fmt(c) if c is not None else "N/A",
                    ]
                )
            sections.append(_md_table(headers, rows))
        else:
            sections.append("*No aggregate metrics available.*")

    sections.append("")

    # -------------------------------------------------------------------
    # 4. Regression Grouping (Feature 8.2, optional)
    # -------------------------------------------------------------------
    regressed_queries = [qid for qid, status in per_query_status.items() if status == "REGRESSION"]
    if regressed_queries:
        sections.append("## Regressions (Sorted by Severity)\n")

        # Build query_id -> question lookup for non-redacted mode
        query_map_regs: dict[str, str] = {}
        if not redact:
            for query in baseline.queries:
                query_map_regs[query.query_id] = query.question
            for query in candidate.queries:
                if query.query_id not in query_map_regs:
                    query_map_regs[query.query_id] = query.question

        # Collect all metric names
        all_metric_names_regs = sorted(
            {metric for q_deltas in per_query_deltas.values() for metric in q_deltas}
        )

        # Compute severity (sum of absolute negative deltas) for each regressed query
        severity_map: dict[str, float] = {}
        for qid in regressed_queries:
            q_deltas = per_query_deltas[qid]
            total_violation = 0.0
            for metric, delta in q_deltas.items():
                if delta < 0:
                    # Sum of magnitudes of all negative deltas (drops)
                    total_violation += abs(delta)
            severity_map[qid] = total_violation

        # Sort by severity (largest violations first)
        sorted_regressed = sorted(
            regressed_queries,
            key=lambda qid: severity_map[qid],
            reverse=True,
        )

        # Build table — include policy threshold if available
        delta_headers_regs = [f"{m} Δ" for m in all_metric_names_regs]
        if policy:
            # When policy available, show threshold and actual delta for failed metrics
            threshold_headers = [f"{m} Threshold" for m in all_metric_names_regs]
            if redact:
                headers_regs = ["Query ID", "Severity"] + threshold_headers + delta_headers_regs
            else:
                headers_regs = (
                    ["Query ID", "Question", "Severity"] + threshold_headers + delta_headers_regs
                )
        else:
            # Without policy, show only actual deltas (backward compatible)
            if redact:
                headers_regs = ["Query ID", "Severity"] + delta_headers_regs
            else:
                headers_regs = ["Query ID", "Question", "Severity"] + delta_headers_regs

        rows_regs: list[list[str]] = []
        for qid in sorted_regressed:
            q_deltas = per_query_deltas[qid]
            severity_val: float = severity_map[qid]

            # Build delta and threshold values
            threshold_cols: list[str] = []
            delta_cols: list[str] = []
            for m in all_metric_names_regs:
                delta_val = q_deltas.get(m)

                # Threshold column (when policy available)
                if policy is not None:
                    threshold_val: float | None = policy.get(m)
                    if threshold_val is not None:
                        threshold_cols.append(_fmt(threshold_val))
                    else:
                        threshold_cols.append("N/A")

                # Delta column
                if delta_val is not None:
                    delta_cols.append(_fmt_delta(delta_val))
                else:
                    delta_cols.append("N/A")

            # Build row with consistent list type
            row_cols: list[str] = []
            if redact:
                row_cols.append(qid)
            else:
                row_cols.append(qid)
                row_cols.append(query_map_regs.get(qid, ""))

            row_cols.append(_fmt(severity_val))

            if policy is not None:
                row_cols.extend(threshold_cols)

            row_cols.extend(delta_cols)
            rows_regs.append(row_cols)

        sections.append(_md_table(headers_regs, rows_regs))
        sections.append("")

    # -------------------------------------------------------------------
    # 5. Improvement Grouping (Feature 8.2, optional)
    # -------------------------------------------------------------------
    improved_queries = [qid for qid, status in per_query_status.items() if status == "IMPROVED"]
    if improved_queries:
        sections.append("## Improvements (Sorted by Impact)\n")

        # Build query_id -> question lookup for non-redacted mode
        query_map_imps: dict[str, str] = {}
        if not redact:
            for query in baseline.queries:
                query_map_imps[query.query_id] = query.question
            for query in candidate.queries:
                if query.query_id not in query_map_imps:
                    query_map_imps[query.query_id] = query.question

        # Collect all metric names
        all_metric_names_imps = sorted(
            {metric for q_deltas in per_query_deltas.values() for metric in q_deltas}
        )

        # Compute impact (sum of positive deltas) for each improved query
        impact_map: dict[str, float] = {}
        for qid in improved_queries:
            q_deltas = per_query_deltas[qid]
            total_improvement = 0.0
            for metric, delta in q_deltas.items():
                if delta > 0:
                    total_improvement += delta
            impact_map[qid] = total_improvement

        # Sort by impact (largest improvements first)
        sorted_improved = sorted(
            improved_queries,
            key=lambda qid: impact_map[qid],
            reverse=True,
        )

        # Build table
        delta_headers_imps = [f"{m} Δ" for m in all_metric_names_imps]
        if redact:
            headers_imps = ["Query ID", "Impact"] + delta_headers_imps
        else:
            headers_imps = ["Query ID", "Question", "Impact"] + delta_headers_imps

        rows_imps = []
        for qid in sorted_improved:
            q_deltas = per_query_deltas[qid]
            impact = impact_map[qid]
            delta_values = [
                _fmt_delta(q_deltas[m]) if m in q_deltas else "N/A" for m in all_metric_names_imps
            ]
            if redact:
                row = [qid, _fmt(impact)] + delta_values
            else:
                question = query_map_imps.get(qid, "")
                row = [qid, question, _fmt(impact)] + delta_values
            rows_imps.append(row)

        sections.append(_md_table(headers_imps, rows_imps))
        sections.append("")

    # -------------------------------------------------------------------
    # 6. Set-wise Metrics (Feature 8.3, optional)
    # -------------------------------------------------------------------
    if comparison.setwise_aggregate_deltas:
        sections.append("## Set-wise Metrics\n")

        # Aggregate set-wise deltas table
        aggregate_setwise = comparison.setwise_aggregate_deltas
        if aggregate_setwise:
            setwise_headers = ["Metric", "Baseline", "Candidate", "Delta"]
            setwise_rows = []

            # Display aggregate set-wise deltas.
            # Note: We only have deltas in the comparison result, not the original
            # baseline/candidate values, so we show "N/A" for those columns.
            for metric_name in sorted(aggregate_setwise.keys()):
                delta_val = aggregate_setwise[metric_name]
                setwise_rows.append([metric_name, "N/A", "N/A", _fmt_delta(delta_val)])

            sections.append(_md_table(setwise_headers, setwise_rows))
            sections.append("")

        # Per-query set-wise changes (show queries with significant changes: |delta| > 0.01)
        if comparison.setwise_deltas:
            significant_queries = []
            for qid, q_deltas in comparison.setwise_deltas.items():
                for metric, delta in q_deltas.items():
                    if abs(delta) > 0.01:
                        significant_queries.append(qid)
                        break

            if significant_queries:
                sections.append("### Per-Query Set-wise Changes\n")

                # Build query_id -> question lookup for non-redacted mode
                query_map_setwise: dict[str, str] = {}
                if not redact:
                    for query in baseline.queries:
                        query_map_setwise[query.query_id] = query.question
                    for query in candidate.queries:
                        if query.query_id not in query_map_setwise:
                            query_map_setwise[query.query_id] = query.question

                # Collect all setwise metric names
                all_setwise_metrics = sorted(
                    {
                        metric
                        for q_deltas in comparison.setwise_deltas.values()
                        for metric in q_deltas
                    }
                )

                setwise_delta_headers = [f"{m} Δ" for m in all_setwise_metrics]
                if redact:
                    per_query_headers_setwise = ["Query ID"] + setwise_delta_headers
                else:
                    per_query_headers_setwise = ["Query ID", "Question"] + setwise_delta_headers

                per_query_rows_setwise = []
                for qid in sorted(significant_queries):
                    q_deltas = comparison.setwise_deltas[qid]
                    delta_values = [
                        _fmt_delta(q_deltas[m]) if m in q_deltas else "N/A"
                        for m in all_setwise_metrics
                    ]
                    if redact:
                        row = [qid] + delta_values
                    else:
                        question = query_map_setwise.get(qid, "")
                        row = [qid, question] + delta_values
                    per_query_rows_setwise.append(row)

                sections.append(_md_table(per_query_headers_setwise, per_query_rows_setwise))
                sections.append("")

    # -------------------------------------------------------------------
    # 7. Aggregate Confidence Intervals (Feature 8.1, optional)
    # -------------------------------------------------------------------
    if comparison.statistics_enabled and comparison.bootstrap_results:
        sections.append("## Aggregate Confidence Intervals\n")
        sections.append(
            f"*(Statistical analysis on {comparison.num_paired_queries} "
            f"paired queries, 95% confidence level)*\n"
        )

        bootstrap_results = comparison.bootstrap_results
        ci_headers = ["Metric", "Mean Δ", "Lower CI", "Upper CI"]
        ci_rows = []

        for metric_name in sorted(bootstrap_results.keys()):
            result = bootstrap_results[metric_name]
            ci_rows.append(
                [
                    metric_name,
                    _fmt(result.mean_delta),
                    _fmt(result.lower_ci),
                    _fmt(result.upper_ci),
                ]
            )

        sections.append(_md_table(ci_headers, ci_rows))
        sections.append("")

    return "\n".join(sections)
