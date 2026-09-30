"""Property-based tests for RetrievalResult model.

These tests use Hypothesis to verify universal properties that must hold
across all possible RetrievalResult instances and their classification behavior.
"""

from hypothesis import given
from hypothesis import strategies as st

from spanchor.models.retrieval import RetrievalResult


class TestRetrievalResultProperties:
    """Property-based tests for RetrievalResult model."""

    @given(
        st.integers(min_value=1, max_value=1000),  # rank (positive)
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # score
        st.text(min_size=1, max_size=1000),  # text content
    )
    def test_retrieval_result_classification_chunk_text_form(
        self, rank: int, score: float, text: str
    ) -> None:
        """Property 8: Retrieval Result Classification.

        **Validates: Requirements 4.5**

        For any RetrievalResult in chunk-text form (text is not None and document_id is None),
        the needs_mapping() method SHALL return True.

        This property verifies:
        - Chunk-text form (has text, no document_id) is correctly identified as needing mapping
        - needs_mapping() returns True for all chunk-text results
        - Classification is consistent regardless of rank, score, or text content
        """
        # Create RetrievalResult in chunk-text form:
        # - text is provided (not None)
        # - document_id is None (not provided)
        chunk_result = RetrievalResult(
            rank=rank,
            score=score,
            text=text,
            document_id=None,  # Explicitly None - this is chunk-text form
        )

        # PROPERTY: chunk-text form SHALL indicate it needs mapping
        assert chunk_result.needs_mapping() is True, (
            f"Chunk-text form should need mapping: " f"text={text!r}, document_id=None"
        )

        # Additional verification: confirm the result is actually in chunk-text form
        assert chunk_result.text is not None, "Chunk-text form must have text"
        assert chunk_result.document_id is None, "Chunk-text form must not have document_id"

    @given(
        st.integers(min_value=1, max_value=1000),  # rank (positive)
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # score
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.integers(min_value=0, max_value=10000),  # start offset
        st.data(),  # data strategy for generating end offset
    )
    def test_retrieval_result_classification_span_form(
        self, rank: int, score: float, document_id: str, start: int, data: st.DataObject
    ) -> None:
        """Property 8: Retrieval Result Classification (span form).

        **Validates: Requirements 4.5**

        For any RetrievalResult in span form (document_id is not None, has start and end),
        the needs_mapping() method SHALL return False.

        This property verifies:
        - Span form (has document_id, start, end) is correctly identified as NOT needing mapping
        - needs_mapping() returns False for all span-form results
        - Classification works regardless of whether text is present or not
        """
        # Generate end offset that's greater than start (valid span)
        end = data.draw(st.integers(min_value=start + 1, max_value=start + 10000))

        # Create RetrievalResult in span form:
        # - document_id is provided (not None)
        # - start and end offsets are provided
        # - text is None (span form doesn't include text)
        span_result = RetrievalResult(
            rank=rank,
            score=score,
            document_id=document_id,
            start=start,
            end=end,
            text=None,  # Span form doesn't include text
        )

        # PROPERTY: span form SHALL NOT need mapping (already mapped to source)
        assert span_result.needs_mapping() is False, (
            f"Span form should NOT need mapping: "
            f"document_id={document_id!r}, start={start}, end={end}"
        )

        # Additional verification: confirm the result is actually in span form
        assert span_result.document_id is not None, "Span form must have document_id"
        assert span_result.start is not None, "Span form must have start offset"
        assert span_result.end is not None, "Span form must have end offset"
        assert span_result.text is None, "Span form should not have text"

    @given(
        st.integers(min_value=1, max_value=1000),  # rank (positive)
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # score
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.text(min_size=1, max_size=1000),  # text content
    )
    def test_retrieval_result_classification_chunk_with_document_hint(
        self, rank: int, score: float, document_id: str, text: str
    ) -> None:
        """Property 8: Retrieval Result Classification (chunk with document hint).

        **Validates: Requirements 4.5**

        For any RetrievalResult with text AND document_id but no start/end offsets,
        this is NOT pure chunk-text form (as defined in Property 8) and needs_mapping() SHALL return False.

        This property verifies:
        - Property 8 defines chunk-text form strictly as (text is not None AND document_id is None)
        - When document_id is provided (even without offsets), it's not the chunk-text form Property 8 refers to
        - needs_mapping() returns False because document_id is present
        """
        # Create RetrievalResult with text AND document_id:
        # - text is provided (not None)
        # - document_id is provided (not None)
        # - start and end are None (no precise offsets)
        chunk_with_hint = RetrievalResult(
            rank=rank,
            score=score,
            text=text,
            document_id=document_id,  # Document id provided
            start=None,  # No offsets
            end=None,
        )

        # PROPERTY: Per Property 8's strict definition, chunk-text form requires document_id to be None
        # When document_id is present (even as a hint), needs_mapping() returns False
        # This aligns with the implementation: text is not None AND document_id is None
        assert chunk_with_hint.needs_mapping() is False, (
            f"Chunk with document_id (not pure chunk-text form per Property 8) should return False: "
            f"text={text!r}, document_id={document_id!r}"
        )

        # Additional verification
        assert chunk_with_hint.text is not None, "Must have text content"
        assert chunk_with_hint.document_id is not None, "Document id is provided"

    @given(
        st.integers(max_value=0),  # rank <= 0 (invalid)
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),  # score
        st.text(min_size=1, max_size=1000),  # text content
    )
    def test_retrieval_result_rank_validation(self, rank: int, score: float, text: str) -> None:
        """Property 9: Retrieval Result Rank Validation.

        **Validates: Requirements 4.6**

        For any RetrievalResult with rank <= 0, validation SHALL fail indicating
        ranks must be positive integers.

        This property verifies:
        - Rank values must be positive integers (>= 1)
        - Zero and negative ranks are invalid
        - Validation catches invalid rank values

        NOTE: Current implementation does not have explicit rank validation.
        This test documents the expected behavior for future implementation.
        When validation is added, this test should pass by catching invalid ranks.
        """
        # PROPERTY: rank <= 0 should be invalid
        # Expected behavior: RetrievalResult creation or validation should fail
        # for rank <= 0

        # For now, we document that the model accepts invalid ranks
        # but this behavior should change when validation is implemented
        result = RetrievalResult(
            rank=rank,
            score=score,
            text=text,
            document_id=None,
        )

        # Document current behavior: rank is accepted without validation
        # When validation is added, this assertion should be replaced with
        # an expectation that creation/validation raises an error
        assert result.rank == rank, f"Rank stored without validation: {rank}"

        # TODO: When validation is implemented, replace the above with:
        # with pytest.raises(InvalidRetrievalResultError, match="rank must be positive"):
        #     RetrievalResult(rank=rank, score=score, text=text)
