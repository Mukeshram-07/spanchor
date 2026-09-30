"""Corpus validation: check all anchors in a gold set against a document corpus.

This module provides check_corpus(), which validates every anchor's:
1. Document existence (DocumentNotFoundError)
2. Document hash integrity (HashMismatchError)
3. Offset bounds (AnchorResolutionError – out of bounds)
4. Text match at offset (AnchorResolutionError – hash mismatch)

All issues are collected (no early exit) and returned as a list of CorpusIssue
objects so the CLI can report a complete picture in one pass.
"""

from __future__ import annotations

from dataclasses import dataclass

from spanchor.errors import DocumentNotFoundError, SpanchorError
from spanchor.models.document import Document
from spanchor.models.query import Query


@dataclass(frozen=True, slots=True)
class CorpusIssue:
    """A single validation issue found during corpus checking.

    Attributes:
        query_id: ID of the query whose anchor failed validation.
        document_id: ID of the document the anchor references.
        message: Human-readable description of what went wrong.
    """

    query_id: str
    document_id: str
    message: str


def check_corpus(
    documents: dict[str, Document],
    queries: list[Query],
) -> list[CorpusIssue]:
    """Validate every anchor in the gold set against the document corpus.

    Iterates over all queries and all anchors within each query, performing
    three validation checks per anchor:

    1. Document existence – the anchor's document_id must be in *documents*.
    2. Document hash / offset bounds / text match – delegated to
       ``Anchor.validate(doc)`` which raises typed errors on failure.

    All failures are collected; the function never raises; it returns the full
    list so callers can decide how to handle partial failures.

    Args:
        documents: Mapping of ``document_id`` → canonical :class:`Document`.
        queries: Gold-set queries whose anchors will be validated.

    Returns:
        A (possibly empty) list of :class:`CorpusIssue` objects.
        An empty list means the corpus is healthy.

    Example:
        >>> from spanchor.models.document import Document
        >>> from spanchor.models.anchor import Anchor
        >>> from spanchor.models.query import Query
        >>> from spanchor.canonical.normalize import compute_hash
        >>> doc = Document.from_text("doc1", "Hello world")
        >>> anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        >>> query = Query("q1", "What?", (anchor,))
        >>> issues = check_corpus({"doc1": doc}, [query])
        >>> issues
        []
    """
    issues: list[CorpusIssue] = []

    for query in queries:
        for anchor in query.anchors:
            doc = documents.get(anchor.document_id)

            if doc is None:
                # Document entirely missing from corpus
                exc = DocumentNotFoundError(
                    document_id=anchor.document_id,
                    query_id=query.query_id,
                )
                issues.append(
                    CorpusIssue(
                        query_id=query.query_id,
                        document_id=anchor.document_id,
                        message=str(exc),
                    )
                )
                continue  # can't validate further without the document

            try:
                anchor.validate(doc)
            except SpanchorError as exc:
                issues.append(
                    CorpusIssue(
                        query_id=query.query_id,
                        document_id=anchor.document_id,
                        message=str(exc),
                    )
                )

    return issues
