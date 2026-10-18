"""Tests for corpus and gold-set fingerprinting.

Tests verify that corpus and gold-set hashes are deterministic, order-independent,
and sensitive to content changes per PHASE_1_DESIGN_LOCK.md (D1, D2).
"""

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.corpus.fingerprint import compute_corpus_hash, compute_gold_set_hash
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query


class TestComputeCorpusHash:
    """Tests for compute_corpus_hash() determinism, order independence, and sensitivity."""

    def test_corpus_hash_format(self) -> None:
        """Corpus hash should be in 'sha256:<hex>' format."""
        doc = Document.from_text("doc1", "Hello world")
        hash_val = compute_corpus_hash([doc])

        assert hash_val.startswith("sha256:")
        assert len(hash_val) == 71  # "sha256:" (7) + 64 hex chars

    def test_corpus_hash_determinism(self) -> None:
        """Same documents should produce the same hash (determinism)."""
        doc = Document.from_text("doc1", "Hello world")
        hash1 = compute_corpus_hash([doc])
        hash2 = compute_corpus_hash([doc])

        assert hash1 == hash2

    def test_corpus_hash_order_independence(self) -> None:
        """Reordered documents should produce the same hash (order independence)."""
        doc1 = Document.from_text("doc1", "Hello")
        doc2 = Document.from_text("doc2", "World")

        hash1 = compute_corpus_hash([doc1, doc2])
        hash2 = compute_corpus_hash([doc2, doc1])

        assert hash1 == hash2

    def test_corpus_hash_sensitivity_to_document_change(self) -> None:
        """Modified document should produce different hash (sensitivity)."""
        doc1 = Document.from_text("doc1", "Hello world")
        doc2 = Document.from_text("doc1", "Hello there")

        hash1 = compute_corpus_hash([doc1])
        hash2 = compute_corpus_hash([doc2])

        assert hash1 != hash2

    def test_corpus_hash_sensitivity_to_document_id_change(self) -> None:
        """Different document_id should produce different hash."""
        doc1 = Document.from_text("doc1", "Hello")
        doc2 = Document.from_text("doc2", "Hello")

        hash1 = compute_corpus_hash([doc1])
        hash2 = compute_corpus_hash([doc2])

        assert hash1 != hash2

    def test_corpus_hash_empty_corpus(self) -> None:
        """Empty corpus should produce valid hash."""
        hash_val = compute_corpus_hash([])

        assert hash_val.startswith("sha256:")
        assert len(hash_val) == 71

    def test_corpus_hash_single_document(self) -> None:
        """Single document corpus should produce valid hash."""
        doc = Document.from_text("doc1", "Test")
        hash_val = compute_corpus_hash([doc])

        assert hash_val.startswith("sha256:")

    def test_corpus_hash_multiple_documents(self) -> None:
        """Multiple documents should produce valid hash."""
        docs = [
            Document.from_text("doc1", "First"),
            Document.from_text("doc2", "Second"),
            Document.from_text("doc3", "Third"),
        ]
        hash_val = compute_corpus_hash(docs)

        assert hash_val.startswith("sha256:")


