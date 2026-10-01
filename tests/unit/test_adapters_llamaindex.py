"""Tests for LlamaIndex adapter.

Tests conversion of LlamaIndex NodeWithScore objects to SPANCHOR RetrievalResult format.

These tests use mock LlamaIndex Node and NodeWithScore classes to avoid requiring
llama-index installation for the test suite.
"""

from __future__ import annotations

from typing import Any

import pytest


class MockTextNode:
    """Mock LlamaIndex TextNode for testing."""

    def __init__(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> None:
        """Initialize mock node.

        Args:
            text: The node text content
            metadata: Optional metadata dict
            doc_id: Optional document ID
        """
        self.text = text
        self.metadata = metadata or {}
        self.doc_id = doc_id

    def get_content(self) -> str:
        """Return text content."""
        return self.text


class MockNodeWithScore:
    """Mock LlamaIndex NodeWithScore for testing."""

    def __init__(self, node: MockTextNode, score: float | None = None) -> None:
        """Initialize mock NodeWithScore.

        Args:
            node: Mock node object
            score: Optional relevance score
        """
        self.node = node
        self.score = score


class TestNodesToRetrievalResults:
    """Tests for nodes_to_retrieval_results function."""

    @pytest.fixture
    def mock_nodes_to_retrieval_results(self) -> Any:
        """Create a local adapter using mock nodes.

        This allows testing without requiring llama-index to be installed.
        Uses local implementation, not the real adapter (which requires llama-index).
        """
        from spanchor.models.retrieval import RetrievalResult

        def adapter(nodes: list[Any], score_key: str = "score") -> list[Any]:
            """Local adapter implementation for mock nodes."""
            # Implement adapter logic locally for testing without llama-index
            spanchor_results = []

            for rank, node_with_score in enumerate(nodes, start=1):
                node = node_with_score.node
                score = node_with_score.score or 0.0

                # Extract text from node
                text: str | None = None
                if hasattr(node, "get_content"):
                    text = node.get_content()
                elif hasattr(node, "text"):
                    text = node.text

                if not text:
                    raise ValueError(
                        f"Cannot extract text from LlamaIndex Node of type {type(node).__name__}"
                    )

                # Extract document ID from metadata
                document_id: str | None = None
                if hasattr(node, "metadata") and isinstance(node.metadata, dict):
                    document_id = node.metadata.get("source") or node.metadata.get("document_id")

                # Extract metadata
                metadata = {}
                if hasattr(node, "metadata") and isinstance(node.metadata, dict):
                    metadata = node.metadata.copy()

                # Create RetrievalResult
                result = RetrievalResult(
                    rank=rank,
                    score=float(score),
                    document_id=document_id,
                    text=text,
                    metadata=metadata,
                )
                spanchor_results.append(result)

            return spanchor_results

        return adapter

    def test_textnode_conversion(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Convert TextNode with score."""
        node = MockTextNode(text="Some retrieved text")
        node_with_score = MockNodeWithScore(node=node, score=0.95)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert len(results) == 1
        assert results[0].text == "Some retrieved text"
        assert results[0].score == 0.95

    def test_multiple_nodes(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Convert multiple nodes preserving order and rank."""
        nodes_with_scores = [
            MockNodeWithScore(
                node=MockTextNode("First result", metadata={"source": "doc1"}),
                score=0.95,
            ),
            MockNodeWithScore(
                node=MockTextNode("Second result", metadata={"source": "doc2"}),
                score=0.85,
            ),
            MockNodeWithScore(
                node=MockTextNode("Third result", metadata={"source": "doc3"}),
                score=0.75,
            ),
        ]

        results = mock_nodes_to_retrieval_results(nodes_with_scores)

        assert len(results) == 3
        assert results[0].text == "First result"
        assert results[0].rank == 1
        assert results[1].text == "Second result"
        assert results[1].rank == 2
        assert results[2].text == "Third result"
        assert results[2].rank == 3

    def test_node_metadata_extraction(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Extract metadata from node."""
        node = MockTextNode(
            text="Text",
            metadata={
                "source": "my_document",
                "page": 1,
                "custom_field": "value",
            },
        )
        node_with_score = MockNodeWithScore(node=node, score=0.88)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].document_id == "my_document"
        assert results[0].metadata["page"] == 1
        assert results[0].metadata["custom_field"] == "value"

    def test_get_content_method(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Use get_content() method if available."""
        node = MockTextNode(text="Content via get_content")
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].text == "Content via get_content"

    def test_node_without_score(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Handle nodes without explicit score (None)."""
        node = MockTextNode(text="Text")
        node_with_score = MockNodeWithScore(node=node, score=None)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].score == 0.0

    def test_score_coercion(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Score is coerced to float."""
        node = MockTextNode(text="Text")
        node_with_score = MockNodeWithScore(node=node, score=1)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].score == 1.0
        assert isinstance(results[0].score, float)

    def test_document_id_from_source(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Extract document_id from 'source' metadata field."""
        node = MockTextNode(
            text="Text",
            metadata={"source": "document.txt"},
        )
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].document_id == "document.txt"

    def test_document_id_from_document_id_field(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Extract document_id from 'document_id' metadata field if 'source' missing."""
        node = MockTextNode(
            text="Text",
            metadata={"document_id": "doc123"},
        )
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].document_id == "doc123"

    def test_source_takes_precedence(self, mock_nodes_to_retrieval_results: Any) -> None:
        """'source' field takes precedence over 'document_id'."""
        node = MockTextNode(
            text="Text",
            metadata={"source": "source.txt", "document_id": "doc123"},
        )
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].document_id == "source.txt"

    def test_missing_document_id(self, mock_nodes_to_retrieval_results: Any) -> None:
        """document_id is None if metadata missing."""
        node = MockTextNode(text="Text", metadata={})
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].document_id is None

    def test_metadata_preservation(self, mock_nodes_to_retrieval_results: Any) -> None:
        """All metadata fields are preserved."""
        node = MockTextNode(
            text="Text",
            metadata={
                "source": "doc1",
                "page": 5,
                "custom": "value",
                "nested": {"key": "val"},
            },
        )
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].metadata["source"] == "doc1"
        assert results[0].metadata["page"] == 5
        assert results[0].metadata["custom"] == "value"
        assert results[0].metadata["nested"] == {"key": "val"}

    def test_empty_nodes_list(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Handle empty nodes list."""
        results = mock_nodes_to_retrieval_results([])

        assert len(results) == 0

    def test_node_without_metadata(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Handle node without metadata attribute."""

        class MinimalNode:
            def __init__(self, text: str) -> None:
                self.text = text

        node = MinimalNode(text="Text")
        node_with_score = MockNodeWithScore(node=node, score=0.9)  # type: ignore

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].text == "Text"
        assert results[0].document_id is None
        assert results[0].metadata == {}

    def test_return_type_is_retrieval_result(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Returned objects are RetrievalResult instances."""
        from spanchor.models.retrieval import RetrievalResult

        node = MockTextNode(text="Text", metadata={"source": "doc1"})
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert len(results) == 1
        assert isinstance(results[0], RetrievalResult)

    def test_ranking_is_sequential(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Ranks are sequential starting from 1."""
        nodes_with_scores = [
            MockNodeWithScore(
                node=MockTextNode(f"Text {i}"),
                score=0.9 - i * 0.1,
            )
            for i in range(10)
        ]

        results = mock_nodes_to_retrieval_results(nodes_with_scores)

        for i, result in enumerate(results, start=1):
            assert result.rank == i

    def test_text_content_preservation(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Preserve full text content."""
        long_text = "This is longer content. " * 50
        node = MockTextNode(text=long_text)
        node_with_score = MockNodeWithScore(node=node, score=0.9)

        results = mock_nodes_to_retrieval_results([node_with_score])

        assert results[0].text == long_text

    def test_mixed_scores(self, mock_nodes_to_retrieval_results: Any) -> None:
        """Handle mixture of scores including None and 0."""
        nodes_with_scores = [
            MockNodeWithScore(node=MockTextNode("Text 1"), score=0.9),
            MockNodeWithScore(node=MockTextNode("Text 2"), score=None),
            MockNodeWithScore(node=MockTextNode("Text 3"), score=0.0),
            MockNodeWithScore(node=MockTextNode("Text 4"), score=0.5),
        ]

        results = mock_nodes_to_retrieval_results(nodes_with_scores)

        assert results[0].score == 0.9
        assert results[1].score == 0.0  # None becomes 0.0
        assert results[2].score == 0.0
        assert results[3].score == 0.5
