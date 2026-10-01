"""LlamaIndex integration adapter.

Convert LlamaIndex NodeWithScore objects into SPANCHOR RetrievalResult format.

Optional dependency: llama-index>=0.9.0

This adapter is only available when llama-index is installed:
    pip install spanchor[llamaindex]

Usage::

    from llama_index.core.retrievers import BaseRetriever
    from spanchor.adapters.llamaindex import nodes_to_retrieval_results

    # Your LlamaIndex retriever
    retriever = ...  # Your retriever instance
    nodes = retriever.retrieve("query")

    # Convert to SPANCHOR format
    spanchor_results = nodes_to_retrieval_results(nodes)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from llama_index.schema import NodeWithScore


def nodes_to_retrieval_results(
    nodes: list[NodeWithScore],
    score_key: str = "score",
) -> list[Any]:
    """Convert LlamaIndex NodeWithScore objects to SPANCHOR RetrievalResults.

    Args:
        nodes: List of NodeWithScore objects (from retriever.retrieve())
        score_key: Attribute name for score (default: 'score')

    Returns:
        List of RetrievalResult objects ready for SPANCHOR evaluation.

    Raises:
        ImportError: If llama-index is not installed.
        ValueError: If Node structure is unexpected.

    Examples:
        >>> from llama_index.schema import NodeWithScore, TextNode
        >>> node = TextNode(text="Some retrieved text")
        >>> node_with_score = NodeWithScore(node=node, score=0.95)
        >>> from spanchor.adapters.llamaindex import nodes_to_retrieval_results
        >>> results = nodes_to_retrieval_results([node_with_score])
        >>> results[0].text
        'Some retrieved text'
        >>> results[0].score
        0.95
    """
    try:
        from llama_index.schema import (
            NodeWithScore,  # type: ignore[import-not-found,import-untyped]  # noqa: F811
        )
    except ImportError as e:
        raise ImportError(
            "llama-index is required for LlamaIndex adapter. "
            "Install with: pip install spanchor[llamaindex]"
        ) from e

    from spanchor.models.retrieval import RetrievalResult

    spanchor_results = []

    for rank, node_with_score in enumerate(nodes, start=1):
        if not isinstance(node_with_score, NodeWithScore):
            raise ValueError(
                f"Expected LlamaIndex NodeWithScore, got {type(node_with_score).__name__}. "
                "Ensure you're passing a list of llama_index.schema.NodeWithScore objects."
            )

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
                f"Cannot extract text from LlamaIndex Node of type {type(node).__name__}. "
                "Ensure the node has a 'text' attribute or 'get_content()' method."
            )

        # Extract document ID from metadata
        document_id: str | None = None
        if hasattr(node, "metadata") and isinstance(node.metadata, dict):
            document_id = node.metadata.get("source") or node.metadata.get("document_id")

        # Extract metadata (if available)
        metadata = {}
        if hasattr(node, "metadata") and isinstance(node.metadata, dict):
            metadata = node.metadata.copy()

        # Create RetrievalResult in chunk-text form
        result = RetrievalResult(
            rank=rank,
            score=float(score),
            document_id=document_id,
            text=text,
            metadata=metadata,
        )
        spanchor_results.append(result)

    return spanchor_results
