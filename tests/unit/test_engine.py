"""Unit tests for evaluation engine.

Tests the main evaluate() API that orchestrates validation, mapping,
metric computation, and aggregation.
"""

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.errors import DocumentNotFoundError, EvaluationError
from spanchor.evaluation.engine import evaluate
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult


class TestEvaluateBasic:
    """Basic functionality tests for evaluate()."""

    def test_evaluate_perfect_recall_span_form(self):
        """Test evaluate with perfect recall using span-form results."""
        # Create document
        doc = Document.from_text("doc1", "Hello world, this is a test.")

        # Create query with anchor for "Hello world"
        text_hash = compute_hash("Hello world")
        anchor = Anchor("doc1", 0, 11, text_hash)
        query = Query("q1", "What is the greeting?", (anchor,))

        # Perfect retrieval - exact match
        result = RetrievalResult(
            rank=1, score=0.95, document_id="doc1", start=0, end=11
        )

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Assertions
        assert run.timestamp is not None
        assert len(run.queries) == 1
        assert run.queries[0].query_id == "q1"

        # Per-query metrics
        q_metrics = run.per_query_metrics["q1"]
        assert q_metrics["recall@5"] == 1.0
        assert q_metrics["precision@5"] == 1.0
        assert q_metrics["hit@5"] == 1.0
        assert q_metrics["full_evidence@5"] == 1.0
        assert q_metrics["iou"] == 1.0

        # Aggregate metrics
        assert run.aggregate_metrics["mean_recall@5"] == 1.0
        assert run.aggregate_metrics["mean_precision@5"] == 1.0

        # Mapper stats
        assert run.mapper_stats["MAPPED_EXACT"] == 1

        # Config
        assert run.config["k"] == 5
        assert run.config["min_overlap"] == 0.5

    def test_evaluate_chunk_text_form_exact_match(self):
        """Test evaluate with chunk-text form requiring exact substring mapping."""
        # Create document
        doc = Document.from_text("doc1", "The quick brown fox jumps over the lazy dog.")

        # Create query with anchor for "quick brown fox"
        text_hash = compute_hash("quick brown fox")
        anchor = Anchor("doc1", 4, 19, text_hash)
        query = Query("q1", "What animal is quick?", (anchor,))

        # Chunk-text form result
        result = RetrievalResult(rank=1, score=0.88, text="quick brown fox")

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Assertions
        q_metrics = run.per_query_metrics["q1"]
        assert q_metrics["recall@5"] == 1.0
        assert q_metrics["precision@5"] == 1.0
        assert run.mapper_stats["MAPPED_EXACT"] == 1

    def test_evaluate_partial_recall(self):
        """Test evaluate with partial recall."""
        # Create document
        doc = Document.from_text("doc1", "Alpha Beta Gamma Delta Epsilon")

        # Create query with anchor for "Alpha Beta Gamma" (17 chars including trailing space)
        text_hash = compute_hash("Alpha Beta Gamma ")
        anchor = Anchor("doc1", 0, 17, text_hash)
        query = Query("q1", "Greek letters?", (anchor,))

        # Retrieval only covers "Alpha Beta" (10 chars)
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=10)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Recall should be 10/17 ≈ 0.588
        q_metrics = run.per_query_metrics["q1"]
        assert 0.58 < q_metrics["recall@5"] < 0.59
        # Precision should be 10/10 = 1.0 (all retrieved is relevant)
        assert q_metrics["precision@5"] == 1.0

    def test_evaluate_multiple_queries(self):
        """Test evaluate with multiple queries and macro-averaging."""
        # Create documents
        doc1 = Document.from_text("doc1", "First document text here.")
        doc2 = Document.from_text("doc2", "Second document content here.")

        # Query 1: perfect recall
        text_hash1 = compute_hash("First")
        anchor1 = Anchor("doc1", 0, 5, text_hash1)
        query1 = Query("q1", "What is first?", (anchor1,))
        result1 = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)

        # Query 2: zero recall (wrong span)
        text_hash2 = compute_hash("Second")
        anchor2 = Anchor("doc2", 0, 6, text_hash2)
        query2 = Query("q2", "What is second?", (anchor2,))
        result2 = RetrievalResult(
            rank=1, score=0.8, document_id="doc2", start=15, end=22
        )  # "content"

        # Evaluate
        run = evaluate(
            documents={"doc1": doc1, "doc2": doc2},
            queries=[query1, query2],
            retrieval_results={"q1": [result1], "q2": [result2]},
            k=5,
        )

        # Per-query metrics
        assert run.per_query_metrics["q1"]["recall@5"] == 1.0
        assert run.per_query_metrics["q2"]["recall@5"] == 0.0

        # Macro-average: (1.0 + 0.0) / 2 = 0.5
        assert run.aggregate_metrics["mean_recall@5"] == 0.5


