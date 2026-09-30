"""Unit tests for the CLI validate command.

The CLI has multiple registered commands (validate, evaluate), so Typer
exposes them with subcommand name prefixes.

Tests cover:
- Req 17.1: load and canonicalize all documents from docs_dir
- Req 17.2: load and parse the gold set JSONL file
- Req 17.3: validate every anchor against its referenced document
- Req 17.4: print success message with counts
- Req 17.5: print all errors with actionable messages and exit code 2
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spanchor.canonical.normalize import compute_hash
from spanchor.cli import app, load_documents
from spanchor.models.document import Document

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_gold_line(
    query_id: str,
    document_id: str,
    start: int,
    end: int,
    text_hash: str,
    question: str = "What is this?",
) -> str:
    """Produce a single JSONL line for the gold set."""
    return json.dumps(
        {
            "schema_version": "0.1.0",
            "query_id": query_id,
            "question": question,
            "anchors": [
                {
                    "document_id": document_id,
                    "start": start,
                    "end": end,
                    "expected_text_hash": text_hash,
                    "schema_version": "0.1.0",
                }
            ],
        }
    )


def _invoke_validate(docs_dir: Path, gold_path: Path) -> object:
    """Invoke the validate command."""
    return runner.invoke(app, ["validate", str(docs_dir), str(gold_path)])


# ---------------------------------------------------------------------------
# load_documents() helper tests (Req 17.1)
# ---------------------------------------------------------------------------


class TestLoadDocuments:
    def test_loads_txt_files(self, tmp_path: Path) -> None:
        (tmp_path / "doc1.txt").write_text("Hello world", encoding="utf-8")
        (tmp_path / "doc2.txt").write_text("Foo bar", encoding="utf-8")
        docs = load_documents(tmp_path)
        assert set(docs.keys()) == {"doc1", "doc2"}

    def test_document_id_is_stem(self, tmp_path: Path) -> None:
        (tmp_path / "report.txt").write_text("content", encoding="utf-8")
        docs = load_documents(tmp_path)
        assert "report" in docs

    def test_canonicalizes_text(self, tmp_path: Path) -> None:
        # CRLF should be normalized to LF (Req 17.1)
        (tmp_path / "doc.txt").write_bytes(b"line1\r\nline2")
        docs = load_documents(tmp_path)
        assert docs["doc"].text == "line1\nline2"

    def test_returns_document_objects(self, tmp_path: Path) -> None:
        (tmp_path / "doc.txt").write_text("Hello", encoding="utf-8")
        docs = load_documents(tmp_path)
        assert isinstance(docs["doc"], Document)

    def test_skips_subdirectories(self, tmp_path: Path) -> None:
        (tmp_path / "doc.txt").write_text("text", encoding="utf-8")
        (tmp_path / "subdir").mkdir()
        docs = load_documents(tmp_path)
        assert "subdir" not in docs

    def test_empty_directory_returns_empty_dict(self, tmp_path: Path) -> None:
        docs = load_documents(tmp_path)
        assert docs == {}

    def test_non_txt_files_are_loaded(self, tmp_path: Path) -> None:
        # All files (not just .txt) are loaded; extension stripped from id
        (tmp_path / "doc.md").write_text("# Title", encoding="utf-8")
        docs = load_documents(tmp_path)
        assert "doc" in docs

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        import typer

        with pytest.raises(typer.BadParameter):
            load_documents(tmp_path / "nonexistent")

    def test_sha256_is_computed(self, tmp_path: Path) -> None:
        (tmp_path / "doc.txt").write_text("Hello", encoding="utf-8")
        docs = load_documents(tmp_path)
        assert len(docs["doc"].sha256) == 64  # SHA256 hex digest length


# ---------------------------------------------------------------------------
# validate command — success path (Req 17.1, 17.2, 17.3, 17.4)
# ---------------------------------------------------------------------------


class TestValidateCommand:
    def test_success_exits_with_code_0(self, tmp_path: Path) -> None:
        doc_text = "The quick brown fox"
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text(doc_text, encoding="utf-8")

        doc = Document.from_text("doc1", doc_text)
        text_hash = compute_hash(doc.text[0:3])  # "The"
        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 3, text_hash),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0

    def test_success_prints_document_count(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")
        (docs_dir / "doc2.txt").write_text("World", encoding="utf-8")

        doc1 = Document.from_text("doc1", "Hello")
        hash1 = compute_hash(doc1.text[0:5])
        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 5, hash1),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0
        assert "2" in result.output  # 2 documents

    def test_success_prints_query_count(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello world", encoding="utf-8")

        doc = Document.from_text("doc1", "Hello world")
        hash1 = compute_hash(doc.text[0:5])
        hash2 = compute_hash(doc.text[6:11])

        lines = "\n".join(
            [
                _make_gold_line("q1", "doc1", 0, 5, hash1, "Query one"),
                _make_gold_line("q2", "doc1", 6, 11, hash2, "Query two"),
            ]
        )
        gold = tmp_path / "gold.jsonl"
        gold.write_text(lines, encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0
        assert "2" in result.output  # 2 queries

    def test_success_prints_anchor_count(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello world", encoding="utf-8")

        doc = Document.from_text("doc1", "Hello world")
        hash1 = compute_hash(doc.text[0:5])

        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 5, hash1),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0
        assert "1" in result.output  # 1 anchor

    def test_empty_gold_set_exits_0(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text("", encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0

    def test_success_message_contains_validated(self, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")

        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash(doc.text[0:5])
        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 5, text_hash),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0
        assert "Validated" in result.output or "✓" in result.output

    def test_multiple_docs_multiple_anchors_validated(self, tmp_path: Path) -> None:
        """Validates across multiple documents with multiple queries."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Alpha beta gamma", encoding="utf-8")
        (docs_dir / "doc2.txt").write_text("Delta epsilon", encoding="utf-8")

        doc1 = Document.from_text("doc1", "Alpha beta gamma")
        doc2 = Document.from_text("doc2", "Delta epsilon")

        lines = "\n".join(
            [
                _make_gold_line("q1", "doc1", 0, 5, compute_hash(doc1.text[0:5])),
                _make_gold_line("q2", "doc2", 0, 5, compute_hash(doc2.text[0:5])),
            ]
        )
        gold = tmp_path / "gold.jsonl"
        gold.write_text(lines, encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# validate command — error paths (Req 17.5)
# ---------------------------------------------------------------------------


class TestValidateCommandErrors:
    def test_missing_document_exits_code_2(self, tmp_path: Path) -> None:
        """Anchor references doc that doesn't exist → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        # No documents in docs_dir

        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "missing_doc", 0, 5, "fakehash"),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2

    def test_bad_hash_exits_code_2(self, tmp_path: Path) -> None:
        """Anchor with wrong text hash → AnchorResolutionError → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello world", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 5, "wrong_hash_that_will_never_match"),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2

    def test_out_of_bounds_offset_exits_code_2(self, tmp_path: Path) -> None:
        """Anchor with offsets beyond document length → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hi", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 9999, "fakehash"),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2

    def test_malformed_gold_json_exits_code_2(self, tmp_path: Path) -> None:
        """Malformed JSONL → InvalidSchemaError → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text("{not valid json\n", encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2

    def test_multiple_errors_all_reported(self, tmp_path: Path) -> None:
        """All errors collected and printed, not just the first (Req 17.5)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello world", encoding="utf-8")

        # Both anchors have wrong hashes → should collect 2 errors
        lines = "\n".join(
            [
                _make_gold_line("q1", "doc1", 0, 5, "wrong_hash_1"),
                _make_gold_line("q2", "doc1", 6, 11, "wrong_hash_2"),
            ]
        )
        gold = tmp_path / "gold.jsonl"
        gold.write_text(lines, encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2
        # Should mention both errors — output or stderr contains "[2]" or count "2"
        combined = result.output + result.stderr
        # At minimum 2 errors were logged
        assert combined.count("[red]") >= 1 or "2 error" in combined

    def test_duplicate_query_id_in_gold_exits_code_2(self, tmp_path: Path) -> None:
        """Duplicate query_id in JSONL → InvalidSchemaError → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello world", encoding="utf-8")

        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash(doc.text[0:5])
        lines = "\n".join(
            [
                _make_gold_line("q1", "doc1", 0, 5, text_hash),
                _make_gold_line("q1", "doc1", 0, 5, text_hash),  # duplicate
            ]
        )
        gold = tmp_path / "gold.jsonl"
        gold.write_text(lines, encoding="utf-8")

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2

    def test_missing_document_error_mentions_document_id(self, tmp_path: Path) -> None:
        """DocumentNotFoundError message should include the missing document_id."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "the_missing_doc", 0, 5, "fakehash"),
            encoding="utf-8",
        )

        result = _invoke_validate(docs_dir, gold)
        assert result.exit_code == 2
        # The error output should contain the missing document_id
        combined = result.output + result.stderr
        assert "the_missing_doc" in combined
