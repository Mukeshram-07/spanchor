"""Unit tests for CLI gold extract command.

Tests cover:
- CLI command invocation (help, arguments)
- JSONL output format validation
- Error handling (missing directory, missing output flag)
- End-to-end extraction with real files

**Validates: Feature 7 - Gold-Set Generation (Minimal) - CLI**
"""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spanchor.cli import app

runner = CliRunner()


class TestGoldExtractCommand:
    """Tests for 'spanchor gold extract' CLI command."""

    def test_gold_extract_help(self) -> None:
        """Help text displays correctly for gold extract command."""
        result = runner.invoke(app, ["gold", "extract", "--help"])
        assert result.exit_code == 0
        assert "extract" in result.stdout.lower()
        assert "candidates" in result.stdout.lower()

    def test_gold_extract_missing_args(self) -> None:
        """Command fails without required arguments."""
        result = runner.invoke(app, ["gold", "extract"])
        assert result.exit_code != 0

    def test_gold_extract_missing_output_flag(self) -> None:
        """Command fails without output flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            # Create a sample document
            (docs_dir / "test.txt").write_text("Hello world.", encoding="utf-8")

            result = runner.invoke(app, ["gold", "extract", str(docs_dir)])
            assert result.exit_code != 0
            # Error message may be in stdout or mix/output parameter may not be recognized
            output = result.stdout + result.stderr if result.stderr else result.stdout
            assert "missing" in output.lower() or "required" in output.lower() or result.exit_code == 2

    def test_gold_extract_nonexistent_directory(self) -> None:
        """Command fails with non-existent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "output.jsonl"
            result = runner.invoke(
                app,
                [
                    "gold",
                    "extract",
                    "/nonexistent/directory",
                    "-o",
                    str(output_file),
                ],
            )
            assert result.exit_code != 0

    def test_gold_extract_empty_directory(self) -> None:
        """Command fails with empty document directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code != 0
            output = result.stdout + result.stderr if result.stderr else result.stdout
            assert "no documents" in output.lower()

    def test_gold_extract_single_document(self) -> None:
        """Extract candidates from single document produces JSONL output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            # Create a sample document
            (docs_dir / "test.txt").write_text(
                "Hello world. How are you?", encoding="utf-8"
            )

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0
            assert "extracted" in result.stdout.lower()
            assert output_file.exists()

    def test_gold_extract_jsonl_format(self) -> None:
        """Output file is valid JSONL with required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            # Create a sample document
            (docs_dir / "test.txt").write_text(
                "First sentence. Second sentence.", encoding="utf-8"
            )

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0

            # Validate JSONL format and content
            lines = output_file.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 2

            for line in lines:
                candidate = json.loads(line)
                assert "candidate_id" in candidate
                assert "text" in candidate
                assert "document_id" in candidate
                assert "confidence" in candidate
                assert "schema_version" in candidate

                # Validate field types and ranges
                assert isinstance(candidate["candidate_id"], str)
                assert isinstance(candidate["text"], str)
                assert isinstance(candidate["document_id"], str)
                assert isinstance(candidate["confidence"], (int, float))
                assert 0.0 <= candidate["confidence"] <= 1.0

    def test_gold_extract_multiple_documents(self) -> None:
        """Extract from multiple documents produces candidates for all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            # Create multiple sample documents
            (docs_dir / "doc1.txt").write_text("First. Second.", encoding="utf-8")
            (docs_dir / "doc2.txt").write_text("Third. Fourth.", encoding="utf-8")

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0

            # Validate output
            lines = output_file.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 4  # 2 sentences per document

            # Check document_ids
            doc1_count = 0
            doc2_count = 0
            for line in lines:
                candidate = json.loads(line)
                if candidate["document_id"] == "doc1":
                    doc1_count += 1
                elif candidate["document_id"] == "doc2":
                    doc2_count += 1

            assert doc1_count == 2
            assert doc2_count == 2

    def test_gold_extract_deduplication_shown_in_count(self) -> None:
        """Deduplication reduces extracted candidate count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            # Create document with duplicate sentences
            (docs_dir / "test.txt").write_text(
                "Same sentence. Different sentence. Same sentence.",  # typo in repeat
                encoding="utf-8",
            )

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0

            # Should have fewer extracted candidates than raw sentences due to dedup
            lines = output_file.read_text(encoding="utf-8").strip().split("\n")
            # Expect 2 unique candidates (first "Same" and "Different", second "Same" deduplicated)
            assert len(lines) == 2

    def test_gold_extract_realworld_document(self) -> None:
        """Extract from realistic RAG-related document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            # Create a realistic multi-sentence document
            text = (
                "Retrieval-Augmented Generation (RAG) is a technique that enhances "
                "large language model outputs by grounding them in retrieved source documents. "
                "Instead of relying solely on parametric knowledge baked into model weights, "
                "RAG pipelines fetch relevant passages at inference time and pass them as context to the model. "
                "This approach reduces hallucinations and keeps answers up to date without retraining."
            )
            (docs_dir / "rag.txt").write_text(text, encoding="utf-8")

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0

            lines = output_file.read_text(encoding="utf-8").strip().split("\n")
            # Should have multiple sentences
            assert len(lines) > 0

            # All should be from same document
            for line in lines:
                candidate = json.loads(line)
                assert candidate["document_id"] == "rag"

    def test_gold_extract_output_flag_short_form(self) -> None:
        """Short form -o flag works for output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            (docs_dir / "test.txt").write_text("Test.", encoding="utf-8")

            # Use short form -o
            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0
            assert output_file.exists()

    def test_gold_extract_output_flag_long_form(self) -> None:
        """Long form --output flag works for output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            (docs_dir / "test.txt").write_text("Test.", encoding="utf-8")

            # Use long form --output
            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "--output", str(output_file)],
            )
            assert result.exit_code == 0
            assert output_file.exists()

    def test_gold_extract_candidate_ids_match_document(self) -> None:
        """Candidate IDs contain the document_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir)
            output_file = Path(tmpdir) / "output.jsonl"

            (docs_dir / "mydoc.txt").write_text("First. Second.", encoding="utf-8")

            result = runner.invoke(
                app,
                ["gold", "extract", str(docs_dir), "-o", str(output_file)],
            )
            assert result.exit_code == 0

            lines = output_file.read_text(encoding="utf-8").strip().split("\n")
            for i, line in enumerate(lines):
                candidate = json.loads(line)
                assert candidate["candidate_id"] == f"mydoc_{i}"
                assert candidate["document_id"] == "mydoc"
