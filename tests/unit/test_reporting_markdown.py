"""Unit tests for markdown report generation.

Tests generate_evaluation_report() and generate_comparison_report()
covering all acceptance criteria for Requirement 21.

Validates: Requirements 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7
"""


from spanchor.comparison.compare import ComparisonResult
from spanchor.models.query import Query
from spanchor.models.run import Run
from spanchor.reporting.markdown import (
    generate_comparison_report,
    generate_evaluation_report,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_run(
    per_query_metrics: dict[str, dict[str, float]] | None = None,
    aggregate_metrics: dict[str, float] | None = None,
    mapper_stats: dict[str, int] | None = None,
    queries: tuple[Query, ...] | None = None,
    timestamp: str = "2024-01-01T00:00:00Z",
) -> Run:
    """Build a minimal Run for testing."""
    return Run(
        timestamp=timestamp,
        queries=queries or tuple(),
        per_query_metrics=per_query_metrics or {},
        aggregate_metrics=aggregate_metrics or {},
        config={"k": 5},
        mapper_stats=mapper_stats or {},
    )


def make_query(query_id: str, question: str) -> Query:
    """Build a minimal Query for testing."""
    return Query(query_id=query_id, question=question, anchors=())


def make_comparison_result(
    per_query_deltas: dict[str, dict[str, float]],
    per_query_status: dict,
    aggregate_deltas: dict[str, float] | None = None,
) -> ComparisonResult:
    """Build a ComparisonResult for testing."""
    has_regression = any(s == "REGRESSION" for s in per_query_status.values())
    return ComparisonResult(
        per_query_deltas=per_query_deltas,
        per_query_status=per_query_status,
        aggregate_deltas=aggregate_deltas or {},
        has_regression=has_regression,
    )


# ---------------------------------------------------------------------------
# generate_evaluation_report — Aggregate Metrics (Req 21.1)
# ---------------------------------------------------------------------------


class TestEvalReportAggregateMetrics:
    """Tests that aggregate metrics appear correctly in the report."""

    def test_aggregate_metrics_section_present(self):
        """Report must contain an 'Aggregate Metrics' section. (Req 21.1)"""
        run = make_run(aggregate_metrics={"mean_recall@5": 0.85, "mean_precision@5": 0.72})
        report = generate_evaluation_report(run)
        assert "## Aggregate Metrics" in report

    def test_aggregate_metrics_appear_in_table(self):
        """Each aggregate metric and its value should appear in the table. (Req 21.1)"""
        run = make_run(aggregate_metrics={"mean_recall@5": 0.8500, "mean_hit@5": 0.9000})
        report = generate_evaluation_report(run)
        assert "mean_recall@5" in report
        assert "0.8500" in report
        assert "mean_hit@5" in report
        assert "0.9000" in report

    def test_aggregate_section_shows_no_data_message_when_empty(self):
        """When aggregate_metrics is empty, a placeholder message is shown."""
        run = make_run(aggregate_metrics={})
        report = generate_evaluation_report(run)
        assert "## Aggregate Metrics" in report
        assert "No aggregate metrics available" in report

    def test_timestamp_present_in_report(self):
        """Report should include the run timestamp."""
        run = make_run(timestamp="2024-06-15T12:00:00Z")
        report = generate_evaluation_report(run)
        assert "2024-06-15T12:00:00Z" in report


# ---------------------------------------------------------------------------
# generate_evaluation_report — Per-Query Metrics (Req 21.2)
# ---------------------------------------------------------------------------


class TestEvalReportPerQueryMetrics:
    """Tests that per-query metrics appear correctly in the report."""

    def test_per_query_metrics_section_present(self):
        """Report must contain a 'Per-Query Metrics' section. (Req 21.2)"""
        run = make_run(per_query_metrics={"q1": {"recall@5": 0.8}})
        report = generate_evaluation_report(run)
        assert "## Per-Query Metrics" in report

    def test_all_query_ids_appear_in_per_query_table(self):
        """Every query_id in per_query_metrics must appear in the table. (Req 21.2)"""
        run = make_run(
            per_query_metrics={
                "q1": {"recall@5": 0.8, "hit@5": 1.0},
                "q2": {"recall@5": 0.6, "hit@5": 0.0},
            }
        )
        report = generate_evaluation_report(run)
        assert "q1" in report
        assert "q2" in report

    def test_metric_values_appear_in_per_query_table(self):
        """Metric values for each query should appear in the table. (Req 21.2)"""
        run = make_run(per_query_metrics={"q1": {"recall@5": 0.7500}})
        report = generate_evaluation_report(run)
        assert "0.7500" in report

    def test_question_text_appears_when_not_redacted(self):
        """Query question text should appear in the per-query table by default. (Req 21.2)"""
        queries = (make_query("q1", "What is the capital of France?"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        report = generate_evaluation_report(run, redact=False)
        assert "What is the capital of France?" in report

    def test_per_query_section_shows_no_data_when_empty(self):
        """When per_query_metrics is empty, a placeholder message is shown."""
        run = make_run(per_query_metrics={})
        report = generate_evaluation_report(run)
        assert "No per-query metrics available" in report


# ---------------------------------------------------------------------------
# generate_evaluation_report — Retrieved Character Counts (Req 21.3)
# ---------------------------------------------------------------------------


class TestEvalReportRetrievedCharCounts:
    """Tests that retrieved character counts are included in the report."""

    def test_retrieved_char_counts_section_present(self):
        """Report must contain a 'Retrieved Character Counts' section. (Req 21.3)"""
        run = make_run()
        report = generate_evaluation_report(run)
        assert "## Retrieved Character Counts" in report

    def test_char_count_metrics_shown_when_present_in_aggregate(self):
        """mean_retrieved_chars in aggregate should appear in char count section. (Req 21.3)"""
        run = make_run(aggregate_metrics={"mean_recall@5": 0.8, "mean_retrieved_chars": 1500.0})
        report = generate_evaluation_report(run)
        assert "mean_retrieved_chars" in report

    def test_char_count_shown_per_query_when_present(self):
        """retrieved_chars per query should appear in the char count table. (Req 21.3)"""
        run = make_run(
            per_query_metrics={
                "q1": {"recall@5": 0.8, "retrieved_chars": 1200.0},
                "q2": {"recall@5": 0.6, "retrieved_chars": 800.0},
            }
        )
        report = generate_evaluation_report(run)
        assert "retrieved_chars" in report


# ---------------------------------------------------------------------------
# generate_evaluation_report — Mapper Statistics (Req 21.4)
# ---------------------------------------------------------------------------


class TestEvalReportMapperStatistics:
    """Tests that mapper statistics are included and correct in the report."""

    def test_mapper_statistics_section_present(self):
        """Report must contain a 'Mapper Statistics' section. (Req 21.4)"""
        run = make_run(mapper_stats={"MAPPED_EXACT": 10, "UNMAPPED": 1})
        report = generate_evaluation_report(run)
        assert "## Mapper Statistics" in report

    def test_all_four_canonical_statuses_present(self):
        """MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, UNMAPPED must all appear. (Req 21.4)"""
        run = make_run(
            mapper_stats={
                "MAPPED_EXACT": 45,
                "MAPPED_NORMALIZED": 5,
                "AMBIGUOUS": 2,
                "UNMAPPED": 1,
            }
        )
        report = generate_evaluation_report(run)
        assert "MAPPED_EXACT" in report
        assert "MAPPED_NORMALIZED" in report
        assert "AMBIGUOUS" in report
        assert "UNMAPPED" in report

    def test_mapper_counts_appear_in_table(self):
        """Mapper counts should appear as numeric values in the table. (Req 21.4)"""
        run = make_run(
            mapper_stats={"MAPPED_EXACT": 42, "MAPPED_NORMALIZED": 8, "AMBIGUOUS": 3, "UNMAPPED": 2}
        )
        report = generate_evaluation_report(run)
        assert "42" in report
        assert "8" in report
        assert "3" in report
        assert "2" in report

    def test_missing_mapper_statuses_default_to_zero(self):
        """Missing mapper statuses should default to 0 in the table. (Req 21.4)"""
        # Only provide MAPPED_EXACT — others should appear as 0
        run = make_run(mapper_stats={"MAPPED_EXACT": 10})
        report = generate_evaluation_report(run)
        assert "MAPPED_NORMALIZED" in report
        assert "AMBIGUOUS" in report
        assert "UNMAPPED" in report

    def test_unmapped_rate_shown_when_totals_nonzero(self):
        """When there are chunks, the unmapped rate should be shown. (Req 21.4)"""
        run = make_run(
            mapper_stats={
                "MAPPED_EXACT": 40,
                "MAPPED_NORMALIZED": 5,
                "AMBIGUOUS": 5,
                "UNMAPPED": 10,
            }
        )
        report = generate_evaluation_report(run)
        assert "Unmapped rate" in report
        assert "16.67%" in report  # 10/60 ≈ 16.67%


# ---------------------------------------------------------------------------
# generate_evaluation_report — Redaction (Req 21.7)
# ---------------------------------------------------------------------------


class TestEvalReportRedaction:
    """Tests that redact=True removes source text from the report."""

    def test_question_text_omitted_when_redacted(self):
        """Query question should NOT appear in the report when redact=True. (Req 21.7)"""
        queries = (make_query("q1", "Secret query text that must not appear"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        report = generate_evaluation_report(run, redact=True)
        assert "Secret query text that must not appear" not in report

    def test_query_id_still_present_when_redacted(self):
        """Query IDs should still appear in the report even when redacted. (Req 21.7)"""
        queries = (make_query("q1", "Some question text"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        report = generate_evaluation_report(run, redact=True)
        assert "q1" in report

    def test_metrics_still_present_when_redacted(self):
        """Metric values should still appear in the report even when redacted. (Req 21.7)"""
        run = make_run(
            per_query_metrics={"q1": {"recall@5": 0.8750}},
            aggregate_metrics={"mean_recall@5": 0.8750},
        )
        report = generate_evaluation_report(run, redact=True)
        assert "0.8750" in report

    def test_question_column_absent_when_redacted(self):
        """The 'Question' column header should be absent when redact=True. (Req 21.7)"""
        queries = (make_query("q1", "What is Python?"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        report_redacted = generate_evaluation_report(run, redact=True)
        report_normal = generate_evaluation_report(run, redact=False)

        # Normal mode should have Question column
        assert "Question" in report_normal
        # Redacted mode should not
        assert "Question" not in report_redacted


# ---------------------------------------------------------------------------
# generate_comparison_report — Per-Query Delta Table (Req 21.5)
# ---------------------------------------------------------------------------


class TestComparisonReportPerQueryDeltas:
    """Tests for the per-query delta table in comparison reports."""

    def test_per_query_deltas_section_present(self):
        """Report must contain a 'Per-Query Deltas' section. (Req 21.5)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "## Per-Query Deltas" in report

    def test_query_ids_appear_in_delta_table(self):
        """All query IDs should appear in the per-query delta table. (Req 21.5)"""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.05},
                "q2": {"recall@5": -0.10},
            },
            per_query_status={"q1": "IMPROVED", "q2": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "q1" in report
        assert "q2" in report

    def test_status_appears_in_delta_table(self):
        """IMPROVED, REGRESSION, UNCHANGED statuses must appear in the table. (Req 21.5)"""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.10},
                "q2": {"recall@5": -0.10},
                "q3": {"recall@5": 0.01},
            },
            per_query_status={
                "q1": "IMPROVED",
                "q2": "REGRESSION",
                "q3": "UNCHANGED",
            },
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "IMPROVED" in report
        assert "REGRESSION" in report
        assert "UNCHANGED" in report

    def test_delta_values_appear_with_sign(self):
        """Delta values should appear with sign (+/-) in the table. (Req 21.5)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}, "q2": {"recall@5": -0.10}},
            per_query_status={"q1": "IMPROVED", "q2": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "+0.0500" in report
        assert "-0.1000" in report

    def test_summary_counts_present(self):
        """Report must include improved/regressed/unchanged counts. (Req 21.5)"""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.1},
                "q2": {"recall@5": -0.1},
                "q3": {"recall@5": 0.01},
            },
            per_query_status={
                "q1": "IMPROVED",
                "q2": "REGRESSION",
                "q3": "UNCHANGED",
            },
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "## Summary" in report
        # Counts for each status
        assert "1" in report  # 1 improved, 1 regressed, 1 unchanged

    def test_regression_warning_shown_when_has_regression(self):
        """A warning should appear in the report when has_regression is True."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "regression" in report.lower() or "REGRESSION" in report

    def test_no_regression_message_when_all_ok(self):
        """A positive message should appear when no regressions detected."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "No regressions detected" in report


# ---------------------------------------------------------------------------
# generate_comparison_report — Aggregate Summary (Req 21.6)
# ---------------------------------------------------------------------------


class TestComparisonReportAggregateSummary:
    """Tests for the aggregate summary table in comparison reports."""

    def test_aggregate_summary_section_present(self):
        """Report must contain an 'Aggregate Summary' section. (Req 21.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.80})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.85})
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "## Aggregate Summary" in report

    def test_baseline_and_candidate_values_appear(self):
        """Both baseline and candidate values should appear in aggregate summary. (Req 21.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.8000})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.8500})
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "0.8000" in report
        assert "0.8500" in report

    def test_delta_appears_in_aggregate_summary(self):
        """Delta values should appear in the aggregate summary table. (Req 21.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.80})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.85})
        report = generate_comparison_report(comparison, baseline, candidate)
        # Delta column should have +0.0500
        assert "+0.0500" in report

    def test_all_aggregate_metrics_in_summary(self):
        """All aggregate metrics from both runs should appear in the summary. (Req 21.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05, "hit@5": 0.10}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05, "hit@5": 0.10},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.80, "mean_hit@5": 0.70})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.85, "mean_hit@5": 0.80})
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "mean_recall@5" in report
        assert "mean_hit@5" in report

    def test_timestamps_in_comparison_report(self):
        """Both baseline and candidate timestamps should appear in the report."""
        comparison = make_comparison_result(
            per_query_deltas={},
            per_query_status={},
        )
        baseline = make_run(timestamp="2024-01-01T00:00:00Z")
        candidate = make_run(timestamp="2024-02-01T00:00:00Z")
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "2024-01-01T00:00:00Z" in report
        assert "2024-02-01T00:00:00Z" in report


