"""Tests for corpus and gold-set hashing in evaluate().

Tests verify:
- Corpus hash computed automatically in evaluate()
- Gold-set hash computed automatically in evaluate()
- Hashes stored in returned Run object
- Mismatch policy (warn/fail/ignore) works correctly
"""

import warnings

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.corpus.fingerprint import compute_corpus_hash, compute_gold_set_hash
from spanchor.errors import EvaluationError
from spanchor.evaluation.engine import evaluate
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult


class TestEvaluateComputesHashes:
    """Tests that evaluate() computes and stores hashes."""

    def test_evaluate_returns_corpus_hash(self) -> None:
        """evaluate() should compute and return corpus_hash in Run."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What is greeting?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        # Should have corpus_hash
        assert run.corpus_hash is not None
        assert run.corpus_hash.startswith("sha256:")
        assert len(run.corpus_hash) == 71

    def test_evaluate_returns_gold_set_hash(self) -> None:
        """evaluate() should compute and return gold_set_hash in Run."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What is greeting?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        # Should have gold_set_hash
        assert run.gold_set_hash is not None
        assert run.gold_set_hash.startswith("sha256:")
        assert len(run.gold_set_hash) == 71

    def test_evaluate_hashes_computed_correctly(self) -> None:
        """evaluate() hashes should match independently computed hashes."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What is greeting?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        # Independently compute hashes
        expected_corpus_hash = compute_corpus_hash([doc])
        expected_gold_set_hash = compute_gold_set_hash([query])

        # Should match
        assert run.corpus_hash == expected_corpus_hash
        assert run.gold_set_hash == expected_gold_set_hash

    def test_evaluate_with_multiple_documents(self) -> None:
        """evaluate() should handle corpus with multiple documents."""
        doc1 = Document.from_text("doc1", "Hello")
        doc2 = Document.from_text("doc2", "World")

        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "First?", (anchor1,))
        result1 = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run = evaluate(
            documents={"doc1": doc1, "doc2": doc2},
            queries=[query1],
            retrieval_results={"q1": [result1]},
        )

        # Corpus hash should include both documents
        expected_corpus_hash = compute_corpus_hash([doc1, doc2])
        assert run.corpus_hash == expected_corpus_hash

    def test_evaluate_with_multiple_queries(self) -> None:
        """evaluate() should handle gold set with multiple queries."""
        doc = Document.from_text("doc1", "Hello world")

        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "First?", (anchor1,))

        anchor2 = Anchor("doc1", 6, 11, compute_hash("world"))
        query2 = Query("q2", "Second?", (anchor2,))

        result1 = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)
        result2 = RetrievalResult(rank=1, score=0.90, document_id="doc1", start=6, end=11)

        run = evaluate(
            documents={"doc1": doc},
            queries=[query1, query2],
            retrieval_results={"q1": [result1], "q2": [result2]},
        )

        # Gold-set hash should include both queries
        expected_gold_set_hash = compute_gold_set_hash([query1, query2])
        assert run.gold_set_hash == expected_gold_set_hash


class TestGoldSetHashMismatchDetection:
    """Tests for gold_set_hash parameter and mismatch policy."""

    def test_mismatch_policy_ignore(self) -> None:
        """corpus_mismatch_policy='ignore' should skip validation."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        # Should not raise even with wrong hash
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            gold_set_hash="sha256:wronghash123",
            corpus_mismatch_policy="ignore",
        )

        # Should still compute correct hash
        assert run.gold_set_hash == compute_gold_set_hash([query])

    def test_mismatch_policy_warn_on_mismatch(self) -> None:
        """corpus_mismatch_policy='warn' should emit warning on mismatch."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        wrong_hash = "sha256:" + "a" * 64

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            run = evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": [result]},
                gold_set_hash=wrong_hash,
                corpus_mismatch_policy="warn",
            )

            # Should emit warning
            assert len(w) >= 1
            # Find our mismatch warning
            mismatch_warning = next(
                (warning for warning in w if "mismatch" in str(warning.message).lower()),
                None,
            )
            assert mismatch_warning is not None
            assert "mismatch" in str(mismatch_warning.message).lower()

    def test_mismatch_policy_warn_no_warning_on_match(self) -> None:
        """corpus_mismatch_policy='warn' should NOT warn on correct hash."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        correct_hash = compute_gold_set_hash([query])

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            run = evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": [result]},
                gold_set_hash=correct_hash,
                corpus_mismatch_policy="warn",
            )

            # Should NOT emit mismatch warning (may have other warnings)
            mismatch_warnings = [
                warning for warning in w if "mismatch" in str(warning.message).lower()
            ]
            assert len(mismatch_warnings) == 0

    def test_mismatch_policy_fail_on_mismatch(self) -> None:
        """corpus_mismatch_policy='fail' should raise on mismatch."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        wrong_hash = "sha256:" + "a" * 64

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": [result]},
                gold_set_hash=wrong_hash,
                corpus_mismatch_policy="fail",
            )

        assert "mismatch" in str(exc_info.value).lower()

    def test_mismatch_policy_fail_no_error_on_match(self) -> None:
        """corpus_mismatch_policy='fail' should NOT raise on correct hash."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        correct_hash = compute_gold_set_hash([query])

        # Should not raise
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            gold_set_hash=correct_hash,
            corpus_mismatch_policy="fail",
        )

        assert run is not None

    def test_gold_set_hash_none_no_validation(self) -> None:
        """gold_set_hash=None should skip validation (default behavior)."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        # Should work fine without providing gold_set_hash
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        # Should still compute hash
        assert run.gold_set_hash is not None

    def test_mismatch_policy_default_is_warn(self) -> None:
        """Default corpus_mismatch_policy should be 'warn'."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        wrong_hash = "sha256:" + "a" * 64

        # Default policy is "warn", should emit warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            run = evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": [result]},
                gold_set_hash=wrong_hash,
                # corpus_mismatch_policy not specified, should use default "warn"
            )

            mismatch_warnings = [
                warning for warning in w if "mismatch" in str(warning.message).lower()
            ]
            assert len(mismatch_warnings) == 1


