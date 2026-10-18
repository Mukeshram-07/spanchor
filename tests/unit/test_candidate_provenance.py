"""Unit tests for candidate → gold provenance tracking.

Tests for traceability of candidate ID through promotion to resulting query ID.
Verifies provenance preservation, determinism, and round-trip serialization.

**Feature 7: Semi-Automated Gold-Set Generation**
"""

import tempfile
from pathlib import Path

from spanchor.generation.promote import promote_candidate_to_gold
from spanchor.models.candidate import Candidate, CandidateReview, CandidateStatus
from spanchor.storage.jsonl import read_gold_set, write_gold_set


class TestProvenancePreserved:
    """Tests for candidate_id preservation through promotion."""

    def test_promoted_query_has_candidate_id(self) -> None:
        """Test: Promoted query has candidate_id field set."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is the question?",
            source_start=0,
            source_end=20,
        )
        candidate = Candidate(
            candidate_id="doc1_0",
            text="Some candidate text.",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.candidate_id == "doc1_0"

    def test_candidate_id_not_none(self) -> None:
        """Test: candidate_id is not None (falsy check)."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="candidate_123",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.candidate_id is not None
        assert len(query.candidate_id) > 0

    def test_different_candidates_have_different_provenance(self) -> None:
        """Test: Different candidates produce queries with different candidate_id."""
        review_template = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Question?",
            source_start=0,
            source_end=5,
        )

        candidate1 = Candidate(
            candidate_id="cand_a",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review_template,
        )
        candidate2 = Candidate(
            candidate_id="cand_b",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review_template,
        )

        query1, _ = promote_candidate_to_gold(candidate1)
        query2, _ = promote_candidate_to_gold(candidate2)

        assert query1.candidate_id == "cand_a"
        assert query2.candidate_id == "cand_b"
        assert query1.candidate_id != query2.candidate_id

    def test_same_candidate_id_multiple_promotions_traces_to_same_source(self) -> None:
        """Test: Same candidate can be promoted multiple times (provenance always traceable)."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q1?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="source_123",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query1, _ = promote_candidate_to_gold(candidate)
        query2, _ = promote_candidate_to_gold(candidate)

        # Both promoted queries trace back to same candidate
        assert query1.candidate_id == "source_123"
        assert query2.candidate_id == "source_123"
        # But query IDs are unique
        assert query1.query_id != query2.query_id


class TestProvenanceRoundTrip:
    """Tests for provenance survival through serialization."""

    def test_promoted_query_with_candidate_id_serializes_to_dict(self) -> None:
        """Test: Query with candidate_id converts to dict correctly."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Question?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="doc1_sentence_0",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        # Serialize Query to dict (mimics what write_queries does)
        query_dict = {
            "query_id": query.query_id,
            "question": query.question,
            "anchors": [
                {
                    "document_id": anchor.document_id,
                    "start": anchor.start,
                    "end": anchor.end,
                    "expected_text_hash": anchor.expected_text_hash,
                    "schema_version": anchor.schema_version,
                }
            ],
            "schema_version": query.schema_version,
            "candidate_id": query.candidate_id,
        }

        # Verify candidate_id is in the dict
        assert query_dict["candidate_id"] == "doc1_sentence_0"

    def test_promoted_gold_with_provenance_roundtrip_jsonl(self) -> None:
        """Test: Query with candidate_id survives JSONL write→read cycle."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is X?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="extraction_001",
            text="Test text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        # Write to JSONL and read back
        with tempfile.TemporaryDirectory() as tmpdir:
            gold_file = Path(tmpdir) / "gold.jsonl"

            # Write Query
            write_gold_set(gold_file, [query])

            # Read back
            queries = read_gold_set(gold_file)

            assert len(queries) == 1
            loaded_query = queries[0]
            assert loaded_query.candidate_id == "extraction_001"

    def test_multiple_promoted_candidates_roundtrip(self) -> None:
        """Test: Multiple promoted queries preserve individual provenance through serialization."""
        candidates_data = [
            ("cand_1", "First text"),
            ("cand_2", "Second text"),
            ("cand_3", "Third text"),
        ]

        queries = []
        for cand_id, text in candidates_data:
            review = CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question=f"Q for {cand_id}?",
                source_start=0,
                source_end=len(text),
            )
            candidate = Candidate(
                candidate_id=cand_id,
                text=text,
                document_id="doc1",
                confidence=1.0,
                review=review,
            )
            query, _ = promote_candidate_to_gold(candidate)
            queries.append(query)

        # Round-trip through JSONL
        with tempfile.TemporaryDirectory() as tmpdir:
            gold_file = Path(tmpdir) / "gold.jsonl"
            write_gold_set(gold_file, queries)
            loaded_queries = read_gold_set(gold_file)

        # Verify provenance preserved for all
        assert len(loaded_queries) == 3
        assert loaded_queries[0].candidate_id == "cand_1"
        assert loaded_queries[1].candidate_id == "cand_2"
        assert loaded_queries[2].candidate_id == "cand_3"


class TestProvenanceTraceable:
    """Tests for candidate → query_id traceability."""

    def test_candidate_query_association_traceable(self) -> None:
        """Test: Can trace from candidate_id back to query_id."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Find X?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="source_ref_123",
            text="Value",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        # Given the candidate_id, we can trace to the resulting query_id
        assert query.candidate_id == "source_ref_123"
        # The query_id is deterministically related to promotion
        # (not to candidate_id, but candidate_id is traceable)
        assert query.query_id.startswith("query_")
        assert len(query.query_id) > 6

    def test_provenance_metadata_complete(self) -> None:
        """Test: Query has all necessary provenance metadata."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Question?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="prov_test",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        # Verify complete traceability
        assert query.candidate_id == candidate.candidate_id
        assert anchor.document_id == candidate.document_id
        assert candidate.review is not None  # Type guard
        assert anchor.start == candidate.review.source_start
        assert anchor.end == candidate.review.source_end
        assert query.question == candidate.review.human_question

    def test_provenance_across_multiple_documents(self) -> None:
        """Test: Provenance works correctly with multiple documents."""
        candidates = [
            Candidate(
                candidate_id="doc1_cand_0",
                text="Text from doc 1",
                document_id="doc1",
                confidence=1.0,
                review=CandidateReview(
                    status=CandidateStatus.APPROVED,
                    human_question="Q1?",
                    source_start=0,
                    source_end=5,
                ),
            ),
            Candidate(
                candidate_id="doc2_cand_0",
                text="Text from doc 2",
                document_id="doc2",
                confidence=1.0,
                review=CandidateReview(
                    status=CandidateStatus.APPROVED,
                    human_question="Q2?",
                    source_start=0,
                    source_end=5,
                ),
            ),
        ]

        promoted = [promote_candidate_to_gold(c) for c in candidates]

        # Verify provenance tracks document source correctly
        assert promoted[0][0].candidate_id == "doc1_cand_0"
        assert promoted[0][1].document_id == "doc1"

        assert promoted[1][0].candidate_id == "doc2_cand_0"
        assert promoted[1][1].document_id == "doc2"


class TestProvenanceDeterministic:
    """Tests for deterministic provenance."""

    def test_candidate_id_is_deterministic_source(self) -> None:
        """Test: candidate_id is deterministic (from extraction)."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=5,
        )

        # Create two candidates with identical properties
        candidate_a = Candidate(
            candidate_id="deterministic_001",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )
        candidate_b = Candidate(
            candidate_id="deterministic_001",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query_a, _ = promote_candidate_to_gold(candidate_a)
        query_b, _ = promote_candidate_to_gold(candidate_b)

        # candidate_id provenance is identical
        assert query_a.candidate_id == query_b.candidate_id
        # query_id will be different (UUID-based), but that's okay
        # The provenance link (candidate_id → query) is deterministic

    def test_provenance_stable_across_repeated_promotion(self) -> None:
        """Test: Repeated promotion of same candidate preserves provenance."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="stable_prov_test",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        # Promote multiple times
        for _ in range(3):
            query, _ = promote_candidate_to_gold(candidate)
            # Provenance always points back to same candidate
            assert query.candidate_id == "stable_prov_test"


class TestProvenanceEdgeCases:
    """Tests for provenance in edge cases."""

    def test_provenance_with_unicode_candidate_id(self) -> None:
        """Test: Provenance works with unicode in candidate_id."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Question?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="doc_你好_0",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.candidate_id == "doc_你好_0"

    def test_provenance_with_special_chars_candidate_id(self) -> None:
        """Test: Provenance preserves special characters in candidate_id."""
        special_ids = [
            "doc:1:sent:0",
            "doc-1_sent-0",
            "doc/1/sent/0",
            "doc.1.sent.0",
        ]

        for cand_id in special_ids:
            review = CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=0,
                source_end=5,
            )
            candidate = Candidate(
                candidate_id=cand_id,
                text="Text",
                document_id="doc1",
                confidence=1.0,
                review=review,
            )

            query, _ = promote_candidate_to_gold(candidate)

            assert query.candidate_id == cand_id

    def test_provenance_with_long_candidate_id(self) -> None:
        """Test: Provenance handles long candidate_id strings."""
        long_id = "doc_" + "x" * 500  # Very long candidate ID
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id=long_id,
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.candidate_id == long_id


