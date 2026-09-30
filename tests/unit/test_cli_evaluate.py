"""Unit tests for the CLI evaluate command.

Tests cover:
- Req 18.1: load docs, gold set, and retrieval results; run evaluation
- Req 18.2: chunk-text results are mapped to spans via evaluate()
- Req 18.3: aggregate metrics are printed to stdout
- Req 18.4: --output writes Run JSON via write_run()
- Req 18.5: --report writes markdown report via generate_evaluation_report()
- Req 18.6: --redact omits source text from reports
- Req 18.7: exit code 0 on success
- Req 13.7: exit code 3 when unmapped chunk rate exceeds max_unmapped_rate
- Req 13.8: exit code 2 on schema/usage errors
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spanchor.canonical.normalize import compute_hash
from spanchor.cli import app
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


def _make_results(query_id: str, doc_id: str, start: int, end: int, rank: int = 1) -> dict:
    """Produce a retrieval results dict (span form)."""
    return {
        query_id: [
            {"rank": rank, "score": 0.9, "document_id": doc_id, "start": start, "end": end}
        ]
    }


def _setup_corpus(tmp_path: Path, doc_text: str = "The quick brown fox") -> tuple[Path, Path, Path]:
    """Create docs_dir, gold JSONL, and results JSON; return their paths."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "doc1.txt").write_text(doc_text, encoding="utf-8")

    doc = Document.from_text("doc1", doc_text)
    text_hash = compute_hash(doc.text[0:3])  # "The"

    gold = tmp_path / "gold.jsonl"
    gold.write_text(
        _make_gold_line("q1", "doc1", 0, 3, text_hash, question="What is the article?"),
        encoding="utf-8",
    )

    results = tmp_path / "results.json"
    results.write_text(
        json.dumps(_make_results("q1", "doc1", 0, 3)),
        encoding="utf-8",
    )

    return docs_dir, gold, results


def _invoke_evaluate(
    docs_dir: Path,
    gold: Path,
    results: Path,
    extra_args: list[str] | None = None,
) -> object:
    """Invoke the evaluate subcommand."""
    args = ["evaluate", str(docs_dir), str(gold), str(results)]
    if extra_args:
        args += extra_args
    return runner.invoke(app, args)


# ---------------------------------------------------------------------------
# Success paths
# ---------------------------------------------------------------------------