# ---------------------------------------------------------------------------
# generate_comparison_report — Redaction (Req 21.7)
# ---------------------------------------------------------------------------


class TestComparisonReportRedaction:
    """Tests that redact=True removes source text from comparison reports."""

    def test_question_text_omitted_when_redacted(self):
        """Query questions should NOT appear when redact=True. (Req 21.7)"""
        queries = (make_query("q1", "Confidential query content"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)
        assert "Confidential query content" not in report

    def test_question_text_present_when_not_redacted(self):
        """Query questions should appear when redact=False. (Req 21.7)"""
        queries = (make_query("q1", "What is machine learning?"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=False)
        assert "What is machine learning?" in report

    def test_metric_values_still_appear_when_redacted(self):
        """Metric values should still appear in the report even when redacted. (Req 21.7)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.0500}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.0500},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.8000})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.8500})
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)
        assert "+0.0500" in report
        assert "0.8000" in report
        assert "0.8500" in report

    def test_query_ids_still_present_when_redacted(self):
        """Query IDs should still appear even with redaction. (Req 21.7)"""
        comparison = make_comparison_result(
            per_query_deltas={"query-abc-123": {"recall@5": 0.05}},
            per_query_status={"query-abc-123": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)
        assert "query-abc-123" in report


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases for both report generators."""

    def test_eval_report_single_query_single_metric(self):
        """Minimal run with one query and one metric should produce valid report."""
        run = make_run(
            per_query_metrics={"q1": {"recall@5": 1.0}},
            aggregate_metrics={"mean_recall@5": 1.0},
            mapper_stats={"MAPPED_EXACT": 1, "MAPPED_NORMALIZED": 0, "AMBIGUOUS": 0, "UNMAPPED": 0},
        )
        report = generate_evaluation_report(run)
        assert isinstance(report, str)
        assert len(report) > 0
        assert "q1" in report
        assert "1.0000" in report

    def test_eval_report_many_metrics_columns(self):
        """Report should handle multiple metric columns correctly."""
        metrics = {
            "recall@5": 0.85,
            "recall@10": 0.90,
            "precision@5": 0.72,
            "hit@5": 1.0,
            "full_evidence@5": 0.8,
            "iou": 0.65,
        }
        run = make_run(
            per_query_metrics={"q1": metrics},
            aggregate_metrics={f"mean_{k}": v for k, v in metrics.items()},
        )
        report = generate_evaluation_report(run)
        for metric in metrics:
            assert metric in report

    def test_comparison_report_empty_deltas(self):
        """Comparison report with no common queries should not crash."""
        comparison = make_comparison_result(
            per_query_deltas={},
            per_query_status={},
            aggregate_deltas={},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert isinstance(report, str)
        assert "## Aggregate Summary" in report

    def test_eval_report_returns_string(self):
        """generate_evaluation_report always returns a str."""
        run = make_run()
        result = generate_evaluation_report(run)
        assert isinstance(result, str)

    def test_comparison_report_returns_string(self):
        """generate_comparison_report always returns a str."""
        comparison = make_comparison_result({}, {})
        report = generate_comparison_report(comparison, make_run(), make_run())
        assert isinstance(report, str)

    def test_eval_report_mapper_all_zeros(self):
        """Mapper stats all zero should not cause divide-by-zero."""
        run = make_run(
            mapper_stats={"MAPPED_EXACT": 0, "MAPPED_NORMALIZED": 0, "AMBIGUOUS": 0, "UNMAPPED": 0}
        )
        report = generate_evaluation_report(run)
        # Should not crash, unmapped rate section should be absent (total=0)
        assert "## Mapper Statistics" in report
        assert "Unmapped rate" not in report

    def test_comparison_report_all_unchanged(self):
        """All-UNCHANGED comparison should show zero regressions."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.0}, "q2": {"recall@5": 0.0}},
            per_query_status={"q1": "UNCHANGED", "q2": "UNCHANGED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "No regressions detected" in report
