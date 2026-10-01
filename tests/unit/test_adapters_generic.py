"""Tests for generic adapter utilities."""

import pytest

from spanchor.adapters.generic import dict_to_retrieval_result, dicts_to_retrieval_results
from spanchor.models.retrieval import RetrievalResult


class TestDictToRetrievalResult:
    """Tests for dict_to_retrieval_result function."""

    def test_basic_text_form(self):
        """Convert dict with text field."""
        result = dict_to_retrieval_result(
            {
                "text": "Some retrieved text",
                "score": 0.95,
            }
        )
        assert result.text == "Some retrieved text"
        assert result.score == 0.95
        assert result.rank == 1  # default
        assert result.document_id is None

    def test_rank_override(self):
        """Rank parameter overrides data."""
        result = dict_to_retrieval_result(
            {"text": "Text"},
            rank=5,
        )
        assert result.rank == 5

    def test_score_override(self):
        """Score parameter overrides data."""
        result = dict_to_retrieval_result(
            {"text": "Text", "score": 0.5},
            score=0.9,
        )
        assert result.score == 0.9

    def test_alternate_text_keys(self):
        """Support multiple naming conventions for text."""
        for text_key in ["text", "chunk", "content", "body"]:
            result = dict_to_retrieval_result({text_key: "Chunk text"})
            assert result.text == "Chunk text"

    def test_alternate_score_keys(self):
        """Support multiple naming conventions for score."""
        test_cases = [
            ("score", 0.8),
            ("relevance_score", 0.75),
            ("similarity", 0.70),
            ("confidence", 0.65),
        ]
        for score_key, score_val in test_cases:
            result = dict_to_retrieval_result(
                {
                    "text": "Text",
                    score_key: score_val,
                }
            )
            assert result.score == score_val

    def test_alternate_rank_keys(self):
        """Support multiple naming conventions for rank."""
        test_cases = [
            ("rank", 3),
            ("position", 2),
            ("index", 1),
        ]
        for rank_key, rank_val in test_cases:
            result = dict_to_retrieval_result(
                {
                    "text": "Text",
                    rank_key: rank_val,
                }
            )
            assert result.rank == rank_val

    def test_alternate_document_id_keys(self):
        """Support multiple naming conventions for document_id."""
        test_cases = [
            ("document_id", "doc1"),
            ("doc_id", "doc2"),
            ("source", "doc3"),
            ("document", "doc4"),
        ]
        for doc_key, doc_val in test_cases:
            result = dict_to_retrieval_result(
                {
                    "text": "Text",
                    doc_key: doc_val,
                }
            )
            assert result.document_id == doc_val

    def test_span_form(self):
        """Convert dict with span offsets (document_id, start, end)."""
        result = dict_to_retrieval_result(
            {
                "document_id": "doc1",
                "start": 100,
                "end": 200,
                "score": 0.9,
            },
            rank=1,
        )
        assert result.document_id == "doc1"
        assert result.start == 100
        assert result.end == 200
        assert result.text is None
        assert isinstance(result, RetrievalResult)

    def test_metadata_preserved(self):
        """Metadata fields (not recognized) are preserved."""
        result = dict_to_retrieval_result(
            {
                "text": "Text",
                "custom_field": "value",
                "another_metadata": 123,
            }
        )
        assert result.metadata == {
            "custom_field": "value",
            "another_metadata": 123,
        }

    def test_missing_text_and_no_span_raises(self):
        """Raise error if neither text nor span info provided."""
        with pytest.raises(ValueError, match="requires either 'text' or"):
            dict_to_retrieval_result(
                {
                    "score": 0.9,
                }
            )

    def test_missing_text_with_incomplete_span_raises(self):
        """Raise error if span info is incomplete."""
        with pytest.raises(ValueError, match="requires either 'text' or"):
            dict_to_retrieval_result(
                {
                    "document_id": "doc1",
                    "start": 100,
                    # missing end
                }
            )

    def test_empty_text_field_treated_as_none(self):
        """Empty string text is treated as None."""
        with pytest.raises(ValueError):
            dict_to_retrieval_result({"text": ""})

    def test_default_rank_one(self):
        """Default rank is 1 if not specified."""
        result = dict_to_retrieval_result({"text": "Text"})
        assert result.rank == 1

    def test_default_score_zero(self):
        """Default score is 0.0 if not specified."""
        result = dict_to_retrieval_result({"text": "Text"})
        assert result.score == 0.0


class TestDictsToRetrievalResults:
    """Tests for dicts_to_retrieval_results function."""

    def test_auto_ranking(self):
        """Results are auto-ranked starting from 1."""
        results = dicts_to_retrieval_results(
            [
                {"text": "First"},
                {"text": "Second"},
                {"text": "Third"},
            ]
        )
        assert len(results) == 3
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[2].rank == 3

    def test_preserves_scores(self):
        """Scores from dict are preserved."""
        results = dicts_to_retrieval_results(
            [
                {"text": "First", "score": 0.9},
                {"text": "Second", "score": 0.7},
            ]
        )
        assert results[0].score == 0.9
        assert results[1].score == 0.7

    def test_empty_list(self):
        """Empty list returns empty list."""
        results = dicts_to_retrieval_results([])
        assert results == []

    def test_converts_all(self):
        """All dicts are converted to RetrievalResult."""
        results = dicts_to_retrieval_results([{"text": f"Result {i}"} for i in range(5)])
        assert len(results) == 5
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert [r.rank for r in results] == [1, 2, 3, 4, 5]

    def test_preserves_metadata(self):
        """Metadata is preserved for each result."""
        results = dicts_to_retrieval_results(
            [
                {"text": "Text", "custom": "value1"},
                {"text": "Text", "custom": "value2"},
            ]
        )
        assert results[0].metadata["custom"] == "value1"
        assert results[1].metadata["custom"] == "value2"