class TestEvaluateCommandSuccess:
    def test_exits_code_0_on_success(self, tmp_path: Path) -> None:
        """Req 18.7 – exit code 0 on success."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        result = _invoke_evaluate(docs_dir, gold, results)
        assert result.exit_code == 0, result.output

    def test_prints_aggregate_metrics(self, tmp_path: Path) -> None:
        """Req 18.3 – aggregate metrics appear in stdout."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        result = _invoke_evaluate(docs_dir, gold, results)
        assert result.exit_code == 0
        # At least one @k metric should appear
        assert "@" in result.output or "recall" in result.output or "iou" in result.output

    def test_output_flag_writes_run_json(self, tmp_path: Path) -> None:
        """Req 18.4 – --output writes a valid Run JSON file."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        out_path = tmp_path / "run.json"
        result = _invoke_evaluate(docs_dir, gold, results, ["--output", str(out_path)])
        assert result.exit_code == 0
        assert out_path.exists(), "Run JSON file was not created"

        # Validate it's a proper Run JSON
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert "schema_version" in data
        assert "aggregate_metrics" in data
        assert "per_query_metrics" in data

    def test_report_flag_writes_markdown(self, tmp_path: Path) -> None:
        """Req 18.5 – --report writes a markdown file."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        report_path = tmp_path / "report.md"
        result = _invoke_evaluate(docs_dir, gold, results, ["--report", str(report_path)])
        assert result.exit_code == 0
        assert report_path.exists(), "Markdown report was not created"
        content = report_path.read_text(encoding="utf-8")
        assert "# Evaluation Report" in content

    def test_redact_omits_question_from_report(self, tmp_path: Path) -> None:
        """Req 18.6 – --redact omits question text from markdown report."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        report_path = tmp_path / "report.md"
        result = _invoke_evaluate(
            docs_dir, gold, results,
            ["--report", str(report_path), "--redact"],
        )
        assert result.exit_code == 0
        content = report_path.read_text(encoding="utf-8")
        # The question text should NOT appear in the redacted report
        assert "What is the article?" not in content

    def test_redact_omits_question_from_output_run(self, tmp_path: Path) -> None:
        """Req 18.6 – --redact omits question text from run JSON output."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        out_path = tmp_path / "run.json"
        result = _invoke_evaluate(
            docs_dir, gold, results,
            ["--output", str(out_path), "--redact"],
        )
        assert result.exit_code == 0
        data = json.loads(out_path.read_text(encoding="utf-8"))
        # Questions should be redacted (empty string) in the run JSON
        for query_dict in data.get("queries", []):
            assert query_dict.get("question", "") == ""

    def test_custom_k_is_used(self, tmp_path: Path) -> None:
        """--k option is passed through to evaluate()."""
        docs_dir, gold, results = _setup_corpus(tmp_path)
        out_path = tmp_path / "run.json"
        result = _invoke_evaluate(
            docs_dir, gold, results,
            ["--k", "10", "--output", str(out_path)],
        )
        assert result.exit_code == 0
        data = json.loads(out_path.read_text(encoding="utf-8"))
        # Config should reflect k=10
        assert data["config"]["k"] == 10

    def test_no_results_for_query_exits_0(self, tmp_path: Path) -> None:
        """Query with no retrieval results still evaluates (metrics all 0)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        doc_text = "Hello world test"
        (docs_dir / "doc1.txt").write_text(doc_text, encoding="utf-8")

        doc = Document.from_text("doc1", doc_text)
        text_hash = compute_hash(doc.text[0:5])
        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 5, text_hash),
            encoding="utf-8",
        )

        # Results file with no entries for q1
        results = tmp_path / "results.json"
        results.write_text(json.dumps({}), encoding="utf-8")

        result = _invoke_evaluate(docs_dir, gold, results)
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


class TestEvaluateCommandErrors:
    def test_missing_docs_dir_exits_code_2(self, tmp_path: Path) -> None:
        """Req 13.8 – non-existent docs_dir causes Typer BadParameter → exit 2."""
        gold = tmp_path / "gold.jsonl"
        gold.write_text("{}", encoding="utf-8")
        results = tmp_path / "results.json"
        results.write_text("{}", encoding="utf-8")
        result = runner.invoke(
            app,
            ["evaluate", str(tmp_path / "nonexistent"), str(gold), str(results)],
        )
        assert result.exit_code == 2

    def test_malformed_gold_exits_code_2(self, tmp_path: Path) -> None:
        """Req 13.8 – malformed gold JSONL → InvalidSchemaError → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text("{not valid json\n", encoding="utf-8")

        results = tmp_path / "results.json"
        results.write_text("{}", encoding="utf-8")

        result = _invoke_evaluate(docs_dir, gold, results)
        assert result.exit_code == 2

    def test_malformed_results_exits_code_2(self, tmp_path: Path) -> None:
        """Req 13.8 – malformed results JSON → InvalidSchemaError → exit 2."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "doc1.txt").write_text("Hello", encoding="utf-8")

        gold = tmp_path / "gold.jsonl"
        gold.write_text("", encoding="utf-8")  # empty gold is valid

        results = tmp_path / "results.json"
        results.write_text("{not valid json", encoding="utf-8")

        result = _invoke_evaluate(docs_dir, gold, results)
        assert result.exit_code == 2

    def test_unmapped_rate_exceeded_exits_code_3(self, tmp_path: Path) -> None:
        """Req 13.7 – unmapped chunk rate > max_unmapped_rate → exit 3."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        doc_text = "The quick brown fox jumps"
        (docs_dir / "doc1.txt").write_text(doc_text, encoding="utf-8")

        doc = Document.from_text("doc1", doc_text)
        text_hash = compute_hash(doc.text[0:3])
        gold = tmp_path / "gold.jsonl"
        gold.write_text(
            _make_gold_line("q1", "doc1", 0, 3, text_hash),
            encoding="utf-8",
        )

        # Chunk-text result that won't map to anything in the doc
        results = tmp_path / "results.json"
        results.write_text(
            json.dumps({
                "q1": [
                    {
                        "rank": 1,
                        "score": 0.5,
                        "text": "zzz_completely_unrecognizable_text_that_wont_map_anywhere",
                    }
                ]
            }),
            encoding="utf-8",
        )

        # Set max_unmapped_rate to 0 so any unmapped result triggers exit 3
        result = _invoke_evaluate(
            docs_dir, gold, results,
            ["--max-unmapped-rate", "0.0"],
        )
        assert result.exit_code == 3