class TestEvaluateValidation:
    """Tests for anchor validation during evaluate()."""

    def test_evaluate_missing_document_raises_error(self):
        """Test that referencing a missing document raises DocumentNotFoundError."""
        # Create document
        doc = Document.from_text("doc1", "Test document")

        # Create query with anchor referencing nonexistent document
        anchor = Anchor("doc999", 0, 4, "somehash")
        query = Query("q1", "Test query", (anchor,))

        # Evaluate should raise DocumentNotFoundError
        with pytest.raises(DocumentNotFoundError) as exc_info:
            evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": []},
                k=5,
            )

        assert exc_info.value.document_id == "doc999"
        assert exc_info.value.query_id == "q1"

    def test_evaluate_invalid_k_raises_error(self):
        """Test that invalid K value raises EvaluationError."""
        doc = Document.from_text("doc1", "Test")
        anchor = Anchor("doc1", 0, 4, doc.sha256)
        query = Query("q1", "Test", (anchor,))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": []},
                k=0,  # Invalid K
            )

        assert "K must be positive" in str(exc_info.value)

    def test_evaluate_invalid_min_overlap_raises_error(self):
        """Test that invalid min_overlap raises EvaluationError."""
        doc = Document.from_text("doc1", "Test")
        anchor = Anchor("doc1", 0, 4, doc.sha256)
        query = Query("q1", "Test", (anchor,))

        with pytest.raises(EvaluationError) as exc_info:
            evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": []},
                k=5,
                min_overlap=1.5,  # Invalid - must be in [0, 1]
            )

        assert "min_overlap must be between 0 and 1" in str(exc_info.value)


class TestEvaluateMapping:
    """Tests for chunk-to-span mapping during evaluate()."""

    def test_evaluate_whitespace_normalized_mapping(self):
        """Test evaluate with whitespace-normalized chunk mapping."""
        # Create document
        doc = Document.from_text("doc1", "The   quick    brown   fox")

        # Create query with anchor
        anchor = Anchor("doc1", 0, 26, doc.sha256)
        query = Query("q1", "Test", (anchor,))

        # Chunk with different whitespace
        result = RetrievalResult(rank=1, score=0.9, text="The quick brown fox")

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Should map successfully with MAPPED_NORMALIZED status
        assert run.mapper_stats["MAPPED_NORMALIZED"] == 1
        assert run.per_query_metrics["q1"]["recall@5"] == 1.0

    def test_evaluate_unmapped_chunk(self):
        """Test evaluate with unmapped chunk."""
        # Create document
        doc = Document.from_text("doc1", "This is the content.")

        # Create query with anchor
        text_hash = compute_hash("This")
        anchor = Anchor("doc1", 0, 4, text_hash)
        query = Query("q1", "Test", (anchor,))

        # Chunk that doesn't exist in document
        result = RetrievalResult(rank=1, score=0.9, text="nonexistent chunk text")

        # Evaluate with high unmapped rate threshold to allow this test
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            max_unmapped_rate=1.0,  # Allow 100% unmapped for this test
        )

        # Should have unmapped chunk
        assert run.mapper_stats["UNMAPPED"] == 1
        # Recall should be 0 (no coverage)
        assert run.per_query_metrics["q1"]["recall@5"] == 0.0

    def test_evaluate_unmapped_rate_threshold_exceeded(self):
        """Test that exceeding unmapped rate threshold raises error."""
        # Create document
        doc = Document.from_text("doc1", "Test content")

        # Create query
        text_hash = compute_hash("Test")
        anchor = Anchor("doc1", 0, 4, text_hash)
        query = Query("q1", "Test", (anchor,))

        # Two chunks: one maps, one doesn't
        results = [
            RetrievalResult(rank=1, score=0.9, text="Test"),
            RetrievalResult(rank=2, score=0.8, text="nonexistent"),
        ]

        # Unmapped rate will be 50% (1/2), exceeding 10% threshold
        with pytest.raises(EvaluationError) as exc_info:
            evaluate(
                documents={"doc1": doc},
                queries=[query],
                retrieval_results={"q1": results},
                k=5,
                max_unmapped_rate=0.1,  # 10% threshold
            )

        assert "Unmapped chunk rate" in str(exc_info.value)
        assert "exceeds threshold" in str(exc_info.value)


