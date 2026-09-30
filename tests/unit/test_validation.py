"""Unit tests for check_corpus() in spanchor.validation.

Covers:
  - Healthy corpus (no issues)
  - Missing document (DocumentNotFoundError captured)
  - Hash / text mismatch (AnchorResolutionError captured)
  - Out-of-bounds offsets (AnchorResolutionError captured)
  - Multiple errors collected (no early exit)
  - Queries with zero anchors produce no issues
  - Public API export (req 26.6)
"""

from __future__ import annotations

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.validation import CorpusIssue, check_corpus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc(doc_id: str, text: str) -> Document:
    return Document.from_text(doc_id, text)


def _valid_anchor(doc: Document, start: int, end: int) -> Anchor:
    """Create an anchor whose expected_text_hash matches the real span."""
    span_text = doc.text[start:end]
    return Anchor(
        document_id=doc.document_id,
        start=start,
        end=end,
        expected_text_hash=compute_hash(span_text),
    )


def _query(query_id: str, *anchors: Anchor) -> Query:
    return Query(query_id=query_id, question="?", anchors=tuple(anchors))


# ---------------------------------------------------------------------------
# Tests: happy path
# ---------------------------------------------------------------------------

class TestCheckCorpusHealthy:
    def test_empty_queries_returns_no_issues(self) -> None:
        """No queries → no issues."""
        docs: dict[str, Document] = {}
        issues = check_corpus(docs, [])
        assert issues == []

    def test_query_with_no_anchors_returns_no_issues(self) -> None:
        """Query with zero anchors does not generate any issues."""
        doc = _doc("doc1", "Hello world")
        query = _query("q1")  # no anchors
        issues = check_corpus({"doc1": doc}, [query])
        assert issues == []

    def test_valid_anchor_returns_no_issues(self) -> None:
        """A valid anchor against a matching document produces no issues."""
        doc = _doc("doc1", "Hello world")
        anchor = _valid_anchor(doc, 0, 5)  # "Hello"
        issues = check_corpus({"doc1": doc}, [_query("q1", anchor)])
        assert issues == []

    def test_multiple_valid_anchors_returns_no_issues(self) -> None:
        """Multiple valid anchors across multiple queries produce no issues."""
        doc1 = _doc("doc1", "Hello world")
        doc2 = _doc("doc2", "Goodbye world")
        a1 = _valid_anchor(doc1, 0, 5)   # "Hello"
        a2 = _valid_anchor(doc2, 0, 7)   # "Goodbye"
        queries = [_query("q1", a1), _query("q2", a2)]
        issues = check_corpus({"doc1": doc1, "doc2": doc2}, queries)
        assert issues == []

    def test_returns_list_type(self) -> None:
        """Return value is always a list."""
        result = check_corpus({}, [])
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Tests: missing document (req 20.1)
# ---------------------------------------------------------------------------

class TestMissingDocument:
    def test_missing_document_creates_issue(self) -> None:
        """Anchor referencing a missing document_id generates a CorpusIssue."""
        anchor = Anchor(
            document_id="missing_doc",
            start=0,
            end=5,
            expected_text_hash="x" * 64,
        )
        issues = check_corpus({}, [_query("q1", anchor)])
        assert len(issues) == 1
        issue = issues[0]
        assert issue.query_id == "q1"
        assert issue.document_id == "missing_doc"
        assert "missing_doc" in issue.message

    def test_missing_document_skips_further_validation(self) -> None:
        """When document is missing no additional issues are raised for that anchor."""
        anchor = Anchor(
            document_id="ghost",
            start=0,
            end=5,
            expected_text_hash="x" * 64,
        )
        issues = check_corpus({}, [_query("q1", anchor)])
        # Only one issue (missing doc), not an extra one for bad hash/offsets
        assert len(issues) == 1


# ---------------------------------------------------------------------------
# Tests: hash / text mismatch (req 20.1, 20.3)
# ---------------------------------------------------------------------------

class TestHashMismatch:
    def test_wrong_text_hash_creates_issue(self) -> None:
        """Anchor whose expected_text_hash does not match actual text generates a CorpusIssue."""
        doc = _doc("doc1", "Hello world")
        bad_anchor = Anchor(
            document_id="doc1",
            start=0,
            end=5,
            expected_text_hash=compute_hash("XXXXX"),  # doesn't match "Hello"
        )
        issues = check_corpus({"doc1": doc}, [_query("q1", bad_anchor)])
        assert len(issues) == 1
        assert issues[0].query_id == "q1"
        assert issues[0].document_id == "doc1"

    def test_correct_text_hash_no_issue(self) -> None:
        """Anchor with correct text hash passes validation."""
        doc = _doc("doc1", "Hello world")
        good_anchor = _valid_anchor(doc, 0, 5)
        issues = check_corpus({"doc1": doc}, [_query("q1", good_anchor)])
        assert issues == []


# ---------------------------------------------------------------------------
# Tests: offset out of bounds (req 20.2)
# ---------------------------------------------------------------------------

