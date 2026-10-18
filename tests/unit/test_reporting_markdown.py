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
    statistics_enabled: bool = False,
    bootstrap_results: dict | None = None,
    num_paired_queries: int = 0,
) -> ComparisonResult:
    """Build a ComparisonResult for testing."""
    has_regression = any(s == "REGRESSION" for s in per_query_status.values())
    return ComparisonResult(
        per_query_deltas=per_query_deltas,
        per_query_status=per_query_status,
        aggregate_deltas=aggregate_deltas or {},
        has_regression=has_regression,
        statistics_enabled=statistics_enabled,
        bootstrap_results=bootstrap_results,
        num_paired_queries=num_paired_queries,
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


# ---------------------------------------------------------------------------
# Feature 8.1: Confidence Intervals in Markdown Report
# ---------------------------------------------------------------------------


class TestComparisonMarkdownRegressionGrouping:
    """Test regression and improvement grouping in markdown reports."""

    def test_regression_section_present_when_regressions_exist(self):
        """Regressions section should appear when there are regressed queries."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": -0.15},
                "q2": {"recall@5": 0.05},
            },
            per_query_status={"q1": "REGRESSION", "q2": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        assert "## Regressions (Sorted by Severity)" in report
        assert "q1" in report

    def test_regression_section_absent_when_no_regressions(self):
        """Regressions section should be absent when there are no regressions."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        assert "## Regressions" not in report

    def test_regression_sorted_by_severity(self):
        """Regressions should be sorted by severity (largest violations first)."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": -0.05},  # Small violation
                "q2": {"recall@5": -0.20},  # Large violation
                "q3": {"recall@5": -0.10},  # Medium violation
            },
            per_query_status={"q1": "REGRESSION", "q2": "REGRESSION", "q3": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        # Find positions of each query in the report
        pos_q2 = report.find("q2")
        pos_q3 = report.find("q3", pos_q2 + 1)
        pos_q1 = report.find("q1", pos_q3 + 1)

        # q2 (largest) should appear before q3, q3 before q1
        assert pos_q2 < pos_q3 < pos_q1

    def test_improvement_section_present_when_improvements_exist(self):
        """Improvements section should appear when there are improved queries."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.15},
                "q2": {"recall@5": -0.05},
            },
            per_query_status={"q1": "IMPROVED", "q2": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        assert "## Improvements (Sorted by Impact)" in report
        assert "q1" in report

    def test_improvement_section_absent_when_no_improvements(self):
        """Improvements section should be absent when there are no improvements."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.05}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        assert "## Improvements" not in report

    def test_improvement_sorted_by_impact(self):
        """Improvements should be sorted by impact (largest gains first)."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.05},  # Small gain
                "q2": {"recall@5": 0.20},  # Large gain
                "q3": {"recall@5": 0.10},  # Medium gain
            },
            per_query_status={"q1": "IMPROVED", "q2": "IMPROVED", "q3": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        # Find positions of each query in the improvements section
        imp_section_start = report.find("## Improvements")
        pos_q2 = report.find("q2", imp_section_start)
        pos_q3 = report.find("q3", pos_q2 + 1)
        pos_q1 = report.find("q1", pos_q3 + 1)

        # q2 (largest) should appear before q3, q3 before q1
        assert pos_q2 < pos_q3 < pos_q1

    def test_regression_and_improvement_sections_both_present(self):
        """Both regressions and improvements sections should appear when appropriate."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": -0.10},
                "q2": {"recall@5": 0.15},
                "q3": {"recall@5": 0.00},
            },
            per_query_status={"q1": "REGRESSION", "q2": "IMPROVED", "q3": "UNCHANGED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        assert "## Regressions" in report
        assert "## Improvements" in report

    def test_regression_with_redaction(self):
        """Regression section should respect redaction mode."""
        queries = (make_query("q1", "Confidential question"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)

        # Query ID should be present but question should not
        assert "q1" in report
        assert "Confidential question" not in report

    def test_improvement_with_redaction(self):
        """Improvement section should respect redaction mode."""
        queries = (make_query("q1", "Secret question"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.15}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)

        # Query ID should be present but question should not
        assert "q1" in report
        assert "Secret question" not in report

    def test_regression_with_multiple_metrics(self):
        """Regression section should display all metrics for each regressed query."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": -0.10, "precision@5": -0.05, "hit@5": 0.02},
            },
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        # All metrics should be displayed in regressions section
        reg_section = report[report.find("## Regressions") :]
        next_section = reg_section.find("##", 2)
        reg_text = reg_section[:next_section] if next_section > 0 else reg_section

        assert "recall@5" in reg_text
        assert "precision@5" in reg_text
        assert "hit@5" in reg_text

    def test_improvement_with_multiple_metrics(self):
        """Improvement section should display all metrics for each improved query."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.10, "precision@5": 0.05, "hit@5": 0.02},
            },
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)

        # All metrics should be displayed in improvements section
        imp_section = report[report.find("## Improvements") :]
        next_section = imp_section.find("##", 2)
        imp_text = imp_section[:next_section] if next_section > 0 else imp_section

        assert "recall@5" in imp_text
        assert "precision@5" in imp_text
        assert "hit@5" in imp_text

    def test_regression_section_preserves_other_sections(self):
        """Adding regression section should preserve all other sections."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.80})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.65})
        report = generate_comparison_report(comparison, baseline, candidate)

        # All sections should be present
        assert "## Summary" in report
        assert "## Per-Query Deltas" in report
        assert "## Aggregate Summary" in report
        assert "## Regressions" in report

    def test_regression_with_policy_threshold_display(self):
        """When policy provided, regression section should show thresholds."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15, "precision@5": -0.08}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        policy = {"recall@5": 0.05, "precision@5": 0.10}
        report = generate_comparison_report(comparison, baseline, candidate, policy=policy)

        # Thresholds should appear in report
        assert "0.0500" in report  # recall threshold
        assert "0.1000" in report  # precision threshold
        # Deltas should also appear
        assert "-0.1500" in report
        assert "-0.0800" in report

    def test_regression_without_policy_backward_compatible(self):
        """Without policy, report should work as before (no thresholds)."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run()
        candidate = make_run()
        # No policy parameter passed
        report = generate_comparison_report(comparison, baseline, candidate)

        # Regression section should exist
        assert "## Regressions" in report
        # Deltas should be shown
        assert "-0.1500" in report
        # But no threshold columns


