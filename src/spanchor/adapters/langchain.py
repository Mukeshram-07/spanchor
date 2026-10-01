"""LangChain integration adapter.

Convert LangChain retrieved Documents into SPANCHOR RetrievalResult format.

Optional dependency: langchain>=0.1.0

This adapter is only available when langchain is installed:
    pip install spanchor[langchain]

Usage::

    from langchain_community.retrievers import BM25Retriever
    from spanchor.adapters.langchain import documents_to_retrieval_results

    # Your LangChain retriever
    retriever = BM25Retriever.from_texts([...])
    docs = retriever.invoke("query")

    # Convert to SPANCHOR format
    spanchor_results = documents_to_retrieval_results(docs)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langchain_core.documents import Document


def documents_to_retrieval_results(
    documents: list[Document],
    score_key: str = "relevance_score",
    document_id_key: str = "source",
) -> list[Any]:
    """Convert LangChain Documents to SPANCHOR RetrievalResults.

    Args:
        documents: List of LangChain Document objects (from retriever.invoke())
        score_key: Metadata key for retrieval score (default: 'relevance_score')
        document_id_key: Metadata key for document identifier (default: 'source')

    Returns:
        List of RetrievalResult objects ready for SPANCHOR evaluation.

    Raises:
        ImportError: If langchain is not installed.
        ValueError: If Document structure is unexpected.

    Examples:
        >>> from langchain_core.documents import Document
        >>> docs = [
        ...     Document(
        ...         page_content="Some retrieved text",
        ...         metadata={"source": "doc1", "relevance_score": 0.95}
        ...     )
        ... ]
        >>> from spanchor.adapters.langchain import documents_to_retrieval_results
        >>> results = documents_to_retrieval_results(docs)
        >>> results[0].text
        'Some retrieved text'
        >>> results[0].document_id
        'doc1'
    """
    try:
        from langchain_core.documents import (
            Document,  # type: ignore[import-not-found,import-untyped]  # noqa: F811
        )
    except ImportError as e:
        raise ImportError(
            "langchain is required for LangChain adapter. "
            "Install with: pip install spanchor[langchain]"
        ) from e

    from spanchor.models.retrieval import RetrievalResult

    spanchor_results = []

    for rank, doc in enumerate(documents, start=1):
        if not isinstance(doc, Document):
            raise ValueError(
                f"Expected LangChain Document, got {type(doc).__name__}. "
                "Ensure you're passing a list of langchain_core.documents.Document objects."
            )

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
        # (LangChain documents typically provide text, not offsets)
        result = RetrievalResult(
            rank=rank,
            score=score,
            document_id=document_id,
            text=doc.page_content,
            metadata=doc.metadata or {},
        )
        spanchor_results.append(result)

    return spanchor_results
