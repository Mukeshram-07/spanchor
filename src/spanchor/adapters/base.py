"""Retriever protocol for integrating custom retrievers with spanchor.

Defines :class:`RetrieverProtocol`, a minimal structural protocol that any
retriever must satisfy to work with spanchor's evaluation pipeline.  It is
intentionally framework-agnostic and has no runtime dependencies beyond the
Python standard library.

Requirements: 27.1, 27.2, 27.3, 27.4

Usage example::

    from spanchor.adapters.base import RetrieverProtocol
    from spanchor.models.retrieval import RetrievalResult


    class MyRetriever:
        \"\"\"Custom retriever that satisfies RetrieverProtocol.\"\"\"

        def retrieve(self, query: str) -> list[RetrievalResult]:
            # ... your retrieval logic here ...
            return [
                RetrievalResult(
                    rank=1,
                    score=0.95,
                    document_id="doc1",
                    start=100,
                    end=250,
                )
            ]


    # Type-check at call sites (static duck typing):
    def run_evaluation(retriever: RetrieverProtocol, queries: list[str]) -> None:
        for query in queries:
            results = retriever.retrieve(query)
            ...
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from spanchor.models.retrieval import RetrievalResult


@runtime_checkable
class RetrieverProtocol(Protocol):
    """Minimal protocol for integrating a custom retriever with spanchor.

    Any class that implements a ``retrieve`` method with the correct signature
    satisfies this protocol automatically via structural subtyping (duck typing).
    No inheritance or registration is required.

    The protocol is marked ``@runtime_checkable`` so you can use
    ``isinstance(obj, RetrieverProtocol)`` checks at runtime if needed.

    Requirements:
        - 27.1: Defines a RetrieverProtocol with a retrieve method.
        - 27.2: retrieve accepts a query string and returns a list of
          RetrievalResult objects.
        - 27.3: Protocol is documented with usage examples.
        - 27.4: Protocol is minimal and requires no framework dependencies.

    Example implementation::

        class BM25Retriever:
            def retrieve(self, query: str) -> list[RetrievalResult]:
                # BM25 search ...
                return [RetrievalResult(rank=1, score=0.8, text="...")]

        class DenseRetriever:
            def retrieve(self, query: str) -> list[RetrievalResult]:
                # Dense embedding search ...
                return [RetrievalResult(rank=1, score=0.95, document_id="d1",
                                        start=0, end=100)]
    """

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """Retrieve relevant results for a query string.

        Args:
            query: The natural-language query to retrieve results for.

        Returns:
            A list of :class:`~spanchor.models.retrieval.RetrievalResult`
            objects, each representing one retrieved item.  Results may be in
            span form (``document_id``, ``start``, ``end``) or chunk-text form
            (``text``).  Rank values should reflect the retriever's ordering
            (1 = most relevant).

            An empty list is valid and means the retriever found nothing.
        """
        ...