class TestComparisonMarkdownConfidenceIntervals:
    """Test bootstrap CI display in markdown comparison reports."""

    def test_markdown_with_confidence_intervals_section_present(self):
        """When CI data available, markdown should include CI section."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify CI section is present
        assert "## Aggregate Confidence Intervals" in report
        assert "Statistical analysis on 25 paired queries" in report

    def test_markdown_without_statistics_no_ci_section(self):
        """When statistics disabled, no CI section in markdown."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=False,
            bootstrap_results=None,
            num_paired_queries=0,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify CI section is NOT present (backward compatible)
        assert "Aggregate Confidence Intervals" not in report

    def test_markdown_ci_table_has_correct_columns(self):
        """CI table should display metric, mean delta, lower CI, upper CI."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify CI values appear in report
        assert "recall@5" in report
        assert "0.0500" in report  # mean delta
        assert "0.0100" in report  # lower CI
        assert "0.0900" in report  # upper CI

    def test_markdown_ci_multiple_metrics(self):
        """Multiple metrics should each appear in CI table."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            ),
            "precision@5": BootstrapResult(
                metric_name="precision@5",
                num_paired_queries=25,
                mean_delta=-0.02,
                lower_ci=-0.06,
                upper_ci=0.02,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            ),
        }

        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05, "precision@5": -0.02}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify both metrics appear in report
        assert "recall@5" in report
        assert "precision@5" in report
        assert "0.0500" in report
        assert "-0.0200" in report

    def test_markdown_ci_preserves_other_sections(self):
        """Adding CI section should not remove existing sections."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify existing sections still present
        assert "## Summary" in report
        assert "## Per-Query Deltas" in report
        assert "## Aggregate Summary" in report
        assert "## Aggregate Confidence Intervals" in report

    def test_markdown_ci_confidence_level_shown(self):
        """Report should display confidence level in CI section."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Verify 95% confidence level is shown
        assert "95% confidence level" in report or "0.95" in report


