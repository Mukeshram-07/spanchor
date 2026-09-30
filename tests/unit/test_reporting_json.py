"""Unit tests for JSON report generation.

Tests generate_evaluation_json() and generate_comparison_json()
covering all acceptance criteria for Requirement 22.

Validates: Requirements 22.1, 22.2, 22.3, 22.4, 22.5, 22.6
"""

import json

import pytest

from spanchor.comparison.compare import ComparisonResult
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query
from spanchor.models.run import Run
from spanchor.reporting.json_report import (
    generate_comparison_json,
    generate_evaluation_json,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_run(
    per_query_metrics: dict[str, dict[str, float]] | None = None,
    aggregate_metrics: dict[str, float] | None = None,
    mapper_stats: dict[str, int] | None = None,
    queries: tuple[Query, ...] | None = None,
    config: dict | None = None,
    timestamp: str = "2024-01-01T00:00:00Z",
    schema_version: str = "0.1.0",
) -> Run:
    """Build a minimal Run for testing."""
    return Run(
        timestamp=timestamp,
        queries=queries if queries is not None else tuple(),
        per_query_metrics=per_query_metrics if per_query_metrics is not None else {},
        aggregate_metrics=aggregate_metrics if aggregate_metrics is not None else {},
        config=config if config is not None else {"k": 5},
        mapper_stats=mapper_stats if mapper_stats is not None else {},
        schema_version=schema_version,
    )


def make_query(query_id: str, question: str) -> Query:
    """Build a minimal Query with no anchors for testing."""
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
# generate_evaluation_json — Return type and JSON-serialisability
# ---------------------------------------------------------------------------


class TestEvalJsonReturnType:
    """Basic structural tests for generate_evaluation_json."""

    def test_returns_dict(self):
        """generate_evaluation_json must return a dict."""
        run = make_run()
        result = generate_evaluation_json(run)
        assert isinstance(result, dict)

    def test_result_is_json_serialisable(self):
        """The returned dict must be serialisable with json.dumps."""
        run = make_run(
            per_query_metrics={"q1": {"recall@5": 0.85}},
            aggregate_metrics={"mean_recall@5": 0.85},
            mapper_stats={"MAPPED_EXACT": 10, "UNMAPPED": 1},
        )
        result = generate_evaluation_json(run)
        serialised = json.dumps(result)
        assert isinstance(serialised, str)

    def test_schema_version_present(self):
        """The dict must include schema_version from the run."""
        run = make_run(schema_version="0.1.0")
        result = generate_evaluation_json(run)
        assert result["schema_version"] == "0.1.0"

    def test_timestamp_present(self):
        """The dict must include the run timestamp."""
        run = make_run(timestamp="2024-06-15T12:00:00Z")
        result = generate_evaluation_json(run)
        assert result["timestamp"] == "2024-06-15T12:00:00Z"


# ---------------------------------------------------------------------------
# generate_evaluation_json — Aggregate Metrics (Req 22.1)
# ---------------------------------------------------------------------------


class TestEvalJsonAggregateMetrics:
    """Tests that all aggregate metrics are included in the JSON output."""

    def test_aggregate_metrics_key_present(self):
        """The 'aggregate_metrics' key must exist in the result. (Req 22.1)"""
        run = make_run(aggregate_metrics={"mean_recall@5": 0.85})
        result = generate_evaluation_json(run)
        assert "aggregate_metrics" in result

    def test_all_aggregate_metrics_values_present(self):
        """All aggregate metric values must be present and accurate. (Req 22.1)"""
        agg = {"mean_recall@5": 0.85, "mean_precision@5": 0.72, "mean_hit@5": 0.90}
        run = make_run(aggregate_metrics=agg)
        result = generate_evaluation_json(run)
        assert result["aggregate_metrics"] == agg

    def test_empty_aggregate_metrics_returns_empty_dict(self):
        """Empty aggregate_metrics should serialise as empty dict. (Req 22.1)"""
        run = make_run(aggregate_metrics={})
        result = generate_evaluation_json(run)
        assert result["aggregate_metrics"] == {}


# ---------------------------------------------------------------------------
# generate_evaluation_json — Per-Query Metrics (Req 22.2)
# ---------------------------------------------------------------------------


class TestEvalJsonPerQueryMetrics:
    """Tests that all per-query metrics are included in the JSON output."""

    def test_per_query_metrics_key_present(self):
        """The 'per_query_metrics' key must exist in the result. (Req 22.2)"""
        run = make_run(per_query_metrics={"q1": {"recall@5": 0.8}})
        result = generate_evaluation_json(run)
        assert "per_query_metrics" in result

    def test_all_query_ids_present(self):
        """All query IDs must appear in per_query_metrics. (Req 22.2)"""
        run = make_run(
            per_query_metrics={
                "q1": {"recall@5": 0.8},
                "q2": {"recall@5": 0.6},
                "q3": {"recall@5": 0.95},
            }
        )
        result = generate_evaluation_json(run)
        pq = result["per_query_metrics"]
        assert "q1" in pq
        assert "q2" in pq
        assert "q3" in pq

    def test_metric_values_accurate(self):
        """Per-query metric values must be exact. (Req 22.2)"""
        run = make_run(per_query_metrics={"q1": {"recall@5": 0.75, "hit@5": 1.0}})
        result = generate_evaluation_json(run)
        metrics = result["per_query_metrics"]["q1"]["metrics"]
        assert metrics["recall@5"] == 0.75
        assert metrics["hit@5"] == 1.0

    def test_metrics_nested_under_metrics_key(self):
        """Per-query entry should have a 'metrics' sub-key containing the values."""
        run = make_run(per_query_metrics={"q1": {"recall@5": 0.8}})
        result = generate_evaluation_json(run)
        assert "metrics" in result["per_query_metrics"]["q1"]

    def test_empty_per_query_returns_empty_dict(self):
        """Empty per_query_metrics should serialise as empty dict. (Req 22.2)"""
        run = make_run(per_query_metrics={})
        result = generate_evaluation_json(run)
        assert result["per_query_metrics"] == {}


# ---------------------------------------------------------------------------
# generate_evaluation_json — Configuration (Req 22.3)
# ---------------------------------------------------------------------------


class TestEvalJsonConfiguration:
    """Tests that configuration parameters are included in the JSON output."""

    def test_config_key_present(self):
        """The 'config' key must exist in the result. (Req 22.3)"""
        run = make_run(config={"k": 5, "min_overlap": 0.5})
        result = generate_evaluation_json(run)
        assert "config" in result

    def test_config_values_accurate(self):
        """All configuration values must be present and accurate. (Req 22.3)"""
        cfg = {"k": 10, "min_overlap": 0.7, "max_unmapped_rate": 0.1}
        run = make_run(config=cfg)
        result = generate_evaluation_json(run)
        assert result["config"] == cfg

    def test_empty_config_returns_empty_dict(self):
        """Empty config should serialise as empty dict. (Req 22.3)"""
        run = make_run(config={})
        result = generate_evaluation_json(run)
        assert result["config"] == {}


# ---------------------------------------------------------------------------
# generate_evaluation_json — Mapper Stats
# ---------------------------------------------------------------------------


class TestEvalJsonMapperStats:
    """Tests that mapper statistics are included in the JSON output."""

    def test_mapper_stats_key_present(self):
        """The 'mapper_stats' key must exist in the result."""
        run = make_run(mapper_stats={"MAPPED_EXACT": 10})
        result = generate_evaluation_json(run)
        assert "mapper_stats" in result

    def test_mapper_stats_values_accurate(self):
        """All mapper stat values must be present and accurate."""
        stats = {"MAPPED_EXACT": 40, "MAPPED_NORMALIZED": 5, "AMBIGUOUS": 2, "UNMAPPED": 3}
        run = make_run(mapper_stats=stats)
        result = generate_evaluation_json(run)
        assert result["mapper_stats"] == stats


# ---------------------------------------------------------------------------
# generate_evaluation_json — Redaction (Req 22.6)
# ---------------------------------------------------------------------------


class TestEvalJsonRedaction:
    """Tests that redact=True removes source text from evaluation JSON."""

    def test_question_absent_when_redacted(self):
        """Question text must not appear in per_query when redact=True. (Req 22.6)"""
        queries = (make_query("q1", "Secret question text"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        result = generate_evaluation_json(run, redact=True)
        q1_entry = result["per_query_metrics"]["q1"]
        assert "question" not in q1_entry
        # Also verify it doesn't appear anywhere in the JSON string
        serialised = json.dumps(result)
        assert "Secret question text" not in serialised

    def test_question_present_when_not_redacted(self):
        """Question text must appear in per_query when redact=False. (Req 22.6)"""
        queries = (make_query("q1", "What is spanchor?"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        result = generate_evaluation_json(run, redact=False)
        q1_entry = result["per_query_metrics"]["q1"]
        assert q1_entry["question"] == "What is spanchor?"

    def test_metrics_still_present_when_redacted(self):
        """Metric values must still be present when redact=True. (Req 22.6)"""
        queries = (make_query("q1", "Confidential"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.75}},
            aggregate_metrics={"mean_recall@5": 0.75},
        )
        result = generate_evaluation_json(run, redact=True)
        assert result["per_query_metrics"]["q1"]["metrics"]["recall@5"] == 0.75
        assert result["aggregate_metrics"]["mean_recall@5"] == 0.75

    def test_query_id_still_present_when_redacted(self):
        """Query IDs must still be present as keys when redact=True. (Req 22.6)"""
        queries = (make_query("my-query-id", "Some text"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"my-query-id": {"recall@5": 0.8}},
        )
        result = generate_evaluation_json(run, redact=True)
        assert "my-query-id" in result["per_query_metrics"]

    def test_no_question_in_per_query_for_unknown_qid_when_not_redacted(self):
        """Per-query entry for a query_id with no matching Query should not include question."""
        # Run has per_query_metrics for "orphan-q" but no corresponding Query object
        run = make_run(
            queries=tuple(),
            per_query_metrics={"orphan-q": {"recall@5": 0.5}},
        )
        result = generate_evaluation_json(run, redact=False)
        assert "question" not in result["per_query_metrics"]["orphan-q"]


# ---------------------------------------------------------------------------
# generate_comparison_json — Return type and JSON-serialisability
# ---------------------------------------------------------------------------


class TestComparisonJsonReturnType:
    """Basic structural tests for generate_comparison_json."""

    def test_returns_dict(self):
        """generate_comparison_json must return a dict."""
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert isinstance(result, dict)

    def test_result_is_json_serialisable(self):
        """The returned dict must be serialisable with json.dumps."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
            aggregate_deltas={"recall@5": 0.05},
        )
        baseline = make_run(aggregate_metrics={"mean_recall@5": 0.80})
        candidate = make_run(aggregate_metrics={"mean_recall@5": 0.85})
        result = generate_comparison_json(comparison, baseline, candidate)
        serialised = json.dumps(result)
        assert isinstance(serialised, str)


# ---------------------------------------------------------------------------
# generate_comparison_json — Per-Query Deltas and Statuses (Req 22.4)
# ---------------------------------------------------------------------------


class TestComparisonJsonPerQueryDeltas:
    """Tests that per-query deltas and statuses are included in the JSON output."""

    def test_per_query_key_present(self):
        """The 'per_query' key must exist in the result. (Req 22.4)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert "per_query" in result

    def test_all_query_ids_present(self):
        """All query IDs from deltas must appear in per_query. (Req 22.4)"""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.05},
                "q2": {"recall@5": -0.10},
            },
            per_query_status={"q1": "IMPROVED", "q2": "REGRESSION"},
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        pq = result["per_query"]
        assert "q1" in pq
        assert "q2" in pq

    def test_delta_values_accurate(self):
        """Delta values must be exact. (Req 22.4)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05, "hit@5": -0.10}},
            per_query_status={"q1": "REGRESSION"},
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        deltas = result["per_query"]["q1"]["deltas"]
        assert deltas["recall@5"] == 0.05
        assert deltas["hit@5"] == -0.10

    def test_status_values_accurate(self):
        """Status must be one of IMPROVED / REGRESSION / UNCHANGED. (Req 22.4)"""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.1},
                "q2": {"recall@5": -0.1},
                "q3": {"recall@5": 0.0},
            },
            per_query_status={
                "q1": "IMPROVED",
                "q2": "REGRESSION",
                "q3": "UNCHANGED",
            },
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        pq = result["per_query"]
        assert pq["q1"]["status"] == "IMPROVED"
        assert pq["q2"]["status"] == "REGRESSION"
        assert pq["q3"]["status"] == "UNCHANGED"

    def test_empty_per_query_returns_empty_dict(self):
        """Empty per_query_deltas should serialise as empty dict. (Req 22.4)"""
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["per_query"] == {}


# ---------------------------------------------------------------------------
# generate_comparison_json — Aggregate Deltas (Req 22.5)
# ---------------------------------------------------------------------------


class TestComparisonJsonAggregateDeltas:
    """Tests that aggregate deltas are included in the JSON output."""

    def test_aggregate_deltas_key_present(self):
        """The 'aggregate_deltas' key must exist in the result. (Req 22.5)"""
        comparison = make_comparison_result({}, {}, aggregate_deltas={"recall@5": 0.05})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert "aggregate_deltas" in result

    def test_aggregate_delta_values_accurate(self):
        """Aggregate delta values must be exact. (Req 22.5)"""
        agg_deltas = {"recall@5": 0.05, "precision@5": -0.02, "hit@5": 0.10}
        comparison = make_comparison_result({}, {}, aggregate_deltas=agg_deltas)
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["aggregate_deltas"] == agg_deltas

    def test_empty_aggregate_deltas_returns_empty_dict(self):
        """Empty aggregate_deltas should serialise as empty dict. (Req 22.5)"""
        comparison = make_comparison_result({}, {}, aggregate_deltas={})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["aggregate_deltas"] == {}


# ---------------------------------------------------------------------------
# generate_comparison_json — has_regression flag
# ---------------------------------------------------------------------------


class TestComparisonJsonRegressionFlag:
    """Tests for the has_regression flag in comparison JSON."""

    def test_has_regression_true_when_regression(self):
        """has_regression must be True when any query is REGRESSION."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.15}},
            per_query_status={"q1": "REGRESSION"},
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["has_regression"] is True

    def test_has_regression_false_when_no_regression(self):
        """has_regression must be False when no query is REGRESSION."""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["has_regression"] is False

    def test_has_regression_false_for_empty_comparison(self):
        """has_regression must be False for an empty comparison."""
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert result["has_regression"] is False


# ---------------------------------------------------------------------------
# generate_comparison_json — Baseline / Candidate metadata
# ---------------------------------------------------------------------------


class TestComparisonJsonMetadata:
    """Tests that baseline and candidate metadata are present in comparison JSON."""

    def test_baseline_key_present(self):
        """The 'baseline' key must exist in the result."""
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert "baseline" in result

    def test_candidate_key_present(self):
        """The 'candidate' key must exist in the result."""
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), make_run())
        assert "candidate" in result

    def test_baseline_timestamp_accurate(self):
        """Baseline timestamp must match baseline run's timestamp."""
        baseline = make_run(timestamp="2024-01-01T00:00:00Z")
        candidate = make_run(timestamp="2024-02-01T00:00:00Z")
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, baseline, candidate)
        assert result["baseline"]["timestamp"] == "2024-01-01T00:00:00Z"

    def test_candidate_timestamp_accurate(self):
        """Candidate timestamp must match candidate run's timestamp."""
        baseline = make_run(timestamp="2024-01-01T00:00:00Z")
        candidate = make_run(timestamp="2024-02-01T00:00:00Z")
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, baseline, candidate)
        assert result["candidate"]["timestamp"] == "2024-02-01T00:00:00Z"

    def test_baseline_config_accurate(self):
        """Baseline config must match baseline run's config."""
        baseline = make_run(config={"k": 5, "min_overlap": 0.5})
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, baseline, make_run())
        assert result["baseline"]["config"] == {"k": 5, "min_overlap": 0.5}

    def test_candidate_config_accurate(self):
        """Candidate config must match candidate run's config."""
        candidate = make_run(config={"k": 10, "min_overlap": 0.7})
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), candidate)
        assert result["candidate"]["config"] == {"k": 10, "min_overlap": 0.7}

    def test_baseline_schema_version_present(self):
        """Baseline schema_version must appear in baseline metadata."""
        baseline = make_run(schema_version="0.1.0")
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, baseline, make_run())
        assert result["baseline"]["schema_version"] == "0.1.0"

    def test_candidate_schema_version_present(self):
        """Candidate schema_version must appear in candidate metadata."""
        candidate = make_run(schema_version="0.1.0")
        comparison = make_comparison_result({}, {})
        result = generate_comparison_json(comparison, make_run(), candidate)
        assert result["candidate"]["schema_version"] == "0.1.0"


