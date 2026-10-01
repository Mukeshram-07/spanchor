"""Generic adapters for converting common retrieval result formats to SPANCHOR RetrievalResult.

This module provides utility functions to convert retrieval results from various
sources (dict, dataclasses, etc.) into SPANCHOR's RetrievalResult format.

No mandatory external dependencies. Framework-specific converters (LangChain, LlamaIndex)
are in separate modules.

Usage::

    from spanchor.adapters.generic import dict_to_retrieval_result

    # Convert a dict
    result_dict = {
        "text": "Chunk of retrieved text",
        "score": 0.95,
        "rank": 1,
        "document_id": "doc1"
    }

    spanchor_result = dict_to_retrieval_result(result_dict)
"""

from __future__ import annotations

from typing import Any

from spanchor.models.retrieval import RetrievalResult


def dict_to_retrieval_result(
    data: dict[str, Any],
    rank: int | None = None,
    score: float | None = None,
) -> RetrievalResult:
    """Convert a dictionary to a RetrievalResult.

    Supports flexible input with various naming conventions for common fields.

    Args:
        data: Dictionary containing retrieval result fields. Supported keys:
            - Text: 'text', 'chunk', 'content', 'body'
            - Score: 'score', 'relevance_score', 'similarity', 'confidence'
            - Rank: 'rank', 'position', 'index' (1-indexed)
            - Document ID: 'document_id', 'doc_id', 'source', 'document'
            - Start offset: 'start', 'start_char', 'offset'
            - End offset: 'end', 'end_char'
            - Metadata: any other keys are included as metadata
        rank: Optional override for rank value (takes precedence over data)
        score: Optional override for score value (takes precedence over data)

    Returns:
        RetrievalResult with extracted/converted fields.

    Raises:
        ValueError: If no text is found and no span offsets provided.

    Examples:
        >>> result = dict_to_retrieval_result(
        ...     {
        ...         "text": "Important passage",
        ...         "score": 0.9,
        ...         "rank": 1,
        ...     }
        ... )
        >>> result.rank
        1
        >>> result.text
        'Important passage'
        >>> result.document_id is None
        True

        >>> result = dict_to_retrieval_result(
        ...     {
        ...         "document_id": "doc1",
        ...         "start": 100,
        ...         "end": 200,
        ...         "relevance_score": 0.85,
        ...     },
        ...     rank=1,
        ... )
        >>> result.document_id
        'doc1'
        >>> result.start
        100
    """
    # Extract text (multiple naming conventions)
    text = data.get("text") or data.get("chunk") or data.get("content") or data.get("body")

    # Extract score
    result_score: float
    if score is not None:
        result_score = score
    else:
        result_score = (
            data.get("score")
            or data.get("relevance_score")
            or data.get("similarity")
            or data.get("confidence")
            or 0.0
        )

    # Extract rank
    result_rank: int
    if rank is not None:
        result_rank = rank
    else:
        result_rank = data.get("rank") or data.get("position") or data.get("index") or 1

    # Extract document ID
    document_id: str | None = (
        data.get("document_id") or data.get("doc_id") or data.get("source") or data.get("document")
    )

    # Extract span offsets
    start: int | None = data.get("start") or data.get("start_char") or data.get("offset")
    end: int | None = data.get("end") or data.get("end_char")

    # Validate that we have either text or span information
    if not text and not (document_id and start is not None and end is not None):
        raise ValueError(
            "dict_to_retrieval_result requires either 'text' or "
            "('document_id', 'start', 'end') to be provided"
        )

    # Extract metadata (everything not already processed)
    processed_keys = {
        "text",
        "chunk",
        "content",
        "body",
        "score",
        "relevance_score",
        "similarity",
        "confidence",
        "rank",
        "position",
        "index",
        "document_id",
        "doc_id",
        "source",
        "document",
        "start",
        "start_char",
        "offset",
        "end",
        "end_char",
    }
    metadata = {k: v for k, v in data.items() if k not in processed_keys}

    return RetrievalResult(
        rank=result_rank,
        score=result_score,
        document_id=document_id,
        start=start,
        end=end,
        text=text,
        metadata=metadata,
    )


def dicts_to_retrieval_results(
    results: list[dict[str, Any]],
) -> list[RetrievalResult]:
    """Convert a list of dictionaries to RetrievalResults, auto-ranking them.

    Args:
        results: List of result dictionaries.

    Returns:
        List of RetrievalResult objects with auto-assigned ranks (1, 2, 3, ...).

    Examples:
        >>> results = [
        ...     {"text": "First result", "score": 0.95},
        ...     {"text": "Second result", "score": 0.80},
        ... ]
        >>> spanchor_results = dicts_to_retrieval_results(results)
        >>> len(spanchor_results)
        2
        >>> spanchor_results[0].rank
        1
        >>> spanchor_results[1].rank
        2
    """
    spanchor_results = []
    for idx, result_dict in enumerate(results, start=1):
        # Use provided score if present, else default
        spanchor_result = dict_to_retrieval_result(
            result_dict,
            rank=idx,
        )
        spanchor_results.append(spanchor_result)
    return spanchor_results
