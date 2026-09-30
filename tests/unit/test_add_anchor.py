"""Unit tests for annotation add_anchor helper.

Covers:
- Req 16.1: locate text in documents when add is called
- Req 16.2: unique text → append valid query+anchor to gold JSONL
- Req 16.3: ambiguous text → reject unless --occurrence N given
- Req 16.4: with --occurrence N → use the Nth occurrence
- Req 16.5: success → return (Query, LocateMatch) for confirmation
- Req 16.6: gold file doesn't exist → create it
- Req 16.7: validate query_id uniqueness before adding
"""

import json

import pytest

from spanchor.annotation.add import (
    AmbiguousTextError,
    DuplicateQueryIdError,
    OccurrenceOutOfRangeError,
    TextNotFoundError,
    add_anchor,
)
from spanchor.models.document import Document
from spanchor.models.query import Query


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def docs() -> dict[str, Document]:
    """Two documents: doc1 has unique text, doc2 has repeated text."""
    return {
        "doc1": Document.from_text(
            "doc1",
            "The quick brown fox jumps over the lazy dog.",
        ),
        "doc2": Document.from_text(
            "doc2",
            "Repeat me once. Repeat me twice.",
        ),
    }


@pytest.fixture
def gold_path(tmp_path):
    """A path inside a temp directory (file does NOT yet exist)."""
    return tmp_path / "gold.jsonl"