class TestHashConsistency:
    """Tests for hash consistency across scenarios."""

    def test_hash_consistent_with_identical_inputs(self) -> None:
        """Same inputs should produce same hashes across evaluate() calls."""
        doc = Document.from_text("doc1", "Hello world")
        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run1 = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        run2 = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        assert run1.corpus_hash == run2.corpus_hash
        assert run1.gold_set_hash == run2.gold_set_hash

    def test_hash_differs_with_different_corpus(self) -> None:
        """Different corpus should produce different corpus_hash."""
        doc1 = Document.from_text("doc1", "Hello world")
        doc2 = Document.from_text("doc1", "Hello there")

        anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query = Query("q1", "What?", (anchor,))
        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run1 = evaluate(
            documents={"doc1": doc1},
            queries=[query],
            retrieval_results={"q1": [result]},
        )

        # Create new anchor with updated hash for doc2
        anchor2 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query2 = Query("q1", "What?", (anchor2,))
        run2 = evaluate(
            documents={"doc1": doc2},
            queries=[query2],
            retrieval_results={"q1": [result]},
        )

        # Corpus hashes should differ
        assert run1.corpus_hash != run2.corpus_hash

        # Gold-set hashes should be same (queries are identical)
        assert run1.gold_set_hash == run2.gold_set_hash

    def test_hash_differs_with_different_gold_set(self) -> None:
        """Different gold set should produce different gold_set_hash."""
        doc = Document.from_text("doc1", "Hello world")

        anchor1 = Anchor("doc1", 0, 5, compute_hash("Hello"))
        query1 = Query("q1", "What?", (anchor1,))

        anchor2 = Anchor("doc1", 0, 6, compute_hash("Hello "))
        query2 = Query("q1", "What?", (anchor2,))

        result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        run1 = evaluate(
            documents={"doc1": doc},
            queries=[query1],
            retrieval_results={"q1": [result]},
        )

        run2 = evaluate(
            documents={"doc1": doc},
            queries=[query2],
            retrieval_results={"q1": [result]},
        )

        # Corpus hashes should be same
        assert run1.corpus_hash == run2.corpus_hash

        # Gold-set hashes should differ
        assert run1.gold_set_hash != run2.gold_set_hash
