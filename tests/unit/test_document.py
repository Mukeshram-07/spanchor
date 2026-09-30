"""Unit tests for Document model."""

import pytest

from spanchor.models.document import Document


class TestDocumentModel:
    """Tests for Document dataclass."""

    def test_document_creation(self):
        """Document can be created with all required fields."""
        doc = Document(
            document_id="doc1",
            text="hello world",
            sha256="a" * 64,
            schema_version="0.1.0",
        )

        assert doc.document_id == "doc1"
        assert doc.text == "hello world"
        assert doc.sha256 == "a" * 64
        assert doc.schema_version == "0.1.0"

    def test_document_frozen(self):
        """Document is immutable (frozen)."""
        doc = Document(
            document_id="doc1",
            text="hello",
            sha256="a" * 64,
        )

        with pytest.raises(AttributeError):
            doc.text = "modified"  # type: ignore

    def test_schema_version_defaults(self):
        """Schema version defaults to 0.1.0."""
        doc = Document(
            document_id="doc1",
            text="hello",
            sha256="a" * 64,
        )

        assert doc.schema_version == "0.1.0"


class TestDocumentFromText:
    """Tests for Document.from_text() factory method."""

    def test_from_text_basic(self):
        """from_text creates Document with canonicalized text and hash."""
        doc = Document.from_text("doc1", "hello world")

        assert doc.document_id == "doc1"
        assert doc.text == "hello world"
        assert len(doc.sha256) == 64
        assert doc.schema_version == "0.1.0"

    def test_from_text_normalizes_newlines(self):
        """from_text applies newline normalization (Requirement 1.2)."""
        doc = Document.from_text("doc1", "hello\r\nworld\rtest")

        assert doc.text == "hello\nworld\ntest"
        assert "\r" not in doc.text

    def test_from_text_applies_nfc(self):
        """from_text applies NFC Unicode normalization (Requirement 1.1)."""
        # café in NFD form (e + combining accent)
        nfd_text = "cafe\u0301"
        doc = Document.from_text("doc1", nfd_text)

        # Should be normalized to NFC
        assert doc.text == "café"

    def test_from_text_computes_hash(self):
        """from_text computes SHA256 hash of canonical text (Requirement 1.3)."""
        doc = Document.from_text("doc1", "hello")

        # Known SHA256 of "hello"
        expected_hash = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert doc.sha256 == expected_hash

    def test_from_text_hash_is_deterministic(self):
        """from_text produces same hash for same input."""
        doc1 = Document.from_text("doc1", "test text")
        doc2 = Document.from_text("doc2", "test text")

        # Different document IDs but same text → same hash
        assert doc1.sha256 == doc2.sha256

    def test_from_text_empty_string(self):
        """from_text handles empty string."""
        doc = Document.from_text("doc1", "")

        assert doc.text == ""
        assert len(doc.sha256) == 64
        # Known SHA256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert doc.sha256 == expected

    def test_from_text_unicode_text(self):
        """from_text handles Unicode text correctly."""
        doc = Document.from_text("doc1", "café ☕ 日本語")

        assert doc.text == "café ☕ 日本語"
        assert len(doc.sha256) == 64


class TestRoundTripProperty:
    """Test round-trip property from Requirement 1.5."""

    def test_document_round_trip_stable_hash(self):
        """Loading, exporting, and reloading produces same hash (Requirement 1.5)."""
        # Simulate loading with various non-canonical forms
        raw_text = "café\r\nworld\rtest"

        doc1 = Document.from_text("doc1", raw_text)

        # Simulate export and reload: use the canonical text
        doc2 = Document.from_text("doc1", doc1.text)

        # Hash should be stable
        assert doc1.sha256 == doc2.sha256
        assert doc1.text == doc2.text

    def test_multiple_normalizations_idempotent(self):
        """Multiple passes through from_text are idempotent."""
        raw_text = "hello\r\nworld"

        doc1 = Document.from_text("doc1", raw_text)
        doc2 = Document.from_text("doc1", doc1.text)
        doc3 = Document.from_text("doc1", doc2.text)

        assert doc1.text == doc2.text == doc3.text
        assert doc1.sha256 == doc2.sha256 == doc3.sha256


class TestDocumentValidation:
    """Tests for Document field validation."""

    def test_document_stores_exact_text(self):
        """Document stores text and hash from canonical layer (Requirement 1.4)."""
        from spanchor.canonical import compute_hash, normalize_text

        raw_text = "test\r\ndata"
        canonical = normalize_text(raw_text)
        expected_hash = compute_hash(canonical)

        doc = Document.from_text("doc1", raw_text)

        assert doc.text == canonical
        assert doc.sha256 == expected_hash

    def test_document_different_ids_same_text(self):
        """Different document_ids can have the same text and hash."""
        doc1 = Document.from_text("doc1", "hello")
        doc2 = Document.from_text("doc2", "hello")

        assert doc1.document_id != doc2.document_id
        assert doc1.text == doc2.text
        assert doc1.sha256 == doc2.sha256