class TestEvaluateMetrics:
    """Tests for metric computation in evaluate()."""

    def test_evaluate_hit_metric_with_partial_overlap(self):
        """Test Hit@K metric with partial overlap."""
        # Create document
        doc = Document.from_text("doc1", "ABCDEFGHIJ")

        # Anchor for "ABCDE" (5 chars)
        text_hash = compute_hash("ABCDE")
        anchor = Anchor("doc1", 0, 5, text_hash)
        query = Query("q1", "Test", (anchor,))

        # Retrieved "ABC" (3 chars) = 60% overlap, should pass 0.5 threshold
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=3)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
            min_overlap=0.5,
        )

        # Hit@5 should be 1 (passes threshold)
        assert run.per_query_metrics["q1"]["hit@5"] == 1.0

    def test_evaluate_full_evidence_metric_multiple_anchors(self):
        """Test FullEvidence@K with multiple anchors."""
        # Create document
        doc = Document.from_text("doc1", "Alpha Beta Gamma Delta")

        # Two anchors: "Alpha" and "Gamma"
        text_hash1 = compute_hash("Alpha")
        text_hash2 = compute_hash("Gamma")
        anchor1 = Anchor("doc1", 0, 5, text_hash1)
        anchor2 = Anchor("doc1", 11, 16, text_hash2)
        query = Query("q1", "Test", (anchor1, anchor2))

        # Only retrieve "Alpha", not "Gamma"
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=5)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # FullEvidence@5 should be 0 (not all anchors covered)
        assert run.per_query_metrics["q1"]["full_evidence@5"] == 0.0
        # But Hit@5 should be 1 (at least one anchor covered)
        assert run.per_query_metrics["q1"]["hit@5"] == 1.0

    def test_evaluate_iou_metric(self):
        """Test IoU diagnostic metric."""
        # Create document
        doc = Document.from_text("doc1", "0123456789")

        # Gold: [0, 5)
        text_hash = compute_hash("01234")
        anchor = Anchor("doc1", 0, 5, text_hash)
        query = Query("q1", "Test", (anchor,))

        # Retrieved: [3, 8) - overlaps at [3, 5)
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=3, end=8)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # IoU = |intersection| / |union|
        # intersection = [3, 5) = 2 chars
        # union = [0, 8) = 8 chars
        # IoU = 2/8 = 0.25
        assert run.per_query_metrics["q1"]["iou"] == 0.25

    def test_evaluate_retrieved_chars_metric(self):
        """Test retrieved character count metric."""
        # Create document
        doc = Document.from_text("doc1", "Test document content")

        # Anchor
        text_hash = compute_hash("Test")
        anchor = Anchor("doc1", 0, 4, text_hash)
        query = Query("q1", "Test", (anchor,))

        # Retrieved 10 characters
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=10)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Should track retrieved character count
        assert run.per_query_metrics["q1"]["retrieved_chars"] == 10.0
        assert run.aggregate_metrics["mean_retrieved_chars"] == 10.0


class TestEvaluateEdgeCases:
    """Edge case tests for evaluate()."""

    def test_evaluate_empty_retrieval_results(self):
        """Test evaluate with no retrieval results."""
        # Create document
        doc = Document.from_text("doc1", "Test")

        # Create query with anchor
        anchor = Anchor("doc1", 0, 4, doc.sha256)
        query = Query("q1", "Test", (anchor,))

        # No retrieval results
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": []},
            k=5,
        )

        # Metrics should reflect zero coverage
        assert run.per_query_metrics["q1"]["recall@5"] == 0.0
        assert run.per_query_metrics["q1"]["precision@5"] == 0.0

    def test_evaluate_query_with_no_anchors(self):
        """Test evaluate with query that has no anchors."""
        # Create document
        doc = Document.from_text("doc1", "Test")

        # Query with no anchors
        query = Query("q1", "Test question", tuple())

        # Some retrieval results
        result = RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=4)

        # Evaluate
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": [result]},
            k=5,
        )

        # Should have zero metrics for query with no gold anchors
        assert run.per_query_metrics["q1"]["recall@5"] == 0.0
        assert run.per_query_metrics["q1"]["precision@5"] == 0.0

    def test_evaluate_respects_k_parameter(self):
        """Test that metrics respect the K parameter."""
        # Create document
        doc = Document.from_text("doc1", "ABCDEFGHIJ")

        # Anchor for entire document
        anchor = Anchor("doc1", 0, 10, doc.sha256)
        query = Query("q1", "Test", (anchor,))

        # 3 results: ranks 1, 2, 3 covering different parts
        results = [
            RetrievalResult(rank=1, score=0.9, document_id="doc1", start=0, end=3),  # ABC
            RetrievalResult(rank=2, score=0.8, document_id="doc1", start=3, end=6),  # DEF
            RetrievalResult(rank=3, score=0.7, document_id="doc1", start=6, end=10),  # GHIJ
        ]

        # Evaluate with K=2 (should only use first 2 results)
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": results},
            k=2,
        )

        # Recall@2 should be 6/10 = 0.6 (only ABC+DEF covered)
        assert run.per_query_metrics["q1"]["recall@2"] == 0.6

        # Now evaluate with K=3 (should use all 3 results)
        run = evaluate(
            documents={"doc1": doc},
            queries=[query],
            retrieval_results={"q1": results},
            k=3,
        )

        # Recall@3 should be 10/10 = 1.0 (all covered)
        assert run.per_query_metrics["q1"]["recall@3"] == 1.0


