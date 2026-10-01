"""Integration tests for framework adapters using real framework objects.

Tests the LangChain and LlamaIndex adapters with actual framework objects
to ensure real-world compatibility beyond mock-based testing.
"""

from __future__ import annotations

import pytest


class TestLangChainRealIntegration:
    """Tests with real LangChain objects."""

    def test_real_langchain_document_conversion(self) -> None:
        """Test with actual LangChain Document objects."""
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError:
            pytest.skip("langchain not installed")

        from spanchor.adapters.langchain import documents_to_retrieval_results

        # Create real LangChain documents
        docs = [
            LCDocument(
                page_content="First document",
                metadata={"relevance_score": 0.95, "source": "doc1"},
            ),
            LCDocument(
                page_content="Second document",
                metadata={"relevance_score": 0.87, "source": "doc2"},
            ),
        ]

        result = documents_to_retrieval_results(docs)

        assert len(result) == 2
        assert result[0].score == 0.95
        assert result[0].document_id == "doc1"
        assert result[0].text == "First document"
        assert result[1].score == 0.87
        assert result[1].document_id == "doc2"

    def test_langchain_custom_metadata_keys(self) -> None:
        """Test LangChain adapter with custom metadata key names."""
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError:
            pytest.skip("langchain not installed")

        from spanchor.adapters.langchain import documents_to_retrieval_results

        docs = [
            LCDocument(
                page_content="Content",
                metadata={"my_score": 0.75, "my_doc_id": "custom_id"},
            ),
        ]

        result = documents_to_retrieval_results(
            docs, score_key="my_score", document_id_key="my_doc_id"
        )

        assert result[0].score == 0.75
        assert result[0].document_id == "custom_id"

    def test_langchain_missing_score_and_id(self) -> None:
        """Test LangChain adapter with missing score and document ID."""
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError:
            pytest.skip("langchain not installed")

        from spanchor.adapters.langchain import documents_to_retrieval_results

        docs = [LCDocument(page_content="Content", metadata={})]

        result = documents_to_retrieval_results(docs)

        assert result[0].score == 0.0
        assert result[0].document_id is None

    def test_langchain_metadata_preservation(self) -> None:
        """Test that all metadata is preserved."""
        try:
            from langchain_core.documents import Document as LCDocument
        except ImportError:
            pytest.skip("langchain not installed")

        from spanchor.adapters.langchain import documents_to_retrieval_results

        metadata = {
            "source": "doc1",
            "page": 5,
            "custom": "value",
            "nested": {"key": "val"},
        }
        docs = [LCDocument(page_content="Content", metadata=metadata)]

        result = documents_to_retrieval_results(docs)

        assert result[0].metadata == metadata


class TestLlamaIndexRealIntegration:
    """Tests with real LlamaIndex objects."""

    def test_real_llamaindex_conversion(self) -> None:
        """Test with actual LlamaIndex NodeWithScore objects."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        # Create real LlamaIndex nodes
        node1 = TextNode(text="First node", metadata={"source": "doc1"})
        node2 = TextNode(text="Second node", metadata={"source": "doc2"})

        nodes = [
            NodeWithScore(node=node1, score=0.95),
            NodeWithScore(node=node2, score=0.87),
        ]

        result = nodes_to_retrieval_results(nodes)

        assert len(result) == 2
        assert result[0].text == "First node"
        assert result[0].score == 0.95
        assert result[0].document_id == "doc1"
        assert result[1].text == "Second node"
        assert result[1].score == 0.87

    def test_llamaindex_get_content_method(self) -> None:
        """Test LlamaIndex adapter using get_content() method."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        node = TextNode(text="Content via text", metadata={"source": "doc1"})
        nodes = [NodeWithScore(node=node, score=0.9)]

        result = nodes_to_retrieval_results(nodes)

        assert result[0].text == "Content via text"

    def test_llamaindex_missing_score(self) -> None:
        """Test LlamaIndex adapter with missing score."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        node = TextNode(text="Content", metadata={"source": "doc1"})
        nodes = [NodeWithScore(node=node, score=None)]

        result = nodes_to_retrieval_results(nodes)

        assert result[0].score == 0.0

    def test_llamaindex_document_id_extraction(self) -> None:
        """Test document ID extraction from source and document_id fields."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        # Test source field
        node1 = TextNode(text="Content", metadata={"source": "from_source"})
        nodes1 = [NodeWithScore(node=node1, score=0.9)]
        result1 = nodes_to_retrieval_results(nodes1)
        assert result1[0].document_id == "from_source"

        # Test document_id field
        node2 = TextNode(text="Content", metadata={"document_id": "from_doc_id"})
        nodes2 = [NodeWithScore(node=node2, score=0.9)]
        result2 = nodes_to_retrieval_results(nodes2)
        assert result2[0].document_id == "from_doc_id"

        # Test source takes precedence
        node3 = TextNode(
            text="Content", metadata={"source": "source_wins", "document_id": "doc_id"}
        )
        nodes3 = [NodeWithScore(node=node3, score=0.9)]
        result3 = nodes_to_retrieval_results(nodes3)
        assert result3[0].document_id == "source_wins"

    def test_llamaindex_metadata_preservation(self) -> None:
        """Test that LlamaIndex metadata is preserved."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        metadata = {"source": "doc1", "page": 5, "custom": "value"}
        node = TextNode(text="Content", metadata=metadata)
        nodes = [NodeWithScore(node=node, score=0.9)]

        result = nodes_to_retrieval_results(nodes)

        assert result[0].metadata == metadata

    def test_llamaindex_ranking(self) -> None:
        """Test that ranks are assigned correctly."""
        try:
            from llama_index.core.schema import NodeWithScore, TextNode
        except ImportError:
            pytest.skip("llama-index not installed")

        from spanchor.adapters.llamaindex import nodes_to_retrieval_results

        nodes = [
            NodeWithScore(node=TextNode(text=f"Text {i}"), score=0.9 - i * 0.1) for i in range(5)
        ]

        result = nodes_to_retrieval_results(nodes)

        for i, r in enumerate(result, start=1):
            assert r.rank == i