@pytest.fixture
def existing_gold_path(tmp_path, docs):
    """A gold JSONL file that already contains one query."""
    path = tmp_path / "gold.jsonl"
    # Write one pre-existing entry directly
    entry = {
        "query_id": "existing-q1",
        "question": "Existing question?",
        "anchors": [
            {
                "document_id": "doc1",
                "start": 0,
                "end": 3,
                "expected_text_hash": "deadbeef",
                "schema_version": "0.1.0",
            }
        ],
        "schema_version": "0.1.0",
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")
    return path


# ---------------------------------------------------------------------------
# Req 16.6 – gold file creation
# ---------------------------------------------------------------------------


class TestGoldFileCreation:
    """Gold file should be created when it does not exist."""

    def test_creates_file_when_absent(self, docs, gold_path):
        assert not gold_path.exists()
        add_anchor("q1", "Where does the fox jump?", "quick brown fox", docs, gold_path)
        assert gold_path.exists()

    def test_creates_parent_directories(self, docs, tmp_path):
        nested = tmp_path / "a" / "b" / "gold.jsonl"
        assert not nested.parent.exists()
        add_anchor("q1", "test question", "quick brown fox", docs, nested)
        assert nested.exists()


# ---------------------------------------------------------------------------
# Req 16.2 – unique text → append and return valid query+anchor
# ---------------------------------------------------------------------------


class TestUniqueTextAdd:
    """Unique search text should be appended as a valid Query with one Anchor."""

    def test_returns_query_and_match(self, docs, gold_path):
        query, match = add_anchor(
            "q1", "Where does the fox jump?", "quick brown fox", docs, gold_path
        )
        assert isinstance(query, Query)
        assert query.query_id == "q1"
        assert query.question == "Where does the fox jump?"
        assert len(query.anchors) == 1

    def test_anchor_offsets_match_document_text(self, docs, gold_path):
        query, match = add_anchor("q1", "Fox question", "quick brown fox", docs, gold_path)
        anchor = query.anchors[0]
        doc = docs[anchor.document_id]
        assert doc.text[anchor.start : anchor.end] == "quick brown fox"

    def test_anchor_text_hash_is_correct(self, docs, gold_path):
        from spanchor.canonical.normalize import compute_hash

        query, match = add_anchor("q1", "Fox question", "quick brown fox", docs, gold_path)
        anchor = query.anchors[0]
        doc = docs[anchor.document_id]
        expected_hash = compute_hash(doc.text[anchor.start : anchor.end])
        assert anchor.expected_text_hash == expected_hash

    def test_written_line_is_valid_json(self, docs, gold_path):
        add_anchor("q1", "Fox question", "quick brown fox", docs, gold_path)
        lines = [ln for ln in gold_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["query_id"] == "q1"
        assert data["question"] == "Fox question"
        assert len(data["anchors"]) == 1
        assert data["schema_version"] == "0.1.0"

    def test_appends_to_existing_file(self, docs, existing_gold_path):
        add_anchor("q2", "New question", "quick brown fox", docs, existing_gold_path)
        lines = [
            ln for ln in existing_gold_path.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
        assert len(lines) == 2
        ids = {json.loads(ln)["query_id"] for ln in lines}
        assert ids == {"existing-q1", "q2"}

    def test_returned_match_has_correct_offsets(self, docs, gold_path):
        query, match = add_anchor("q1", "Fox question", "quick brown fox", docs, gold_path)
        doc = docs["doc1"]
        assert doc.text[match.start : match.end] == "quick brown fox"


# ---------------------------------------------------------------------------
# Req 16.1 – text not found raises TextNotFoundError
# ---------------------------------------------------------------------------


class TestTextNotFound:
    def test_raises_when_text_absent(self, docs, gold_path):
        with pytest.raises(TextNotFoundError):
            add_anchor("q1", "question", "zzz no such text zzz", docs, gold_path)

    def test_gold_file_not_written_on_failure(self, docs, gold_path):
        with pytest.raises(TextNotFoundError):
            add_anchor("q1", "question", "not here", docs, gold_path)
        assert not gold_path.exists()


# ---------------------------------------------------------------------------
# Req 16.3 – ambiguous text rejected without --occurrence
# ---------------------------------------------------------------------------


class TestAmbiguousText:
    def test_raises_when_multiple_matches_and_no_occurrence(self, docs, gold_path):
        with pytest.raises(AmbiguousTextError) as exc_info:
            add_anchor("q1", "question", "Repeat me", docs, gold_path)
        err = exc_info.value
        assert err.match_count == 2
        assert len(err.matches) == 2

    def test_gold_file_not_written_on_ambiguous(self, docs, gold_path):
        with pytest.raises(AmbiguousTextError):
            add_anchor("q1", "question", "Repeat me", docs, gold_path)
        assert not gold_path.exists()


# ---------------------------------------------------------------------------
# Req 16.4 – --occurrence N picks the Nth match
# ---------------------------------------------------------------------------


class TestOccurrenceSelection:
    def test_occurrence_1_picks_first_match(self, docs, gold_path):
        query, match = add_anchor("q1", "question", "Repeat me", docs, gold_path, occurrence=1)
        assert match.occurrence_number == 1

    def test_occurrence_2_picks_second_match(self, docs, gold_path):
        query, match = add_anchor("q1", "question", "Repeat me", docs, gold_path, occurrence=2)
        assert match.occurrence_number == 2

    def test_occurrence_differs_in_offsets(self, docs, gold_path):
        _, match1 = add_anchor("q1", "q", "Repeat me", docs, gold_path, occurrence=1)
        gold_path2 = gold_path.parent / "gold2.jsonl"
        _, match2 = add_anchor("q1", "q", "Repeat me", docs, gold_path2, occurrence=2)
        assert match1.start != match2.start

    def test_occurrence_on_unique_text_uses_first(self, docs, gold_path):
        """occurrence=1 on a unique match should work normally."""
        query, match = add_anchor(
            "q1", "Fox question", "quick brown fox", docs, gold_path, occurrence=1
        )
        assert query.query_id == "q1"

    def test_occurrence_out_of_range_raises(self, docs, gold_path):
        with pytest.raises(OccurrenceOutOfRangeError) as exc_info:
            add_anchor("q1", "question", "Repeat me", docs, gold_path, occurrence=99)
        err = exc_info.value
        assert err.requested == 99
        assert err.available == 2

    def test_occurrence_zero_raises(self, docs, gold_path):
        with pytest.raises(OccurrenceOutOfRangeError):
            add_anchor("q1", "question", "Repeat me", docs, gold_path, occurrence=0)

    def test_occurrence_negative_raises(self, docs, gold_path):
        with pytest.raises(OccurrenceOutOfRangeError):
            add_anchor("q1", "question", "Repeat me", docs, gold_path, occurrence=-1)


# ---------------------------------------------------------------------------
# Req 16.7 – query_id uniqueness validation
# ---------------------------------------------------------------------------


class TestQueryIdUniqueness:
    def test_raises_when_duplicate_query_id(self, docs, existing_gold_path):
        with pytest.raises(DuplicateQueryIdError) as exc_info:
            add_anchor(
                "existing-q1",
                "duplicate question",
                "quick brown fox",
                docs,
                existing_gold_path,
            )
        err = exc_info.value
        assert err.query_id == "existing-q1"

    def test_no_duplicate_allows_add(self, docs, existing_gold_path):
        """A unique query_id should succeed even when file already has entries."""
        query, _ = add_anchor(
            "brand-new-id",
            "New question",
            "quick brown fox",
            docs,
            existing_gold_path,
        )
        assert query.query_id == "brand-new-id"

    def test_gold_file_unchanged_on_duplicate(self, docs, existing_gold_path):
        """On duplicate error, file content must not be modified."""
        original_content = existing_gold_path.read_text(encoding="utf-8")
        with pytest.raises(DuplicateQueryIdError):
            add_anchor(
                "existing-q1",
                "dupe question",
                "quick brown fox",
                docs,
                existing_gold_path,
            )
        assert existing_gold_path.read_text(encoding="utf-8") == original_content