class TestEvaluateSmallSampleWarning:
    """Tests for small-sample warning when gold set has fewer than 30 queries.

    Validates: Requirements 24.1, 24.2, 24.3
    """

    def _make_query(self, query_id: str) -> tuple[Query, Document]:
        """Helper to create a minimal query + document pair."""
        doc = Document.from_text(query_id, "Test content for query.")
        anchor = Anchor(query_id, 0, 4, compute_hash("Test"))
        query = Query(query_id, f"Question for {query_id}?", (anchor,))
        return query, doc

    def test_small_sample_emits_warning_for_single_query(self):
        """Warning is emitted when gold set has only 1 query (< 30). (Req 24.1, 24.2)"""
        query, doc = self._make_query("q1")

        with pytest.warns(UserWarning, match=r"Gold set has only 1 quer"):
            evaluate(
                documents={"q1": doc},
                queries=[query],
                retrieval_results={"q1": []},
                k=5,
            )

    def test_small_sample_warning_includes_query_count(self):
        """Warning message includes the actual query count. (Req 24.2)"""
        queries = []
        documents = {}
        retrieval_results = {}

        for i in range(5):
            qid = f"q{i}"
            query, doc = self._make_query(qid)
            queries.append(query)
            documents[qid] = doc
            retrieval_results[qid] = []

        with pytest.warns(UserWarning, match=r"Gold set has only 5 quer"):
            evaluate(
                documents=documents,
                queries=queries,
                retrieval_results=retrieval_results,
                k=5,
            )

    def test_small_sample_warning_does_not_prevent_evaluation(self):
        """Warning does not stop evaluation — Run is still returned. (Req 24.3)"""
        query, doc = self._make_query("q1")

        import warnings as _warnings

        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore", UserWarning)
            run = evaluate(
                documents={"q1": doc},
                queries=[query],
                retrieval_results={"q1": []},
                k=5,
            )

        assert run is not None
        assert "q1" in run.per_query_metrics

    def test_no_warning_for_exactly_30_queries(self):
        """No warning is emitted when gold set has exactly 30 queries."""
        queries = []
        documents = {}
        retrieval_results = {}

        for i in range(30):
            qid = f"q{i}"
            query, doc = self._make_query(qid)
            queries.append(query)
            documents[qid] = doc
            retrieval_results[qid] = []

        # Should not emit any UserWarning
        with pytest.warns(Warning) as warning_list:
            # emit a dummy warning so pytest.warns doesn't fail on empty
            import warnings as _warnings
            _warnings.warn("sentinel", UserWarning)
            evaluate(
                documents=documents,
                queries=queries,
                retrieval_results=retrieval_results,
                k=5,
            )

        # Filter out the sentinel; no spanchor warning should be present
        spanchor_warns = [
            w for w in warning_list.list
            if "Gold set has only" in str(w.message)
        ]
        assert spanchor_warns == []

    def test_no_warning_for_more_than_30_queries(self):
        """No warning is emitted when gold set has more than 30 queries."""
        queries = []
        documents = {}
        retrieval_results = {}

        for i in range(35):
            qid = f"q{i}"
            query, doc = self._make_query(qid)
            queries.append(query)
            documents[qid] = doc
            retrieval_results[qid] = []

        with pytest.warns(Warning) as warning_list:
            import warnings as _warnings
            _warnings.warn("sentinel", UserWarning)
            evaluate(
                documents=documents,
                queries=queries,
                retrieval_results=retrieval_results,
                k=5,
            )

        spanchor_warns = [
            w for w in warning_list.list
            if "Gold set has only" in str(w.message)
        ]
        assert spanchor_warns == []
