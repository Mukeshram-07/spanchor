"""Unit tests for annotation locate helper."""

import pytest

from spanchor.annotation.locate import (
    LocateMatch,
    format_matches,
    locate_text,
)
from spanchor.models.document import Document


@pytest.fixture
def single_doc() -> dict[str, Document]:
    """Single document with well-known content."""
    return {
        "doc1": Document.from_text(
            "doc1", "The quick brown fox jumps over the lazy dog."
        )
    }


@pytest.fixture
def multi_doc() -> dict[str, Document]:
    """Multiple documents including duplicated text."""
    return {
        "doc1": Document.from_text("doc1", "The quick brown fox jumps over the lazy dog."),
        "doc2": Document.from_text(
            "doc2",
            "The quick brown fox appears in doc2. The quick brown fox is here again.",
        ),
        "doc3": Document.from_text(
            "doc3", "Text with   extra    whitespace   is   here."
        ),
    }


# ---------------------------------------------------------------------------
# Exact matching
# ---------------------------------------------------------------------------


class TestLocateTextExact:
    """Tests for exact substring matching."""

    def test_single_exact_match(self, single_doc: dict[str, Document]) -> None:
        """A unique substring is found with correct offsets."""
        matches = locate_text("quick brown fox", single_doc)

        assert len(matches) == 1
        m = matches[0]
        assert m.document_id == "doc1"
        assert m.start == 4
        assert m.end == 19
        assert m.matched_text == "quick brown fox"
        assert not m.is_normalized_match

    def test_offsets_are_correct_slice(self, single_doc: dict[str, Document]) -> None:
        """document.text[start:end] must equal matched_text (half-open interval semantics)."""
        matches = locate_text("lazy dog", single_doc)
        assert len(matches) == 1
        doc = single_doc["doc1"]
        m = matches[0]
        assert doc.text[m.start : m.end] == m.matched_text

    def test_text_hash_is_sha256_of_matched_text(
        self, single_doc: dict[str, Document]
    ) -> None:
        """text_hash must be SHA256 of the matched substring."""
        import hashlib

        matches = locate_text("quick brown fox", single_doc)
        assert len(matches) == 1
        m = matches[0]
        expected_hash = hashlib.sha256(m.matched_text.encode("utf-8")).hexdigest()
        assert m.text_hash == expected_hash

    def test_multiple_occurrences_in_same_document(
        self, multi_doc: dict[str, Document]
    ) -> None:
        """Multiple occurrences in one document are all returned."""
        matches = locate_text("quick brown fox", {"doc2": multi_doc["doc2"]})
        assert len(matches) == 2
        # Both matches live in doc2
        assert all(m.document_id == "doc2" for m in matches)
        # Offsets are different
        starts = [m.start for m in matches]
        assert starts[0] != starts[1]

    def test_occurrence_numbers_assigned(self, multi_doc: dict[str, Document]) -> None:
        """Occurrence numbers are 1-based and sequential."""
        matches = locate_text("quick brown fox", {"doc2": multi_doc["doc2"]})
        assert [m.occurrence_number for m in matches] == [1, 2]

    def test_matches_across_multiple_documents(
        self, multi_doc: dict[str, Document]
    ) -> None:
        """Matches are returned from all documents that contain the text."""
        # "quick brown fox" appears in doc1 (once) and doc2 (twice)
        docs = {k: multi_doc[k] for k in ("doc1", "doc2")}
        matches = locate_text("quick brown fox", docs)
        assert len(matches) == 3
        doc_ids = {m.document_id for m in matches}
        assert doc_ids == {"doc1", "doc2"}

    def test_returns_empty_when_not_found(self, single_doc: dict[str, Document]) -> None:
        """Returns empty list when text is not present anywhere."""
        matches = locate_text("absolutely not here at all zzz", single_doc)
        assert matches == []

    def test_empty_search_text_returns_empty(
        self, single_doc: dict[str, Document]
    ) -> None:
        """Empty search string returns empty list without error."""
        assert locate_text("", single_doc) == []

    def test_empty_documents_returns_empty(self) -> None:
        """No documents → no matches."""
        assert locate_text("anything", {}) == []

    def test_context_before_and_after_populated(
        self, single_doc: dict[str, Document]
    ) -> None:
        """Context fields are non-empty when there is surrounding text."""
        matches = locate_text("quick brown fox", single_doc)
        m = matches[0]
        assert m.context_before == "The "
        assert m.context_after == " jumps over the lazy dog."

    def test_context_at_document_start(self, single_doc: dict[str, Document]) -> None:
        """context_before is empty when match is at document start."""
        matches = locate_text("The quick", single_doc)
        assert len(matches) == 1
        assert matches[0].context_before == ""

    def test_context_at_document_end(self, single_doc: dict[str, Document]) -> None:
        """context_after is empty when match is at document end."""
        matches = locate_text("lazy dog.", single_doc)
        assert len(matches) == 1
        assert matches[0].context_after == ""

    def test_context_chars_limits_window(self) -> None:
        """context_chars parameter limits context window size."""
        doc = Document.from_text("d", "A" * 200 + "TARGET" + "B" * 200)
        matches = locate_text("TARGET", {"d": doc}, context_chars=10)
        assert len(matches) == 1
        m = matches[0]
        assert len(m.context_before) == 10
        assert len(m.context_after) == 10

    def test_sorted_by_document_id_then_start(
        self, multi_doc: dict[str, Document]
    ) -> None:
        """Results are sorted alphabetically by document_id, then by start offset."""
        docs = {k: multi_doc[k] for k in ("doc1", "doc2")}
        matches = locate_text("quick brown fox", docs)
        # doc1 before doc2
        assert matches[0].document_id == "doc1"
        # Within doc2, earlier occurrence first
        doc2_matches = [m for m in matches if m.document_id == "doc2"]
        assert doc2_matches[0].start < doc2_matches[1].start