class TestComputeGoldSetHash:
    """Tests for compute_gold_set_hash() determinism, text-agnosticity, and sensitivity."""

    def test_gold_set_hash_format(self) -> None:
        """Gold-set hash should be in 'sha256:<hex>' format."""
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What is this?", (anchor,))
        hash_val = compute_gold_set_hash([query])

        assert hash_val.startswith("sha256:")
        assert len(hash_val) == 71  # "sha256:" (7) + 64 hex chars

    def test_gold_set_hash_determinism(self) -> None:
        """Same queries should produce same hash (determinism)."""
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What is this?", (anchor,))

        hash1 = compute_gold_set_hash([query])
        hash2 = compute_gold_set_hash([query])

        assert hash1 == hash2

    def test_gold_set_hash_order_independence(self) -> None:
        """Reordered queries should produce same hash (order independence)."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "First?", (anchor1,))

        anchor2 = Anchor("doc2", 0, 5, compute_hash("World"))
        query2 = Query("q2", "Second?", (anchor2,))

        hash1 = compute_gold_set_hash([query1, query2])
        hash2 = compute_gold_set_hash([query2, query1])

        assert hash1 == hash2

    def test_gold_set_hash_question_text_agnostic(self) -> None:
        """Different question text should produce SAME hash (text-agnostic).

        Per D2: Gold-set hash identifies STRUCTURE (anchors), not question text.
        Question text is editorial; only anchor structure matters.
        """
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "What is the greeting?", (anchor,))
        query2 = Query("q1", "What's the hello?", (anchor,))

        hash1 = compute_gold_set_hash([query1])
        hash2 = compute_gold_set_hash([query2])

        # Same hash even though questions are different
        assert hash1 == hash2

    def test_gold_set_hash_sensitive_to_anchor_change(self) -> None:
        """Changed anchor should produce DIFFERENT hash (anchor-sensitive)."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "What?", (anchor1,))

        anchor2 = Anchor("doc1", 0, 6, compute_hash("Hello "))
        query2 = Query("q1", "What?", (anchor2,))

        hash1 = compute_gold_set_hash([query1])
        hash2 = compute_gold_set_hash([query2])

        assert hash1 != hash2

    def test_gold_set_hash_sensitive_to_document_id_change(self) -> None:
        """Changed document_id should produce DIFFERENT hash."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "What?", (anchor1,))

        anchor2 = Anchor("doc2", 0, 5, compute_hash("Hello"))
        query2 = Query("q1", "What?", (anchor2,))

        hash1 = compute_gold_set_hash([query1])
        hash2 = compute_gold_set_hash([query2])

        assert hash1 != hash2

    def test_gold_set_hash_empty_anchors(self) -> None:
        """Query with no anchors should produce valid hash."""
        query = Query("q1", "No anchors?", ())
        hash_val = compute_gold_set_hash([query])

        assert hash_val.startswith("sha256:")

    def test_gold_set_hash_multiple_anchors_order_independence(self) -> None:
        """Multiple anchors in different order should produce same hash."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        anchor2 = Anchor("doc2", 0, 5, compute_hash("World"))

        query1 = Query("q1", "What?", (anchor1, anchor2))
        query2 = Query("q1", "What?", (anchor2, anchor1))

        hash1 = compute_gold_set_hash([query1])
        hash2 = compute_gold_set_hash([query2])

        # Should be same because anchors are sorted before hashing
        assert hash1 == hash2

    def test_gold_set_hash_multiple_queries(self) -> None:
        """Multiple queries should produce valid hash."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        anchor2 = Anchor("doc2", 0, 5, compute_hash("World"))

        query1 = Query("q1", "First?", (anchor1,))
        query2 = Query("q2", "Second?", (anchor2,))

        hash_val = compute_gold_set_hash([query1, query2])

        assert hash_val.startswith("sha256:")

    def test_gold_set_hash_query_id_affects_hash(self) -> None:
        """Different query_id should produce DIFFERENT hash."""
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "What?", (anchor,))
        query2 = Query("q2", "What?", (anchor,))

        hash1 = compute_gold_set_hash([query1])
        hash2 = compute_gold_set_hash([query2])

        assert hash1 != hash2


class TestHashStability:
    """Integration tests for hash stability across operations."""

    def test_corpus_hash_stable_across_multiple_documents(self) -> None:
        """Corpus hash should remain stable for consistent corpus."""
        docs = [
            Document.from_text("doc1", "Alpha"),
            Document.from_text("doc2", "Beta"),
            Document.from_text("doc3", "Gamma"),
        ]
        hash_val = compute_corpus_hash(docs)

        # Hash should be consistent when computed again
        hash_val2 = compute_corpus_hash(docs)
        assert hash_val == hash_val2

        # But differ when document changes
        docs_modified = [
            Document.from_text("doc1", "Alpha"),
            Document.from_text("doc2", "Beta-Modified"),
            Document.from_text("doc3", "Gamma"),
        ]
        hash_val3 = compute_corpus_hash(docs_modified)
        assert hash_val != hash_val3

    def test_gold_set_hash_stable_for_consistent_gold_set(self) -> None:
        """Gold-set hash should remain stable for consistent queries."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        anchor2 = Anchor("doc2", 5, 10, compute_hash("World"))

        queries = [
            Query("q1", "First question?", (anchor1,)),
            Query("q2", "Second question?", (anchor2,)),
        ]

        hash_val = compute_gold_set_hash(queries)
        hash_val2 = compute_gold_set_hash(queries)

        assert hash_val == hash_val2

    def test_hash_types_independent(self) -> None:
        """Corpus and gold-set hashes should be independent.

        Changing corpus shouldn't affect gold-set hash, and vice versa.
        """
        # Original corpus and gold set
        doc = Document.from_text("doc1", "Hello")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))

        corpus_hash1 = compute_corpus_hash([doc])
        gold_hash1 = compute_gold_set_hash([query])

        # Change corpus (add document)
        doc2 = Document.from_text("doc2", "World")
        corpus_hash2 = compute_corpus_hash([doc, doc2])

        # Gold-set hash should be unchanged
        gold_hash2 = compute_gold_set_hash([query])

        assert corpus_hash1 != corpus_hash2  # corpus changed
        assert gold_hash1 == gold_hash2  # gold set unchanged

    def test_hash_output_hex_encoding(self) -> None:
        """Hash should be valid hex string."""
        doc = Document.from_text("doc1", "Test")
        hash_val = compute_corpus_hash([doc])

        # Remove "sha256:" prefix
        hex_part = hash_val[7:]

        # Should be valid hex
        try:
            int(hex_part, 16)
        except ValueError:
            pytest.fail(f"Hash hex part is not valid hex: {hex_part}")

        # Should be 64 characters (256 bits = 64 hex digits)
        assert len(hex_part) == 64