# ---------------------------------------------------------------------------
# generate_comparison_json — Redaction (Req 22.6)
# ---------------------------------------------------------------------------


class TestComparisonJsonRedaction:
    """Tests that redact=True removes source text from comparison JSON."""

    def test_question_absent_when_redacted(self):
        """Question text must not appear in per_query when redact=True. (Req 22.6)"""
        queries = (make_query("q1", "Confidential question text"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        result = generate_comparison_json(comparison, baseline, candidate, redact=True)
        q1_entry = result["per_query"]["q1"]
        assert "question" not in q1_entry
        serialised = json.dumps(result)
        assert "Confidential question text" not in serialised

    def test_question_present_when_not_redacted(self):
        """Question text must appear in per_query when redact=False. (Req 22.6)"""
        queries = (make_query("q1", "What does spanchor do?"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        result = generate_comparison_json(comparison, baseline, candidate, redact=False)
        assert result["per_query"]["q1"]["question"] == "What does spanchor do?"

    def test_question_from_baseline_used_for_shared_query(self):
        """When both runs have same query_id, baseline question is used."""
        b_queries = (make_query("q1", "Baseline question"),)
        c_queries = (make_query("q1", "Candidate question"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.0}},
            per_query_status={"q1": "UNCHANGED"},
        )
        baseline = make_run(queries=b_queries)
        candidate = make_run(queries=c_queries)
        result = generate_comparison_json(comparison, baseline, candidate, redact=False)
        # baseline question takes priority (set last in the merge loop)
        assert result["per_query"]["q1"]["question"] == "Baseline question"

    def test_deltas_still_present_when_redacted(self):
        """Delta values must still be present when redact=True. (Req 22.6)"""
        queries = (make_query("q1", "Secret"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": -0.10}},
            per_query_status={"q1": "REGRESSION"},
        )
        baseline = make_run(queries=queries)
        candidate = make_run(queries=queries)
        result = generate_comparison_json(comparison, baseline, candidate, redact=True)
        assert result["per_query"]["q1"]["deltas"]["recall@5"] == -0.10

    def test_status_still_present_when_redacted(self):
        """Status must still be present when redact=True. (Req 22.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.0}},
            per_query_status={"q1": "UNCHANGED"},
        )
        result = generate_comparison_json(
            comparison, make_run(), make_run(), redact=True
        )
        assert result["per_query"]["q1"]["status"] == "UNCHANGED"

    def test_query_id_still_present_when_redacted(self):
        """Query IDs must still be present as keys when redact=True. (Req 22.6)"""
        comparison = make_comparison_result(
            per_query_deltas={"specific-query-id": {"recall@5": 0.05}},
            per_query_status={"specific-query-id": "IMPROVED"},
        )
        result = generate_comparison_json(
            comparison, make_run(), make_run(), redact=True
        )
        assert "specific-query-id" in result["per_query"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases for both JSON generators."""

    def test_eval_json_multiple_queries_multiple_metrics(self):
        """Should handle many queries and metrics without error."""
        pq = {f"q{i}": {f"metric_{j}": float(i * j) / 100 for j in range(1, 6)}
              for i in range(1, 11)}
        run = make_run(per_query_metrics=pq)
        result = generate_evaluation_json(run)
        assert len(result["per_query_metrics"]) == 10
        for i in range(1, 11):
            assert f"q{i}" in result["per_query_metrics"]

    def test_comparison_json_all_statuses_present(self):
        """Comparison with all three statuses should serialise correctly."""
        comparison = make_comparison_result(
            per_query_deltas={
                "q1": {"recall@5": 0.1},
                "q2": {"recall@5": -0.1},
                "q3": {"recall@5": 0.0},
            },
            per_query_status={
                "q1": "IMPROVED",
                "q2": "REGRESSION",
                "q3": "UNCHANGED",
            },
        )
        result = generate_comparison_json(comparison, make_run(), make_run())
        statuses = {qid: entry["status"] for qid, entry in result["per_query"].items()}
        assert statuses == {"q1": "IMPROVED", "q2": "REGRESSION", "q3": "UNCHANGED"}

    def test_eval_json_default_redact_is_false(self):
        """redact should default to False for generate_evaluation_json."""
        queries = (make_query("q1", "Visible question"),)
        run = make_run(
            queries=queries,
            per_query_metrics={"q1": {"recall@5": 0.9}},
        )
        result = generate_evaluation_json(run)
        assert result["per_query_metrics"]["q1"]["question"] == "Visible question"

    def test_comparison_json_default_redact_is_false(self):
        """redact should default to False for generate_comparison_json."""
        queries = (make_query("q1", "Visible question"),)
        comparison = make_comparison_result(
            per_query_deltas={"q1": {"recall@5": 0.05}},
            per_query_status={"q1": "IMPROVED"},
        )
        baseline = make_run(queries=queries)
        result = generate_comparison_json(comparison, baseline, make_run())
        assert result["per_query"]["q1"]["question"] == "Visible question"

    def test_eval_json_config_complex_types(self):
        """Config with nested values should round-trip through JSON correctly."""
        cfg = {"k": 5, "k_values": [1, 3, 5, 10], "min_overlap": 0.5}
        run = make_run(config=cfg)
        result = generate_evaluation_json(run)
        # Verify it's JSON serialisable and values are preserved
        round_tripped = json.loads(json.dumps(result))
        assert round_tripped["config"] == cfg
