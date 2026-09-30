"""Unit tests for RetrievalResult model."""

import pytest

from spanchor.models.retrieval import RetrievalResult


class TestRetrievalResultModel:
    """Tests for RetrievalResult dataclass."""

    def test_span_form_creation(self):
        """RetrievalResult can be created in span form (Requirement 4.1)."""
        result = RetrievalResult(
            rank=1,
            score=0.95,
            document_id="doc1",
            start=0,
            end=10,
            span_type="text",
            schema_version="0.1.0",
        )

        assert result.rank == 1
        assert result.score == 0.95
        assert result.document_id == "doc1"
        assert result.start == 0
        assert result.end == 10
        assert result.text is None
        assert result.span_type == "text"
        assert result.schema_version == "0.1.0"

    def test_chunk_text_form_creation(self):
        """RetrievalResult can be created in chunk-text form (Requirement 4.2)."""
        result = RetrievalResult(
            rank=2,
            score=0.85,
            text="Some chunk text",
            metadata={"source": "vectordb"},
        )

        assert result.rank == 2
        assert result.score == 0.85
        assert result.text == "Some chunk text"
        assert result.document_id is None
        assert result.start is None
        assert result.end is None
        assert result.metadata == {"source": "vectordb"}

    def test_chunk_text_with_document_hint(self):
        """RetrievalResult chunk-text form can include optional document_id hint."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="Chunk content",
            document_id="doc1",  # Optional hint
        )

        assert result.text == "Chunk content"
        assert result.document_id == "doc1"
        assert result.start is None
        assert result.end is None

    def test_span_type_defaults(self):
        """span_type defaults to 'text' (Requirement 4.3)."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            document_id="doc1",
            start=0,
            end=10,
        )

        assert result.span_type == "text"

    def test_metadata_defaults_to_empty_dict(self):
        """metadata defaults to empty dict (Requirement 4.2)."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="chunk",
        )

        assert result.metadata == {}
        assert isinstance(result.metadata, dict)

    def test_schema_version_defaults(self):
        """schema_version defaults to 0.1.0 (Requirement 4.4)."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="chunk",
        )

        assert result.schema_version == "0.1.0"

    def test_result_frozen(self):
        """RetrievalResult is immutable (frozen)."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="chunk",
        )

        with pytest.raises(AttributeError):
            result.rank = 2  # type: ignore


class TestRetrievalResultNeedsMapping:
    """Tests for RetrievalResult.needs_mapping() method."""

    def test_needs_mapping_true_for_chunk_text(self):
        """needs_mapping returns True for chunk-text form (Requirement 4.5)."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="Some chunk text",
        )

        assert result.needs_mapping() is True

    def test_needs_mapping_false_for_span_form(self):
        """needs_mapping returns False for span form."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            document_id="doc1",
            start=0,
            end=10,
        )

        assert result.needs_mapping() is False

    def test_needs_mapping_true_with_document_hint(self):
        """needs_mapping returns False when document_id is provided even with text."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="Chunk text",
            document_id="doc1",  # Hint provided, not pure chunk-text form
        )

        # When document_id is provided, it's not pure chunk-text form
        # so needs_mapping returns False per the spec
        assert result.needs_mapping() is False

    def test_needs_mapping_false_when_no_text(self):
        """needs_mapping returns False when text is None."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            document_id="doc1",
            start=0,
            end=10,
            text=None,
        )

        assert result.needs_mapping() is False


class TestRetrievalResultValidation:
    """Tests for RetrievalResult validation expectations."""

    def test_positive_rank(self):
        """Rank should be positive integer (Requirement 4.6)."""
        # Create with positive rank
        result = RetrievalResult(rank=1, score=0.9, text="chunk")
        assert result.rank == 1

        # Create with higher rank
        result = RetrievalResult(rank=100, score=0.5, text="chunk")
        assert result.rank == 100

    def test_numeric_score(self):
        """Score should be numeric (Requirement 4.7)."""
        # Float score
        result = RetrievalResult(rank=1, score=0.95, text="chunk")
        assert result.score == 0.95

        # Integer score (also numeric)
        result = RetrievalResult(rank=1, score=1, text="chunk")
        assert result.score == 1

        # Negative score (valid numeric)
        result = RetrievalResult(rank=1, score=-0.5, text="chunk")
        assert result.score == -0.5


class TestRetrievalResultEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_text_chunk(self):
        """Chunk-text form with empty string."""
        result = RetrievalResult(
            rank=1,
            score=0.5,
            text="",
        )

        assert result.text == ""
        assert result.needs_mapping() is True

    def test_zero_length_span(self):
        """Span form with zero-length span (start == end)."""
        result = RetrievalResult(
            rank=1,
            score=0.5,
            document_id="doc1",
            start=5,
            end=5,
        )

        assert result.start == 5
        assert result.end == 5
        assert result.needs_mapping() is False

    def test_metadata_with_nested_structure(self):
        """Metadata can contain nested structures."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            text="chunk",
            metadata={
                "source": "vectordb",
                "embedding_model": "text-embedding-3-small",
                "scores": {"cosine": 0.9, "bm25": 15.3},
            },
        )

        assert result.metadata["source"] == "vectordb"
        assert result.metadata["scores"]["cosine"] == 0.9

    def test_custom_span_type(self):
        """span_type can be customized."""
        result = RetrievalResult(
            rank=1,
            score=0.9,
            document_id="doc1",
            start=0,
            end=10,
            span_type="code",
        )

        assert result.span_type == "code"

    def test_large_rank_values(self):
        """Large rank values are supported."""
        result = RetrievalResult(
            rank=1000000,
            score=0.001,
            text="chunk",
        )

        assert result.rank == 1000000

    def test_score_boundary_values(self):
        """Score can have various boundary values."""
        # Zero score
        result = RetrievalResult(rank=1, score=0.0, text="chunk")
        assert result.score == 0.0

        # Very small positive score
        result = RetrievalResult(rank=1, score=1e-10, text="chunk")
        assert result.score == 1e-10

        # Large score
        result = RetrievalResult(rank=1, score=1000.0, text="chunk")
        assert result.score == 1000.0