# ---------------------------------------------------------------------------
# Whitespace-normalized fallback
# ---------------------------------------------------------------------------


class TestLocateTextNormalizedFallback:
    """Tests for whitespace-normalized fallback search (Requirement 15.3)."""

    def test_normalizes_when_no_exact_match(
        self, multi_doc: dict[str, Document]
    ) -> None:
        """Falls back to normalized search when exact match fails."""
        # "extra    whitespace" in doc3 has multiple spaces
        matches = locate_text("extra whitespace", {"doc3": multi_doc["doc3"]})
        assert len(matches) == 1
        assert matches[0].is_normalized_match is True

    def test_normalized_match_offsets_slice_correctly(
        self, multi_doc: dict[str, Document]
    ) -> None:
        """Offsets from normalized match correctly slice original document text."""
        matches = locate_text("extra whitespace", {"doc3": multi_doc["doc3"]})
        doc = multi_doc["doc3"]
        m = matches[0]
        # The slice of original text should contain the expected words
        sliced = doc.text[m.start : m.end]
        assert "extra" in sliced
        assert "whitespace" in sliced

    def test_exact_preferred_over_normalized(self) -> None:
        """Exact match is returned and normalized fallback is not triggered."""
        doc = Document.from_text("d", "hello world")
        matches = locate_text("hello world", {"d": doc})
        assert len(matches) == 1
        assert matches[0].is_normalized_match is False

    def test_no_match_in_either_mode_returns_empty(self) -> None:
        """Returns empty when text is absent even after normalization."""
        doc = Document.from_text("d", "hello world")
        matches = locate_text("completely absent xyz", {"d": doc})
        assert matches == []


# ---------------------------------------------------------------------------
# format_matches
# ---------------------------------------------------------------------------


class TestFormatMatches:
    """Tests for the format_matches display helper."""

    def test_no_matches_message(self) -> None:
        """Returns a human-readable 'no matches' message for empty list."""
        result = format_matches([])
        assert "no matches" in result.lower()

    def test_single_match_contains_key_fields(
        self, single_doc: dict[str, Document]
    ) -> None:
        """Single match output includes document_id, offsets, and hash."""
        matches = locate_text("quick brown fox", single_doc)
        output = format_matches(matches)
        assert "doc1" in output
        assert "4" in output   # start offset
        assert "19" in output  # end offset
        assert matches[0].text_hash[:8] in output

    def test_multiple_matches_numbered(self, multi_doc: dict[str, Document]) -> None:
        """Multiple matches show occurrence numbers."""
        docs = {"doc2": multi_doc["doc2"]}
        matches = locate_text("quick brown fox", docs)
        output = format_matches(matches)
        assert "1/" in output
        assert "2/" in output

    def test_show_context_false_omits_context(
        self, single_doc: dict[str, Document]
    ) -> None:
        """Passing show_context=False omits context lines from output."""
        matches = locate_text("quick brown fox", single_doc)
        output = format_matches(matches, show_context=False)
        assert "context" not in output.lower()

    def test_normalized_match_noted_in_output(self) -> None:
        """Whitespace-normalized matches are labelled in output."""
        doc = Document.from_text("d", "hello   world")
        matches = locate_text("hello world", {"d": doc})
        output = format_matches(matches)
        assert "normalized" in output.lower()
