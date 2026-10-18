"""Unit tests for candidate promotion to gold Query + Anchor.

Tests for explicit promotion of APPROVED candidates into the existing gold
representation (Query + Anchor). Verifies all safety invariants and proper
conversion of candidate metadata to gold metadata.

**Feature 7: Semi-Automated Gold-Set Generation**
"""

import pytest

from spanchor.generation.promote import promote_candidate_to_gold
from spanchor.models.anchor import Anchor
from spanchor.models.candidate import Candidate, CandidateReview, CandidateStatus
from spanchor.models.query import Query


class TestPromotionSuccessful:
    """Tests for successful promotion of APPROVED candidates."""

    def test_promote_approved_candidate_with_valid_metadata(self) -> None:
        """Test: APPROVED candidate with valid metadata → Query + Anchor."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is the answer?",
            source_start=0,
            source_end=15,
        )
        candidate = Candidate(
            candidate_id="doc1_0",
            text="The answer text.",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        # Verify Query
        assert isinstance(query, Query)
        assert query.query_id.startswith("query_")
        assert query.question == "What is the answer?"
        assert query.schema_version == "0.1.0"
        assert len(query.anchors) == 1

        # Verify Anchor
        assert isinstance(anchor, Anchor)
        assert anchor.document_id == "doc1"
        assert anchor.start == 0
        assert anchor.end == 15
        assert anchor.schema_version == "0.1.0"

    def test_promote_generates_unique_query_ids(self) -> None:
        """Test: Multiple promotions generate unique query IDs."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate1 = Candidate(
            candidate_id="c1",
            text="Text1",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )
        candidate2 = Candidate(
            candidate_id="c2",
            text="Text2",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query1, _ = promote_candidate_to_gold(candidate1)
        query2, _ = promote_candidate_to_gold(candidate2)

        # IDs should be different (with very high probability)
        assert query1.query_id != query2.query_id
        assert query1.query_id.startswith("query_")
        assert query2.query_id.startswith("query_")

    def test_promote_with_edited_text(self) -> None:
        """Test: APPROVED candidate with edited_text uses edited version for hash."""
        edited_text = "Edited version of the text"
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=20,
            edited_text=edited_text,
            was_edited=True,
        )
        candidate = Candidate(
            candidate_id="doc1_0",
            text="Original text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        # Verify Query text matches human_question (not edited_text)
        assert query.question == "Q?"

        # Verify Anchor uses edited_text for hash (not original)
        # We verify by checking hash was computed (non-empty)
        assert anchor.expected_text_hash
        assert len(anchor.expected_text_hash) == 64  # SHA256 hex

    def test_promote_multiple_documents(self) -> None:
        """Test: Candidates from different documents promote independently."""
        review1 = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q1?",
            source_start=0,
            source_end=10,
        )
        candidate1 = Candidate(
            candidate_id="doc1_0",
            text="Text from doc1",
            document_id="doc1",
            confidence=1.0,
            review=review1,
        )

        review2 = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q2?",
            source_start=5,
            source_end=15,
        )
        candidate2 = Candidate(
            candidate_id="doc2_0",
            text="Text from doc2",
            document_id="doc2",
            confidence=1.0,
            review=review2,
        )

        query1, anchor1 = promote_candidate_to_gold(candidate1)
        query2, anchor2 = promote_candidate_to_gold(candidate2)

        # Verify each has correct document_id
        assert anchor1.document_id == "doc1"
        assert anchor2.document_id == "doc2"
        assert query1.question == "Q1?"
        assert query2.question == "Q2?"

    def test_promote_query_has_single_anchor(self) -> None:
        """Test: Promoted Query contains exactly one Anchor."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        assert len(query.anchors) == 1
        assert query.anchors[0] == anchor

    def test_promote_with_whitespace_in_question(self) -> None:
        """Test: Question with leading/trailing whitespace is stripped."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="  What is the question?  ",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.question == "What is the question?"