class TestOffsetBounds:
    def test_end_beyond_document_length_creates_issue(self) -> None:
        """Anchor with end > len(doc.text) generates a CorpusIssue."""
        doc = _doc("doc1", "Hi")  # length = 2
        anchor = Anchor(
            document_id="doc1",
            start=0,
            end=100,  # out of bounds
            expected_text_hash=compute_hash("Hi"),
        )
        issues = check_corpus({"doc1": doc}, [_query("q1", anchor)])
        assert len(issues) == 1
        assert "doc1" in issues[0].document_id

    def test_negative_start_creates_issue(self) -> None:
        """Anchor with negative start generates a CorpusIssue."""
        doc = _doc("doc1", "Hello")
        anchor = Anchor(
            document_id="doc1",
            start=-1,
            end=5,
            expected_text_hash=compute_hash("Hello"),
        )
        issues = check_corpus({"doc1": doc}, [_query("q1", anchor)])
        assert len(issues) == 1

    def test_start_greater_than_end_creates_issue(self) -> None:
        """Anchor where start > end generates a CorpusIssue."""
        doc = _doc("doc1", "Hello world")
        anchor = Anchor(
            document_id="doc1",
            start=5,
            end=2,  # invalid: start > end
            expected_text_hash=compute_hash(""),
        )
        issues = check_corpus({"doc1": doc}, [_query("q1", anchor)])
        assert len(issues) == 1

    def test_valid_bounds_no_issue(self) -> None:
        """Anchor with valid bounds passes bounds check."""
        doc = _doc("doc1", "Hello world")
        anchor = _valid_anchor(doc, 6, 11)  # "world"
        issues = check_corpus({"doc1": doc}, [_query("q1", anchor)])
        assert issues == []


# ---------------------------------------------------------------------------
# Tests: all errors collected (req 20.4 behaviour)
# ---------------------------------------------------------------------------

class TestAllErrorsCollected:
    def test_multiple_bad_anchors_all_reported(self) -> None:
        """All invalid anchors are reported, not just the first one."""
        doc = _doc("doc1", "Hello world")

        bad1 = Anchor("doc1", 0, 5, compute_hash("XXXXX"))  # text mismatch
        bad2 = Anchor("doc1", 0, 999, compute_hash("Hello"))  # out of bounds

        query = _query("q1", bad1, bad2)
        issues = check_corpus({"doc1": doc}, [query])
        assert len(issues) == 2

    def test_issues_across_multiple_queries_all_reported(self) -> None:
        """Issues across different queries are all collected."""
        doc = _doc("doc1", "Hello world")

        bad_anchor_q1 = Anchor("missing", 0, 5, "x" * 64)
        bad_anchor_q2 = Anchor("doc1", 0, 5, compute_hash("XXXXX"))

        queries = [_query("q1", bad_anchor_q1), _query("q2", bad_anchor_q2)]
        issues = check_corpus({"doc1": doc}, queries)
        assert len(issues) == 2

        query_ids = {i.query_id for i in issues}
        assert query_ids == {"q1", "q2"}

    def test_one_valid_one_invalid_only_invalid_reported(self) -> None:
        """Only the invalid anchor shows up; the valid one does not."""
        doc = _doc("doc1", "Hello world")
        good = _valid_anchor(doc, 0, 5)
        bad = Anchor("doc1", 0, 5, compute_hash("XXXXX"))

        issues = check_corpus({"doc1": doc}, [_query("q1", good, bad)])
        assert len(issues) == 1


# ---------------------------------------------------------------------------
# Tests: CorpusIssue dataclass
# ---------------------------------------------------------------------------

class TestCorpusIssue:
    def test_corpus_issue_is_frozen(self) -> None:
        """CorpusIssue is immutable."""
        issue = CorpusIssue(query_id="q1", document_id="d1", message="oops")
        with pytest.raises(AttributeError):
            issue.message = "changed"  # type: ignore

    def test_corpus_issue_fields(self) -> None:
        """CorpusIssue exposes query_id, document_id, message."""
        issue = CorpusIssue(query_id="q1", document_id="d1", message="bad hash")
        assert issue.query_id == "q1"
        assert issue.document_id == "d1"
        assert issue.message == "bad hash"


# ---------------------------------------------------------------------------
# Tests: public API export (req 26.6)
# ---------------------------------------------------------------------------

class TestPublicAPIExport:
    def test_check_corpus_exported_from_spanchor(self) -> None:
        """check_corpus is importable from the top-level spanchor package."""
        import spanchor
        assert hasattr(spanchor, "check_corpus")
        assert callable(spanchor.check_corpus)

    def test_corpus_issue_exported_from_spanchor(self) -> None:
        """CorpusIssue is importable from the top-level spanchor package."""
        import spanchor
        assert hasattr(spanchor, "CorpusIssue")

    def test_check_corpus_in_all(self) -> None:
        """check_corpus is listed in spanchor.__all__."""
        import spanchor
        assert "check_corpus" in spanchor.__all__