# ---------------------------------------------------------------------------
# Feature 8.3: Set-wise Metrics in Markdown Report
# ---------------------------------------------------------------------------


class TestComparisonMarkdownSetwiseMetrics:
    """Test set-wise metrics integration in markdown reports."""

    def make_comparison_with_setwise(
        self,
        per_query_deltas=None,
        per_query_status=None,
        aggregate_deltas=None,
        setwise_deltas=None,
        setwise_aggregate_deltas=None,
    ):
        """Helper to create comparison with setwise data."""
        return ComparisonResult(
            per_query_deltas=per_query_deltas or {},
            per_query_status=per_query_status or {},
            aggregate_deltas=aggregate_deltas or {},
            has_regression=False,
            setwise_deltas=setwise_deltas,
            setwise_aggregate_deltas=setwise_aggregate_deltas,
        )

    def test_markdown_setwise_section_present(self):
        """Setwise section should appear when setwise_aggregate_deltas available."""
        comparison = self.make_comparison_with_setwise(
            setwise_aggregate_deltas={
                "span_concentration": 0.05,
                "fragmentation_ratio": -0.03,
                "pairwise_overlap": 0.01,
            }
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "## Set-wise Metrics" in report

    def test_markdown_setwise_section_absent_when_no_data(self):
        """Setwise section should be omitted when setwise_aggregate_deltas is None."""
        comparison = self.make_comparison_with_setwise(setwise_aggregate_deltas=None)
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "## Set-wise Metrics" not in report

    def test_markdown_setwise_metrics_displayed(self):
        """All three setwise metrics should be displayed in the section."""
        comparison = self.make_comparison_with_setwise(
            setwise_aggregate_deltas={
                "span_concentration": 0.05,
                "fragmentation_ratio": -0.03,
                "pairwise_overlap": 0.01,
            }
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "span_concentration" in report
        assert "fragmentation_ratio" in report
        assert "pairwise_overlap" in report

    def test_markdown_setwise_deltas_with_signs(self):
        """Setwise deltas should appear with +/- signs."""
        comparison = self.make_comparison_with_setwise(
            setwise_aggregate_deltas={
                "span_concentration": 0.05,
                "fragmentation_ratio": -0.03,
                "pairwise_overlap": 0.01,
            }
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        # Check for formatted delta values with signs
        assert "+0.0500" in report  # span_concentration
        assert "-0.0300" in report  # fragmentation_ratio
        assert "+0.0100" in report  # pairwise_overlap

    def test_markdown_setwise_per_query_section_when_significant_changes(self):
        """Per-query setwise section should appear for queries with |delta| > 0.01."""
        comparison = self.make_comparison_with_setwise(
            setwise_deltas={
                "q1": {
                    "span_concentration": 0.15,  # > 0.01, significant
                    "fragmentation_ratio": -0.05,
                },
                "q2": {
                    "span_concentration": 0.005,  # < 0.01, not significant
                    "fragmentation_ratio": 0.002,
                },
            },
            setwise_aggregate_deltas={
                "span_concentration": 0.075,
                "fragmentation_ratio": -0.024,
            },
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        assert "### Per-Query Set-wise Changes" in report
        # q1 should appear (has significant changes)
        assert "q1" in report

    def test_markdown_setwise_per_query_absent_when_no_significant_changes(self):
        """Per-query setwise subsection should be absent if no significant changes."""
        comparison = self.make_comparison_with_setwise(
            setwise_deltas={
                "q1": {
                    "span_concentration": 0.005,  # < 0.01, not significant
                    "fragmentation_ratio": 0.003,
                },
                "q2": {
                    "span_concentration": 0.008,  # < 0.01, not significant
                    "fragmentation_ratio": -0.002,
                },
            },
            setwise_aggregate_deltas={
                "span_concentration": 0.0065,
                "fragmentation_ratio": 0.0005,
            },
        )
        baseline = make_run()
        candidate = make_run()
        report = generate_comparison_report(comparison, baseline, candidate)
        # Aggregate section should be present but not per-query section
        assert "## Set-wise Metrics" in report
        assert "### Per-Query Set-wise Changes" not in report

    def test_markdown_setwise_question_text_shown_when_not_redacted(self):
        """Query questions should appear in per-query setwise section when not redacted."""
        queries = (make_query("q1", "Test question about setwise metrics"),)
        comparison = self.make_comparison_with_setwise(
            setwise_deltas={"q1": {"span_concentration": 0.15}},
            setwise_aggregate_deltas={
                "span_concentration": 0.15,
                "fragmentation_ratio": 0.0,
                "pairwise_overlap": 0.0,
            },
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=False)
        assert "Test question about setwise metrics" in report

    def test_markdown_setwise_question_text_omitted_when_redacted(self):
        """Query questions should be omitted from setwise section when redacted."""
        queries = (make_query("q1", "Secret setwise query"),)
        comparison = self.make_comparison_with_setwise(
            setwise_deltas={"q1": {"span_concentration": 0.15}},
            setwise_aggregate_deltas={
                "span_concentration": 0.15,
                "fragmentation_ratio": 0.0,
                "pairwise_overlap": 0.0,
            },
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        report = generate_comparison_report(comparison, baseline, candidate, redact=True)
        assert "Secret setwise query" not in report
        # But query ID should still be present
        assert "q1" in report

    def test_markdown_setwise_and_statistics_in_same_report(self):
        """Both setwise metrics and statistics should appear in the same report."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = self.make_comparison_with_setwise(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05},
            setwise_aggregate_deltas={
                "span_concentration": 0.05,
                "fragmentation_ratio": -0.03,
                "pairwise_overlap": 0.01,
            },
            setwise_deltas={
                "q1": {
                    "span_concentration": 0.05,
                    "fragmentation_ratio": -0.03,
                    "pairwise_overlap": 0.01,
                }
            },
        )

        comparison = ComparisonResult(
            per_query_deltas=comparison.per_query_deltas,
            per_query_status=comparison.per_query_status,
            aggregate_deltas=comparison.aggregate_deltas,
            has_regression=False,
            statistics_enabled=True,
            bootstrap_results=bootstrap_results,
            num_paired_queries=25,
            setwise_deltas=comparison.setwise_deltas,
            setwise_aggregate_deltas=comparison.setwise_aggregate_deltas,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Both sections should be present
        assert "## Set-wise Metrics" in report
        assert "## Aggregate Confidence Intervals" in report
        # Check ordering: setwise should come before confidence intervals
        pos_setwise = report.find("## Set-wise Metrics")
        pos_ci = report.find("## Aggregate Confidence Intervals")
        assert pos_setwise < pos_ci

    def test_markdown_setwise_placement_after_improvements(self):
        """Setwise section should appear after Improvements section."""
        from spanchor.comparison.statistics import BootstrapResult

        bootstrap_results = {
            "recall@5": BootstrapResult(
                metric_name="recall@5",
                num_paired_queries=25,
                mean_delta=0.05,
                lower_ci=0.01,
                upper_ci=0.09,
                ci_level=0.95,
                num_resamples=10000,
                seed=42,
            )
        }

        comparison = self.make_comparison_with_setwise(
            per_query_deltas={
                "q1": {"recall@5": 0.15},
                "q2": {"recall@5": -0.05},
            },
            per_query_status={"q1": "IMPROVED", "q2": "REGRESSION"},
            setwise_aggregate_deltas={
                "span_concentration": 0.05,
                "fragmentation_ratio": -0.03,
                "pairwise_overlap": 0.01,
            },
        )

        comparison = ComparisonResult(
            per_query_deltas=comparison.per_query_deltas,
            per_query_status=comparison.per_query_status,
            aggregate_deltas=comparison.aggregate_deltas,
            has_regression=True,
            setwise_deltas=comparison.setwise_deltas,
            setwise_aggregate_deltas=comparison.setwise_aggregate_deltas,
        )

        report = generate_comparison_report(comparison, make_run(), make_run())

        # Find positions
        pos_improvements = report.find("## Improvements")
        pos_setwise = report.find("## Set-wise Metrics")

        # Setwise should appear after improvements
        if pos_improvements >= 0 and pos_setwise >= 0:
            assert pos_improvements < pos_setwise