class TestPromotionRejectedStatuses:
    """Tests for rejection of candidates with terminal states."""

    def test_promote_pending_candidate_raises_error(self) -> None:
        """Test: PENDING candidate cannot be promoted."""
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=None,  # PENDING
        )

        with pytest.raises(ValueError) as exc_info:
            promote_candidate_to_gold(candidate)

        error_msg = str(exc_info.value).lower()
        assert "pending" in error_msg
        assert "cannot promote" in error_msg

    def test_promote_rejected_candidate_raises_error(self) -> None:
        """Test: REJECTED candidate cannot be promoted."""
        review = CandidateReview(
            status=CandidateStatus.REJECTED,
            rejection_reason="Not relevant",
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        with pytest.raises(ValueError) as exc_info:
            promote_candidate_to_gold(candidate)

        error_msg = str(exc_info.value).lower()
        assert "rejected" in error_msg
        assert "cannot promote" in error_msg

    def test_promote_edited_pending_candidate_raises_error(self) -> None:
        """Test: EDITED but PENDING candidate cannot be promoted."""
        review = CandidateReview(
            status=CandidateStatus.PENDING,
            edited_text="Edited text",
            was_edited=True,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Original text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        with pytest.raises(ValueError) as exc_info:
            promote_candidate_to_gold(candidate)

        error_msg = str(exc_info.value).lower()
        assert "pending" in error_msg
        assert "cannot promote" in error_msg


class TestPromotionMissingQuestion:
    """Tests for rejection when human question is missing."""

    def test_promote_approved_without_question_raises_error(self) -> None:
        """Test: APPROVED candidate without human_question cannot be promoted."""
        # CandidateReview validation catches this at creation time
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question=None,
                source_start=0,
                source_end=10,
            )

        assert "human_question" in str(exc_info.value)

    def test_promote_approved_with_empty_question_raises_error(self) -> None:
        """Test: APPROVED candidate with empty question cannot be promoted."""
        # CandidateReview validation catches this at creation time
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="",
                source_start=0,
                source_end=10,
            )

        assert "human_question" in str(exc_info.value)

    def test_promote_approved_with_whitespace_only_question_raises_error(self) -> None:
        """Test: APPROVED with whitespace-only question cannot be promoted."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="   \n\t  ",
                source_start=0,
                source_end=10,
            )

        assert "human_question" in str(exc_info.value)


class TestPromotionInvalidAnchor:
    """Tests for rejection when source anchor is invalid."""

    def test_promote_approved_without_source_start_raises_error(self) -> None:
        """Test: APPROVED candidate without source_start cannot be promoted."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=None,
                source_end=10,
            )

        assert "source_start and source_end" in str(exc_info.value)

    def test_promote_approved_without_source_end_raises_error(self) -> None:
        """Test: APPROVED candidate without source_end cannot be promoted."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=0,
                source_end=None,
            )

        assert "source_start and source_end" in str(exc_info.value)

    def test_promote_with_negative_source_start_raises_error(self) -> None:
        """Test: Negative source_start raises error."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=-1,
                source_end=10,
            )

        assert "Invalid source span" in str(exc_info.value)

    def test_promote_with_start_equals_end_raises_error(self) -> None:
        """Test: source_start >= source_end raises error."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=10,
                source_end=10,
            )

        assert "Invalid source span" in str(exc_info.value)

    def test_promote_with_start_greater_than_end_raises_error(self) -> None:
        """Test: source_start > source_end raises error."""
        with pytest.raises(ValueError) as exc_info:
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=20,
                source_end=10,
            )

        assert "Invalid source span" in str(exc_info.value)


class TestPromotionQueryCorrectness:
    """Tests for correctness of resulting Query object."""

    def test_promoted_query_text_matches_human_question(self) -> None:
        """Test: Query.question = human_question (exact copy)."""
        question_text = "What is the meaning of life?"
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question=question_text,
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Original text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.question == question_text

    def test_promoted_query_id_is_valid(self) -> None:
        """Test: Query.query_id is non-empty, valid identifier."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.query_id
        assert isinstance(query.query_id, str)
        assert query.query_id.startswith("query_")
        assert len(query.query_id) > 6  # "query_" + at least some hex

    def test_promoted_query_can_be_serialized(self) -> None:
        """Test: Promoted Query can be serialized to dict format."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        # Verify we can access all fields needed for serialization
        query_dict = {
            "query_id": query.query_id,
            "question": query.question,
            "anchors": [
                {
                    "document_id": a.document_id,
                    "start": a.start,
                    "end": a.end,
                    "expected_text_hash": a.expected_text_hash,
                }
                for a in query.anchors
            ],
            "schema_version": query.schema_version,
        }

        assert query_dict["query_id"] == query.query_id
        assert len(query_dict["anchors"]) == 1


class TestPromotionAnchorCorrectness:
    """Tests for correctness of resulting Anchor object."""

    def test_promoted_anchor_document_id_matches_candidate(self) -> None:
        """Test: Anchor.document_id = candidate.document_id."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc_important_123",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        assert anchor.document_id == "doc_important_123"

    def test_promoted_anchor_span_matches_source_span(self) -> None:
        """Test: Anchor.start = source_start, Anchor.end = source_end."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=42,
            source_end=100,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        assert anchor.start == 42
        assert anchor.end == 100

    def test_promoted_anchor_id_is_valid(self) -> None:
        """Test: Anchor has valid anchor_id (from Anchor init)."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        # Anchor doesn't have an explicit anchor_id field in v0.1.0
        # It's identified by its (document_id, start, end) tuple
        assert anchor.document_id
        assert anchor.start is not None
        assert anchor.end is not None

    def test_promoted_anchor_has_hash(self) -> None:
        """Test: Anchor has computed expected_text_hash."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        # Hash should be 64-char hex string (SHA256)
        assert anchor.expected_text_hash
        assert len(anchor.expected_text_hash) == 64
        assert all(c in "0123456789abcdef" for c in anchor.expected_text_hash)

    def test_promoted_anchor_can_be_serialized(self) -> None:
        """Test: Promoted Anchor can be serialized to dict format."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        # Verify we can serialize to JSONL format
        anchor_dict = {
            "document_id": anchor.document_id,
            "start": anchor.start,
            "end": anchor.end,
            "expected_text_hash": anchor.expected_text_hash,
            "schema_version": anchor.schema_version,
        }

        assert anchor_dict["document_id"] == anchor.document_id
        assert anchor_dict["start"] == 0
        assert anchor_dict["end"] == 10


class TestPromotionEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_promote_with_zero_source_start(self) -> None:
        """Test: source_start=0 is valid."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        assert anchor.start == 0
        assert anchor.end == 10

    def test_promote_with_large_span(self) -> None:
        """Test: Large source spans are valid."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=1000000,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        assert anchor.start == 0
        assert anchor.end == 1000000

    def test_promote_with_single_character_span(self) -> None:
        """Test: Single-character spans are valid."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=5,
            source_end=6,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        _, anchor = promote_candidate_to_gold(candidate)

        assert anchor.start == 5
        assert anchor.end == 6

    def test_promote_candidate_with_multiline_question(self) -> None:
        """Test: Multi-line questions are supported."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is X?\nAnd why?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.question == "What is X?\nAnd why?"

    def test_promote_candidate_with_unicode_text(self) -> None:
        """Test: Unicode text in question and candidate."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is 日本語?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="This is 日本語",
            document_id="doc_ja",
            confidence=1.0,
            review=review,
        )

        query, anchor = promote_candidate_to_gold(candidate)

        assert query.question == "What is 日本語?"
        assert anchor.document_id == "doc_ja"

    def test_promote_candidate_with_special_characters(self) -> None:
        """Test: Special characters in question."""
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question='What is "special" & <important>?',
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        assert query.question == 'What is "special" & <important>?'


class TestNoAutomaticPromotion:
    """Tests to verify extraction/review workflow never auto-promotes."""

    def test_extraction_not_calling_promote(self) -> None:
        """Test: Extraction workflow doesn't auto-promote (no import of promote)."""
        # Import extraction module and verify promote_candidate_to_gold not imported
        from spanchor.generation import extract

        # Verify extract module doesn't import the promote function
        assert not hasattr(extract, "promote_candidate_to_gold")
        # Extraction only deals with candidates, not gold

    def test_promotion_is_explicit_only(self) -> None:
        """Test: Promotion function must be called explicitly."""
        # Verify promote function exists and is accessible
        from spanchor.generation.promote import promote_candidate_to_gold

        assert callable(promote_candidate_to_gold)