class TestProvenanceValidation:
    """Tests for provenance validation and consistency."""

    def test_promoted_query_candidate_id_matches_source_candidate(self) -> None:
        """Test: Query candidate_id exactly matches source candidate_id."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=5,
        )
        candidate = Candidate(
            candidate_id="source_match_test",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        # Exact match, not transformed
        assert query.candidate_id == candidate.candidate_id

    def test_provenance_not_dependent_on_question_content(self) -> None:
        """Test: Different questions don't affect provenance."""
        candidate_id = "same_source"
        document_id = "doc1"

        reviews = [
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Question 1?",
                source_start=0,
                source_end=5,
            ),
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Question 2?",
                source_start=0,
                source_end=5,
            ),
        ]

        queries = []
        for review in reviews:
            candidate = Candidate(
                candidate_id=candidate_id,
                text="Text",
                document_id=document_id,
                confidence=1.0,
                review=review,
            )
            query, _ = promote_candidate_to_gold(candidate)
            queries.append(query)

        # Same candidate_id provenance regardless of question
        assert queries[0].candidate_id == candidate_id
        assert queries[1].candidate_id == candidate_id
        # But queries are different
        assert queries[0].query_id != queries[1].query_id


# **Validates: Feature 7 Phase III — Provenance (candidate_id → query_id)
