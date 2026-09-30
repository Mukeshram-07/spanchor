"""Unit tests for JSONL storage functions."""

import json
from pathlib import Path

import pytest

from spanchor.errors import InvalidSchemaError
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query
from spanchor.storage.jsonl import read_gold_set, write_gold_set


class TestReadGoldSet:
    """Tests for read_gold_set function."""

    def test_read_valid_jsonl_single_query(self, tmp_path: Path) -> None:
        """Test reading a valid JSONL file with a single query."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "What is Python?",
            "anchors": [
                {
                    "document_id": "doc1",
                    "start": 0,
                    "end": 10,
                    "expected_text_hash": "abcd1234",
                    "schema_version": "0.1.0",
                }
            ],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        queries = read_gold_set(jsonl_file)

        assert len(queries) == 1
        assert queries[0].query_id == "q1"
        assert queries[0].question == "What is Python?"
        assert len(queries[0].anchors) == 1
        assert queries[0].anchors[0].document_id == "doc1"
        assert queries[0].anchors[0].start == 0
        assert queries[0].anchors[0].end == 10

    def test_read_multiple_queries(self, tmp_path: Path) -> None:
        """Test reading multiple queries from JSONL."""
        jsonl_file = tmp_path / "gold.jsonl"
        queries_data = [
            {
                "query_id": "q1",
                "question": "First question?",
                "anchors": [],
                "schema_version": "0.1.0",
            },
            {
                "query_id": "q2",
                "question": "Second question?",
                "anchors": [
                    {
                        "document_id": "doc2",
                        "start": 5,
                        "end": 15,
                        "expected_text_hash": "hash2",
                        "schema_version": "0.1.0",
                    }
                ],
                "schema_version": "0.1.0",
            },
        ]
        with jsonl_file.open("w") as f:
            for q in queries_data:
                f.write(json.dumps(q) + "\n")

        queries = read_gold_set(jsonl_file)

        assert len(queries) == 2
        assert queries[0].query_id == "q1"
        assert queries[1].query_id == "q2"
        assert len(queries[0].anchors) == 0
        assert len(queries[1].anchors) == 1

    def test_read_skips_empty_lines(self, tmp_path: Path) -> None:
        """Test that empty lines are skipped."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "anchors": [],
            "schema_version": "0.1.0",
        }
        with jsonl_file.open("w") as f:
            f.write("\n")  # Empty line
            f.write(json.dumps(data) + "\n")
            f.write("\n")  # Another empty line

        queries = read_gold_set(jsonl_file)

        assert len(queries) == 1
        assert queries[0].query_id == "q1"

    def test_duplicate_query_id_raises_error(self, tmp_path: Path) -> None:
        """Test that duplicate query_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "anchors": [],
            "schema_version": "0.1.0",
        }
        with jsonl_file.open("w") as f:
            f.write(json.dumps(data) + "\n")
            f.write(json.dumps(data) + "\n")  # Duplicate

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Duplicate query_id" in str(exc_info.value)
        assert "q1" in str(exc_info.value)
        assert "Line: 2" in str(exc_info.value)

    def test_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """Test that malformed JSON raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        jsonl_file.write_text("{ invalid json }\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Invalid JSON" in str(exc_info.value)
        assert "Line: 1" in str(exc_info.value)

    def test_missing_schema_version_raises_error(self, tmp_path: Path) -> None:
        """Test that missing schema_version raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "anchors": [],
            # Missing schema_version
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Missing required field 'schema_version'" in str(exc_info.value)
        assert "Field: schema_version" in str(exc_info.value)

    def test_missing_query_id_raises_error(self, tmp_path: Path) -> None:
        """Test that missing query_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "question": "Test?",
            "anchors": [],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Missing required field 'query_id'" in str(exc_info.value)

    def test_missing_question_raises_error(self, tmp_path: Path) -> None:
        """Test that missing question raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "anchors": [],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Missing required field 'question'" in str(exc_info.value)

    def test_missing_anchors_raises_error(self, tmp_path: Path) -> None:
        """Test that missing anchors field raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Missing required field 'anchors'" in str(exc_info.value)

    def test_non_string_query_id_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string query_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": 123,  # Should be string
            "question": "Test?",
            "anchors": [],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "must be a string" in str(exc_info.value)
        assert "query_id" in str(exc_info.value)

    def test_non_string_question_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string question raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": 456,  # Should be string
            "anchors": [],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "must be a string" in str(exc_info.value)
        assert "question" in str(exc_info.value)

    def test_non_list_anchors_raises_error(self, tmp_path: Path) -> None:
        """Test that non-list anchors raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "anchors": "not a list",
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "must be a list" in str(exc_info.value)
        assert "anchors" in str(exc_info.value)

    def test_anchor_missing_field_raises_error(self, tmp_path: Path) -> None:
        """Test that anchor missing required field raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
            "query_id": "q1",
            "question": "Test?",
            "anchors": [
                {
                    "document_id": "doc1",
                    "start": 0,
                    # Missing 'end'
                    "expected_text_hash": "hash",
                }
            ],
            "schema_version": "0.1.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "missing field 'end'" in str(exc_info.value)
        assert "anchors[0]" in str(exc_info.value)

    def test_anchor_wrong_type_raises_error(self, tmp_path: Path) -> None:
        """Test that anchor field with wrong type raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        data = {
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
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "must be int" in str(exc_info.value)
        assert "start" in str(exc_info.value)

    def test_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Test that missing file raises InvalidSchemaError."""
        jsonl_file = tmp_path / "nonexistent.jsonl"

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "File not found" in str(exc_info.value)

    def test_non_dict_json_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dictionary JSON raises InvalidSchemaError."""
        jsonl_file = tmp_path / "gold.jsonl"
        jsonl_file.write_text('["not", "a", "dict"]\n')

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_gold_set(jsonl_file)

        assert "Expected JSON object" in str(exc_info.value)


class TestWriteGoldSet:
    """Tests for write_gold_set function."""

    def test_write_single_query(self, tmp_path: Path) -> None:
        """Test writing a single query to JSONL."""
        jsonl_file = tmp_path / "output.jsonl"
        anchor = Anchor("doc1", 0, 10, "hash123", "0.1.0")
        query = Query("q1", "What is X?", (anchor,), "0.1.0")

        write_gold_set(jsonl_file, [query])

        # Read back and verify
        content = jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1

        data = json.loads(lines[0])
        assert data["query_id"] == "q1"
        assert data["question"] == "What is X?"
        assert data["schema_version"] == "0.1.0"
        assert len(data["anchors"]) == 1
        assert data["anchors"][0]["document_id"] == "doc1"

    def test_write_multiple_queries(self, tmp_path: Path) -> None:
        """Test writing multiple queries to JSONL."""
        jsonl_file = tmp_path / "output.jsonl"
        queries = [
            Query("q1", "First?", (), "0.1.0"),
            Query("q2", "Second?", (), "0.1.0"),
            Query("q3", "Third?", (), "0.1.0"),
        ]

        write_gold_set(jsonl_file, queries)

        content = jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3

        ids = [json.loads(line)["query_id"] for line in lines]
        assert ids == ["q1", "q2", "q3"]

    def test_write_query_with_multiple_anchors(self, tmp_path: Path) -> None:
        """Test writing a query with multiple anchors."""
        jsonl_file = tmp_path / "output.jsonl"
        anchors = (
            Anchor("doc1", 0, 10, "hash1", "0.1.0"),
            Anchor("doc2", 20, 30, "hash2", "0.1.0"),
        )
        query = Query("q1", "Multi-anchor?", anchors, "0.1.0")

        write_gold_set(jsonl_file, [query])

        content = jsonl_file.read_text()
        data = json.loads(content)
        assert len(data["anchors"]) == 2
        assert data["anchors"][0]["document_id"] == "doc1"
        assert data["anchors"][1]["document_id"] == "doc2"

    def test_write_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test that write_gold_set creates parent directories."""
        jsonl_file = tmp_path / "subdir" / "nested" / "output.jsonl"
        query = Query("q1", "Test?", (), "0.1.0")

        write_gold_set(jsonl_file, [query])

        assert jsonl_file.exists()
        assert jsonl_file.parent.exists()

    def test_write_empty_list(self, tmp_path: Path) -> None:
        """Test writing an empty list of queries."""
        jsonl_file = tmp_path / "output.jsonl"

        write_gold_set(jsonl_file, [])

        content = jsonl_file.read_text()
        assert content == ""

    def test_roundtrip_preserves_data(self, tmp_path: Path) -> None:
        """Test that write then read preserves all data."""
        jsonl_file = tmp_path / "roundtrip.jsonl"
        anchors = (
            Anchor("doc1", 5, 15, "hash_abc", "0.1.0"),
            Anchor("doc2", 100, 200, "hash_xyz", "0.1.0"),
        )
        original_queries = [
            Query("q1", "First question?", anchors, "0.1.0"),
            Query("q2", "Second question?", (), "0.1.0"),
        ]

        write_gold_set(jsonl_file, original_queries)
        loaded_queries = read_gold_set(jsonl_file)

        assert len(loaded_queries) == len(original_queries)
        for orig, loaded in zip(original_queries, loaded_queries):
            assert orig.query_id == loaded.query_id
            assert orig.question == loaded.question
            assert orig.schema_version == loaded.schema_version
            assert len(orig.anchors) == len(loaded.anchors)
            for orig_anchor, loaded_anchor in zip(orig.anchors, loaded.anchors):
                assert orig_anchor.document_id == loaded_anchor.document_id
                assert orig_anchor.start == loaded_anchor.start
                assert orig_anchor.end == loaded_anchor.end
                assert orig_anchor.expected_text_hash == loaded_anchor.expected_text_hash

    def test_write_unicode_content(self, tmp_path: Path) -> None:
        """Test writing queries with unicode characters."""
        jsonl_file = tmp_path / "unicode.jsonl"
        query = Query("q1", "What is 日本語?", (), "0.1.0")

        write_gold_set(jsonl_file, [query])

        loaded_queries = read_gold_set(jsonl_file)
        assert loaded_queries[0].question == "What is 日本語?"
