"""Unit tests for JSON I/O storage functions."""

import json
from pathlib import Path

import pytest

from spanchor.errors import InvalidSchemaError
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query
from spanchor.models.run import Run
from spanchor.storage.json_io import read_run, write_run


class TestReadRun:
    """Tests for read_run function."""

    def test_read_valid_run(self, tmp_path: Path) -> None:
        """Test reading a valid Run from JSON."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": "q1",
                    "question": "What is Python?",
                    "anchors": [
                        {
                            "document_id": "doc1",
                            "start": 0,
                            "end": 10,
                            "expected_text_hash": "hash123",
                            "schema_version": "0.1.0",
                        }
                    ],
                    "schema_version": "0.1.0",
                }
            ],
            "per_query_metrics": {"q1": {"recall@5": 0.85, "precision@5": 0.72}},
            "aggregate_metrics": {
                "mean_recall@5": 0.85,
                "mean_precision@5": 0.72,
            },
            "config": {"k": 5, "min_overlap": 0.5},
            "mapper_stats": {
                "MAPPED_EXACT": 10,
                "MAPPED_NORMALIZED": 2,
                "AMBIGUOUS": 1,
                "UNMAPPED": 0,
            },
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        run = read_run(json_file)

        assert run.timestamp == "2024-01-15T10:30:00Z"
        assert len(run.queries) == 1
        assert run.queries[0].query_id == "q1"
        assert run.queries[0].question == "What is Python?"
        assert len(run.queries[0].anchors) == 1
        assert run.per_query_metrics["q1"]["recall@5"] == 0.85
        assert run.aggregate_metrics["mean_recall@5"] == 0.85
        assert run.config["k"] == 5
        assert run.mapper_stats["MAPPED_EXACT"] == 10
        assert run.schema_version == "0.1.0"

    def test_read_run_with_multiple_queries(self, tmp_path: Path) -> None:
        """Test reading a Run with multiple queries."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": "q1",
                    "question": "First?",
                    "anchors": [],
                    "schema_version": "0.1.0",
                },
                {
                    "query_id": "q2",
                    "question": "Second?",
                    "anchors": [],
                    "schema_version": "0.1.0",
                },
            ],
            "per_query_metrics": {
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.90},
            },
            "aggregate_metrics": {"mean_recall@5": 0.85},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        run = read_run(json_file)

        assert len(run.queries) == 2
        assert run.queries[0].query_id == "q1"
        assert run.queries[1].query_id == "q2"

    def test_read_run_with_empty_queries(self, tmp_path: Path) -> None:
        """Test reading a Run with no queries."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        run = read_run(json_file)

        assert len(run.queries) == 0
        assert len(run.per_query_metrics) == 0

    def test_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """Test that malformed JSON raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        json_file.write_text("{ invalid json }")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Invalid JSON" in str(exc_info.value)

    def test_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Test that missing file raises InvalidSchemaError."""
        json_file = tmp_path / "nonexistent.json"

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "File not found" in str(exc_info.value)

    def test_non_dict_json_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dictionary JSON raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        json_file.write_text('["not", "a", "dict"]')

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Expected JSON object" in str(exc_info.value)

    def test_missing_schema_version_raises_error(self, tmp_path: Path) -> None:
        """Test that missing schema_version raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            # Missing schema_version
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'schema_version'" in str(exc_info.value)
        assert "Field: schema_version" in str(exc_info.value)

    def test_missing_timestamp_raises_error(self, tmp_path: Path) -> None:
        """Test that missing timestamp raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'timestamp'" in str(exc_info.value)

    def test_missing_queries_raises_error(self, tmp_path: Path) -> None:
        """Test that missing queries field raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'queries'" in str(exc_info.value)

    def test_missing_per_query_metrics_raises_error(self, tmp_path: Path) -> None:
        """Test that missing per_query_metrics raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'per_query_metrics'" in str(exc_info.value)

    def test_missing_aggregate_metrics_raises_error(self, tmp_path: Path) -> None:
        """Test that missing aggregate_metrics raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'aggregate_metrics'" in str(exc_info.value)

    def test_missing_config_raises_error(self, tmp_path: Path) -> None:
        """Test that missing config raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'config'" in str(exc_info.value)

    def test_missing_mapper_stats_raises_error(self, tmp_path: Path) -> None:
        """Test that missing mapper_stats raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "Missing required field 'mapper_stats'" in str(exc_info.value)

    def test_non_string_timestamp_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string timestamp raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": 12345,  # Should be string
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a string" in str(exc_info.value)
        assert "timestamp" in str(exc_info.value)

    def test_non_list_queries_raises_error(self, tmp_path: Path) -> None:
        """Test that non-list queries raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": "not a list",
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a list" in str(exc_info.value)
        assert "queries" in str(exc_info.value)

    def test_non_dict_per_query_metrics_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dict per_query_metrics raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": "not a dict",
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a dict" in str(exc_info.value)
        assert "per_query_metrics" in str(exc_info.value)

    def test_non_dict_aggregate_metrics_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dict aggregate_metrics raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": [],
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a dict" in str(exc_info.value)
        assert "aggregate_metrics" in str(exc_info.value)

    def test_non_dict_config_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dict config raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": [],
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a dict" in str(exc_info.value)
        assert "config" in str(exc_info.value)

    def test_non_dict_mapper_stats_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dict mapper_stats raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": [],
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be a dict" in str(exc_info.value)
        assert "mapper_stats" in str(exc_info.value)

    def test_query_missing_field_raises_error(self, tmp_path: Path) -> None:
        """Test that query missing required field raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": "q1",
                    # Missing question
                    "anchors": [],
                    "schema_version": "0.1.0",
                }
            ],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "missing field 'question'" in str(exc_info.value)
        assert "queries[0]" in str(exc_info.value)

    def test_query_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that query field with wrong type raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": 123,  # Should be string
                    "question": "Test?",
                    "anchors": [],
                    "schema_version": "0.1.0",
                }
            ],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be string" in str(exc_info.value)
        assert "query_id" in str(exc_info.value)

    def test_anchor_missing_field_raises_error(self, tmp_path: Path) -> None:
        """Test that anchor missing required field raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": "q1",
                    "question": "Test?",
                    "anchors": [
                        {
                            "document_id": "doc1",
                            "start": 0,
                            # Missing end
                            "expected_text_hash": "hash",
                        }
                    ],
                    "schema_version": "0.1.0",
                }
            ],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "missing field 'end'" in str(exc_info.value)
        assert "anchors[0]" in str(exc_info.value)

    def test_anchor_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that anchor field with wrong type raises InvalidSchemaError."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [
                {
                    "query_id": "q1",
                    "question": "Test?",
                    "anchors": [
                        {
                            "document_id": "doc1",
                            "start": "0",  # Should be int
                            "end": 10,
                            "expected_text_hash": "hash",
                        }
                    ],
                    "schema_version": "0.1.0",
                }
            ],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be int" in str(exc_info.value)
        assert "start" in str(exc_info.value)

    def test_per_query_metrics_wrong_structure_raises_error(self, tmp_path: Path) -> None:
        """Test that per_query_metrics with wrong structure raises error."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {
                "q1": "not a dict",  # Should be dict of metrics
            },
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be dict" in str(exc_info.value)
        assert "per_query_metrics" in str(exc_info.value)

    def test_metric_value_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that metric value with wrong type raises error."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {
                "q1": {"recall@5": "not a number"},  # Should be numeric
            },
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be numeric" in str(exc_info.value)
        assert "recall@5" in str(exc_info.value)

    def test_aggregate_metric_value_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that aggregate metric value with wrong type raises error."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {
                "mean_recall@5": "not a number",  # Should be numeric
            },
            "config": {},
            "mapper_stats": {},
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be numeric" in str(exc_info.value)
        assert "mean_recall@5" in str(exc_info.value)

    def test_mapper_stat_count_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that mapper stat count with wrong type raises error."""
        json_file = tmp_path / "run.json"
        data = {
            "timestamp": "2024-01-15T10:30:00Z",
            "queries": [],
            "per_query_metrics": {},
            "aggregate_metrics": {},
            "config": {},
            "mapper_stats": {
                "MAPPED_EXACT": "not an int",  # Should be int
            },
            "schema_version": "0.1.0",
        }
        json_file.write_text(json.dumps(data))

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_run(json_file)

        assert "must be int" in str(exc_info.value)
        assert "MAPPED_EXACT" in str(exc_info.value)


class TestWriteRun:
    """Tests for write_run function."""

    def test_write_basic_run(self, tmp_path: Path) -> None:
        """Test writing a basic Run to JSON."""
        json_file = tmp_path / "output.json"
        query = Query("q1", "What is X?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={"q1": {"recall@5": 0.85}},
            aggregate_metrics={"mean_recall@5": 0.85},
            config={"k": 5},
            mapper_stats={"MAPPED_EXACT": 10},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        assert json_file.exists()
        data = json.loads(json_file.read_text())
        assert data["timestamp"] == "2024-01-15T10:30:00Z"
        assert len(data["queries"]) == 1
        assert data["queries"][0]["query_id"] == "q1"
        assert data["queries"][0]["question"] == "What is X?"
        assert data["per_query_metrics"]["q1"]["recall@5"] == 0.85

    def test_write_run_with_multiple_queries(self, tmp_path: Path) -> None:
        """Test writing a Run with multiple queries."""
        json_file = tmp_path / "output.json"
        queries = (
            Query("q1", "First?", (), "0.1.0"),
            Query("q2", "Second?", (), "0.1.0"),
        )
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=queries,
            per_query_metrics={
                "q1": {"recall@5": 0.80},
                "q2": {"recall@5": 0.90},
            },
            aggregate_metrics={"mean_recall@5": 0.85},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        data = json.loads(json_file.read_text())
        assert len(data["queries"]) == 2
        assert data["queries"][0]["query_id"] == "q1"
        assert data["queries"][1]["query_id"] == "q2"

    def test_write_run_with_anchors(self, tmp_path: Path) -> None:
        """Test writing a Run with queries containing anchors."""
        json_file = tmp_path / "output.json"
        anchors = (
            Anchor("doc1", 0, 10, "hash1", "0.1.0"),
            Anchor("doc2", 20, 30, "hash2", "0.1.0"),
        )
        query = Query("q1", "Multi-anchor?", anchors, "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        data = json.loads(json_file.read_text())
        assert len(data["queries"][0]["anchors"]) == 2
        assert data["queries"][0]["anchors"][0]["document_id"] == "doc1"
        assert data["queries"][0]["anchors"][1]["document_id"] == "doc2"

    def test_write_run_with_redaction(self, tmp_path: Path) -> None:
        """Test writing a Run with redaction enabled."""
        json_file = tmp_path / "redacted.json"
        query = Query("q1", "Sensitive question?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run, redact=True)

        data = json.loads(json_file.read_text())
        # Question should be redacted (empty string)
        assert data["queries"][0]["question"] == ""
        # Other fields should be preserved
        assert data["queries"][0]["query_id"] == "q1"
        assert data["timestamp"] == "2024-01-15T10:30:00Z"

    def test_write_run_without_redaction_preserves_text(self, tmp_path: Path) -> None:
        """Test that without redaction, question text is preserved."""
        json_file = tmp_path / "output.json"
        query = Query("q1", "What is the answer?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run, redact=False)

        data = json.loads(json_file.read_text())
        assert data["queries"][0]["question"] == "What is the answer?"

    def test_write_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test that write_run creates parent directories."""
        json_file = tmp_path / "subdir" / "nested" / "output.json"
        query = Query("q1", "Test?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        assert json_file.exists()
        assert json_file.parent.exists()

    def test_write_unicode_content(self, tmp_path: Path) -> None:
        """Test writing queries with unicode characters."""
        json_file = tmp_path / "unicode.json"
        query = Query("q1", "What is 日本語?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        data = json.loads(json_file.read_text(encoding="utf-8"))
        assert data["queries"][0]["question"] == "What is 日本語?"

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        """Test that write then read preserves all data."""
        json_file = tmp_path / "roundtrip.json"
        anchors = (
            Anchor("doc1", 5, 15, "hash_abc", "0.1.0"),
            Anchor("doc2", 100, 200, "hash_xyz", "0.1.0"),
        )
        original_query = Query("q1", "Test question?", anchors, "0.1.0")
        original_run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(original_query,),
            per_query_metrics={"q1": {"recall@5": 0.85, "precision@5": 0.72}},
            aggregate_metrics={"mean_recall@5": 0.85},
            config={"k": 5, "min_overlap": 0.5},
            mapper_stats={"MAPPED_EXACT": 42, "UNMAPPED": 3},
            schema_version="0.1.0",
        )

        write_run(json_file, original_run)
        loaded_run = read_run(json_file)

        assert loaded_run.timestamp == original_run.timestamp
        assert loaded_run.schema_version == original_run.schema_version
        assert len(loaded_run.queries) == len(original_run.queries)
        assert loaded_run.queries[0].query_id == original_run.queries[0].query_id
        assert loaded_run.queries[0].question == original_run.queries[0].question
        assert len(loaded_run.queries[0].anchors) == len(original_run.queries[0].anchors)
        assert loaded_run.per_query_metrics == original_run.per_query_metrics
        assert loaded_run.aggregate_metrics == original_run.aggregate_metrics
        assert loaded_run.config == original_run.config
        assert loaded_run.mapper_stats == original_run.mapper_stats

    def test_roundtrip_with_redaction(self, tmp_path: Path) -> None:
        """Test that redacted write and read produces empty questions."""
        json_file = tmp_path / "roundtrip_redacted.json"
        query = Query("q1", "Original question", (), "0.1.0")
        original_run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, original_run, redact=True)
        loaded_run = read_run(json_file)

        # Question should be empty after redaction
        assert loaded_run.queries[0].question == ""
        # Other data should be intact
        assert loaded_run.queries[0].query_id == "q1"
        assert loaded_run.timestamp == original_run.timestamp

    def test_write_with_complex_config(self, tmp_path: Path) -> None:
        """Test writing a Run with complex nested config."""
        json_file = tmp_path / "output.json"
        query = Query("q1", "Test?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={},
            aggregate_metrics={},
            config={
                "k_values": [5, 10, 20],
                "min_overlap": 0.5,
                "nested": {"option": True, "count": 42},
            },
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)

        data = json.loads(json_file.read_text())
        assert data["config"]["k_values"] == [5, 10, 20]
        assert data["config"]["nested"]["option"] is True
        assert data["config"]["nested"]["count"] == 42

    def test_write_preserves_metric_precision(self, tmp_path: Path) -> None:
        """Test that floating point metric values are preserved correctly."""
        json_file = tmp_path / "output.json"
        query = Query("q1", "Test?", (), "0.1.0")
        run = Run(
            timestamp="2024-01-15T10:30:00Z",
            queries=(query,),
            per_query_metrics={
                "q1": {
                    "recall@5": 0.85123456,
                    "precision@5": 0.72987654,
                }
            },
            aggregate_metrics={"mean_recall@5": 0.85123456},
            config={},
            mapper_stats={},
            schema_version="0.1.0",
        )

        write_run(json_file, run)
        loaded_run = read_run(json_file)

        assert loaded_run.per_query_metrics["q1"]["recall@5"] == pytest.approx(0.85123456)
        assert loaded_run.per_query_metrics["q1"]["precision@5"] == pytest.approx(0.72987654)