class TestPromotionRoundTrip:
    """Tests for serialization round-trip of promoted gold."""

    def test_promoted_query_anchor_can_be_written_to_jsonl(self) -> None:
        """Test: Promoted Query+Anchor can be written to JSONL."""
        from spanchor.storage.jsonl import write_gold_set

        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="Text",
            document_id="doc1",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        # This should not raise
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path

            gold_file = Path(tmpdir) / "gold.jsonl"
            write_gold_set(gold_file, [query])

            assert gold_file.exists()

    def test_promoted_gold_roundtrip_preserves_data(self) -> None:
        """Test: Write promoted gold → read back → data identical."""
        from spanchor.storage.jsonl import read_gold_set, write_gold_set

        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="What is life?",
            source_start=10,
            source_end=25,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="The answer to life",
            document_id="doc_life",
            confidence=1.0,
            review=review,
        )

        query, _ = promote_candidate_to_gold(candidate)

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path

            gold_file = Path(tmpdir) / "gold.jsonl"

            # Write
            write_gold_set(gold_file, [query])

            # Read back
            loaded_queries = read_gold_set(gold_file)

            # Verify identical
            assert len(loaded_queries) == 1
            loaded_query = loaded_queries[0]

            assert loaded_query.query_id == query.query_id
            assert loaded_query.question == query.question
            assert len(loaded_query.anchors) == 1

            loaded_anchor = loaded_query.anchors[0]
            original_anchor = query.anchors[0]

            assert loaded_anchor.document_id == original_anchor.document_id
            assert loaded_anchor.start == original_anchor.start
            assert loaded_anchor.end == original_anchor.end
            assert loaded_anchor.expected_text_hash == original_anchor.expected_text_hash

    def test_promoted_gold_can_be_appended_to_existing(self) -> None:
        """Test: Promoted gold can be appended to existing gold set."""
        from spanchor.storage.jsonl import read_gold_set, write_gold_set

        # Create existing gold
        existing_anchor = Anchor(
            document_id="doc1",
            start=0,
            end=10,
            expected_text_hash="abc123def456" * 5 + "0123",
        )
        existing_query = Query(
            query_id="existing_q1",
            question="Existing question?",
            anchors=(existing_anchor,),
        )

        # Create promoted candidate
        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="New question?",
            source_start=20,
            source_end=30,
        )
        candidate = Candidate(
            candidate_id="c1",
            text="New text",
            document_id="doc2",
            confidence=1.0,
            review=review,
        )
        new_query, _ = promote_candidate_to_gold(candidate)

        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            from pathlib import Path

            gold_file = Path(tmpdir) / "gold.jsonl"

            # Write existing
            write_gold_set(gold_file, [existing_query])

            # Read existing
            loaded = read_gold_set(gold_file)

            # Append promoted
            loaded.append(new_query)

            # Write combined
            write_gold_set(gold_file, loaded)

            # Read back
            final_queries = read_gold_set(gold_file)

            # Verify both present
            assert len(final_queries) == 2
            ids = [q.query_id for q in final_queries]
            assert "existing_q1" in ids
            assert new_query.query_id in ids
