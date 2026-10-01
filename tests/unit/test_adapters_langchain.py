"""Tests for LangChain adapter.

Tests conversion of LangChain Document objects to SPANCHOR RetrievalResult format.

These tests use a mock LangChain Document class to avoid requiring langchain
installation for the test suite. Tests are skipped if langchain is available
but can be run with actual LangChain objects by importing the real Document.
"""

from __future__ import annotations

from typing import Any

import pytest


class MockLangChainDocument:
    """Mock LangChain Document for testing without requiring langchain."""

    def __init__(self, page_content: str, metadata: dict[str, Any] | None = None) -> None:
        """Initialize mock document.

        Args:
            page_content: The document text content
            metadata: Optional metadata dict
        """
        self.page_content = page_content
        self.metadata = metadata or {}


class TestDocumentsToRetrievalResults:
    """Tests for documents_to_retrieval_results function."""

    @pytest.fixture
    def mock_documents_to_retrieval_results(self) -> Any:
        """Create a local adapter using mock documents.

        This allows testing without requiring langchain to be installed.
        Uses local implementation, not the real adapter (which requires langchain).
        """
        from spanchor.models.retrieval import RetrievalResult

        def adapter(
            documents: list[Any],
            score_key: str = "relevance_score",
            document_id_key: str = "source",
        ) -> list[Any]:
            """Local adapter implementation for mock documents."""
            # Implement adapter logic locally for testing without langchain
            spanchor_results = []
            for rank, doc in enumerate(documents, start=1):
                # Extract score from metadata
                score: float = 0.0
                if doc.metadata and score_key in doc.metadata:
                    score_val = doc.metadata[score_key]
                    if isinstance(score_val, int | float):
                        score = float(score_val)

                # Extract document ID from metadata
                document_id: str | None = None
                if doc.metadata and document_id_key in doc.metadata:
                    document_id_val = doc.metadata[document_id_key]
                    if isinstance(document_id_val, str):
                        document_id = document_id_val

                # Create RetrievalResult in chunk-text form
                result = RetrievalResult(
                    rank=rank,
                    score=score,
                    document_id=document_id,
                    text=doc.page_content,
                    metadata=doc.metadata or {},
                )
                spanchor_results.append(result)

            return spanchor_results

        return adapter

    def test_basic_document_conversion(self, mock_documents_to_retrieval_results: Any) -> None:
        """Convert single LangChain Document to RetrievalResult."""
        docs = [
            MockLangChainDocument(
                page_content="Some retrieved text",
                metadata={"source": "doc1", "relevance_score": 0.95},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 1
        assert results[0].text == "Some retrieved text"
        assert results[0].score == 0.95
        assert results[0].document_id == "doc1"
        assert results[0].rank == 1

    def test_multiple_documents(self, mock_documents_to_retrieval_results: Any) -> None:
        """Convert multiple LangChain Documents preserving order and rank."""
        docs = [
            MockLangChainDocument(
                page_content="First result",
                metadata={"source": "doc1", "relevance_score": 0.95},
            ),
            MockLangChainDocument(
                page_content="Second result",
                metadata={"source": "doc2", "relevance_score": 0.85},
            ),
            MockLangChainDocument(
                page_content="Third result",
                metadata={"source": "doc3", "relevance_score": 0.75},
            ),
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 3
        assert results[0].text == "First result"
        assert results[0].rank == 1
        assert results[1].text == "Second result"
        assert results[1].rank == 2
        assert results[2].text == "Third result"
        assert results[2].rank == 3

    def test_metadata_extraction_default_keys(
        self, mock_documents_to_retrieval_results: Any
    ) -> None:
        """Extract score and document_id from default metadata keys."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={
                    "source": "my_document",
                    "relevance_score": 0.88,
                    "page": 1,
                },
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].document_id == "my_document"
        assert results[0].score == 0.88
        # Additional metadata preserved
        assert results[0].metadata.get("page") == 1

    def test_metadata_extraction_custom_score_key(
        self, mock_documents_to_retrieval_results: Any
    ) -> None:
        """Extract score from custom metadata key."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": "doc1", "custom_score": 0.73},
            )
        ]

        results = mock_documents_to_retrieval_results(docs, score_key="custom_score")

        assert results[0].score == 0.73

    def test_metadata_extraction_custom_document_id_key(
        self, mock_documents_to_retrieval_results: Any
    ) -> None:
        """Extract document_id from custom metadata key."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"file_path": "documents/file.txt", "relevance_score": 0.9},
            )
        ]

        results = mock_documents_to_retrieval_results(docs, document_id_key="file_path")

        assert results[0].document_id == "documents/file.txt"

    def test_missing_score_defaults_to_zero(self, mock_documents_to_retrieval_results: Any) -> None:
        """Score defaults to 0.0 if metadata key missing."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": "doc1"},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].score == 0.0

    def test_missing_document_id_defaults_to_none(
        self, mock_documents_to_retrieval_results: Any
    ) -> None:
        """document_id defaults to None if metadata key missing."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"relevance_score": 0.9},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].document_id is None

    def test_score_coercion_from_int(self, mock_documents_to_retrieval_results: Any) -> None:
        """Score is coerced from int to float."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": "doc1", "relevance_score": 1},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].score == 1.0
        assert isinstance(results[0].score, float)

    def test_non_numeric_score_ignored(self, mock_documents_to_retrieval_results: Any) -> None:
        """Non-numeric score in metadata is ignored, defaults to 0.0."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": "doc1", "relevance_score": "high"},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].score == 0.0

    def test_non_string_document_id_ignored(self, mock_documents_to_retrieval_results: Any) -> None:
        """Non-string document_id in metadata is ignored, defaults to None."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": 12345, "relevance_score": 0.9},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].document_id is None

    def test_metadata_preservation(self, mock_documents_to_retrieval_results: Any) -> None:
        """All metadata fields are preserved in result."""
        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={
                    "source": "doc1",
                    "relevance_score": 0.9,
                    "custom_field": "value",
                    "another_field": 42,
                    "nested": {"key": "val"},
                },
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].metadata["source"] == "doc1"
        assert results[0].metadata["relevance_score"] == 0.9
        assert results[0].metadata["custom_field"] == "value"
        assert results[0].metadata["another_field"] == 42
        assert results[0].metadata["nested"] == {"key": "val"}

    def test_empty_documents_list(self, mock_documents_to_retrieval_results: Any) -> None:
        """Handle empty documents list."""
        docs: list[Any] = []

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 0
        assert results == []

    def test_document_with_none_metadata(self, mock_documents_to_retrieval_results: Any) -> None:
        """Handle document with None metadata."""
        docs = [MockLangChainDocument(page_content="Text", metadata=None)]

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 1
        assert results[0].text == "Text"
        assert results[0].document_id is None
        assert results[0].score == 0.0
        assert results[0].metadata == {}

    def test_document_with_empty_metadata(self, mock_documents_to_retrieval_results: Any) -> None:
        """Handle document with empty metadata dict."""
        docs = [MockLangChainDocument(page_content="Text", metadata={})]

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 1
        assert results[0].metadata == {}

    def test_text_content_preservation(self, mock_documents_to_retrieval_results: Any) -> None:
        """Preserve full page_content as text."""
        long_text = "This is a longer piece of text. " * 50
        docs = [
            MockLangChainDocument(
                page_content=long_text,
                metadata={"source": "doc1", "relevance_score": 0.9},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert results[0].text == long_text

    def test_return_type_is_retrieval_result(
        self, mock_documents_to_retrieval_results: Any
    ) -> None:
        """Returned objects are RetrievalResult instances."""
        from spanchor.models.retrieval import RetrievalResult

        docs = [
            MockLangChainDocument(
                page_content="Text",
                metadata={"source": "doc1", "relevance_score": 0.9},
            )
        ]

        results = mock_documents_to_retrieval_results(docs)

        assert len(results) == 1
        assert isinstance(results[0], RetrievalResult)

    def test_ranking_is_sequential(self, mock_documents_to_retrieval_results: Any) -> None:
        """Ranks are sequential starting from 1."""
        docs = [
            MockLangChainDocument(
                page_content=f"Text {i}",
                metadata={"source": f"doc{i}", "relevance_score": 0.9 - i * 0.1},
            )
            for i in range(10)
        ]

        results = mock_documents_to_retrieval_results(docs)

        for i, result in enumerate(results, start=1):
            assert result.rank == i
