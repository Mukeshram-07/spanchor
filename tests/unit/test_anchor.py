"""Unit tests for the Anchor model."""

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.errors import AnchorResolutionError
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document


class TestAnchorCreation:
    """Tests for Anchor instantiation."""

    def test_anchor_creation(self) -> None:
        """Test basic anchor creation."""
        text_hash = compute_hash("Hello")
        anchor = Anchor("doc1", 0, 5, text_hash)

        assert anchor.document_id == "doc1"
        assert anchor.start == 0
        assert anchor.end == 5
        assert anchor.expected_text_hash == text_hash
        assert anchor.schema_version == "0.1.0"

    def test_anchor_with_custom_schema_version(self) -> None:
        """Test anchor with custom schema version."""
        text_hash = compute_hash("test")
        anchor = Anchor("doc1", 0, 4, text_hash, schema_version="0.2.0")

        assert anchor.schema_version == "0.2.0"

    def test_anchor_is_frozen(self) -> None:
        """Test that Anchor is immutable."""
        text_hash = compute_hash("test")
        anchor = Anchor("doc1", 0, 4, text_hash)

        with pytest.raises(AttributeError):
            anchor.start = 10  # type: ignore


class TestAnchorValidation:
    """Tests for Anchor.validate() method."""

    def test_validate_success(self) -> None:
        """Test successful validation of a valid anchor."""
        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash("Hello")
        anchor = Anchor("doc1", 0, 5, text_hash)

        # Should not raise
        anchor.validate(doc)

    def test_validate_middle_span(self) -> None:
        """Test validation of anchor in middle of document."""
        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash("world")
        anchor = Anchor("doc1", 6, 11, text_hash)

        anchor.validate(doc)

    def test_validate_empty_span(self) -> None:
        """Test validation of empty span (start == end)."""
        doc = Document.from_text("doc1", "Hello world")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 5, 5, text_hash)

        anchor.validate(doc)

    def test_validate_full_document(self) -> None:
        """Test anchor spanning entire document."""
        text = "Hello world"
        doc = Document.from_text("doc1", text)
        text_hash = compute_hash(text)
        anchor = Anchor("doc1", 0, len(text), text_hash)

        anchor.validate(doc)

    def test_validate_text_hash_mismatch(self) -> None:
        """Test validation fails when text doesn't match hash."""
        doc = Document.from_text("doc1", "Hello world")
        wrong_hash = compute_hash("Goodbye")
        anchor = Anchor("doc1", 0, 5, wrong_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert error.start == 0
        assert error.end == 5
        assert "hash mismatch" in str(error).lower()

    def test_validate_end_out_of_bounds(self) -> None:
        """Test validation fails when end offset exceeds document length."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("Hello!")
        anchor = Anchor("doc1", 0, 10, text_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert error.start == 0
        assert error.end == 10
        assert "out of bounds" in str(error).lower()

    def test_validate_start_out_of_bounds(self) -> None:
        """Test validation fails when start offset exceeds document length."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 10, 10, text_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert "out of bounds" in str(error).lower()

    def test_validate_negative_start(self) -> None:
        """Test validation fails with negative start offset."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", -1, 5, text_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert "negative" in str(error).lower()

    def test_validate_negative_end(self) -> None:
        """Test validation fails with negative end offset."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 0, -1, text_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert "negative" in str(error).lower()

    def test_validate_start_greater_than_end(self) -> None:
        """Test validation fails when start > end."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 5, 2, text_hash)

        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        error = exc_info.value
        assert error.document_id == "doc1"
        assert error.start == 5
        assert error.end == 2
        assert "invalid interval" in str(error).lower()


class TestAnchorWithNormalizedText:
    """Tests for anchors with text requiring normalization."""

    def test_validate_with_normalized_newlines(self) -> None:
        """Test anchor validation with normalized newlines."""
        # Document.from_text normalizes \r\n to \n
        doc = Document.from_text("doc1", "Hello\r\nworld")
        assert doc.text == "Hello\nworld"

        # Anchor should reference the normalized text
        text_hash = compute_hash("Hello\nworld")
        anchor = Anchor("doc1", 0, 11, text_hash)

        anchor.validate(doc)

    def test_validate_unicode_normalization(self) -> None:
        """Test anchor validation with NFC-normalized text."""
        # Document.from_text applies NFC normalization
        raw_text = "café"  # could be in NFD or NFC form
        doc = Document.from_text("doc1", raw_text)

        # Create anchor with hash of normalized text
        text_hash = compute_hash(doc.text)
        anchor = Anchor("doc1", 0, len(doc.text), text_hash)

        anchor.validate(doc)


class TestAnchorEdgeCases:
    """Tests for edge cases in anchor validation."""

    def test_validate_at_document_boundary(self) -> None:
        """Test anchor at end of document."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 5, 5, text_hash)

        anchor.validate(doc)

    def test_validate_single_character(self) -> None:
        """Test anchor spanning single character."""
        doc = Document.from_text("doc1", "Hello")
        text_hash = compute_hash("H")
        anchor = Anchor("doc1", 0, 1, text_hash)

        anchor.validate(doc)

    def test_validate_empty_document(self) -> None:
        """Test anchor in empty document."""
        doc = Document.from_text("doc1", "")
        text_hash = compute_hash("")
        anchor = Anchor("doc1", 0, 0, text_hash)

        anchor.validate(doc)

    def test_validate_empty_document_invalid_offset(self) -> None:
        """Test anchor with invalid offset in empty document."""
        doc = Document.from_text("doc1", "")
        text_hash = compute_hash("x")
        anchor = Anchor("doc1", 0, 1, text_hash)

        with pytest.raises(AnchorResolutionError):
            anchor.validate(doc)
