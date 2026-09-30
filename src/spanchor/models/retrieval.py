"""RetrievalResult model supporting both span and chunk-text forms.

A RetrievalResult can represent retriever output in two forms:
- Span form: with document_id, start, and end offsets (already mapped to source)
- Chunk-text form: with text content that needs mapping to source spans
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """Retrieval result in span or chunk-text form.

    RetrievalResult supports two forms:

    **Span form** (already mapped to source document):
        - document_id: required
        - start: required (inclusive offset)
        - end: required (exclusive offset)
        - text: None

    **Chunk-text form** (needs mapping):
        - text: required
        - document_id: None (or optional hint if provided)
        - start: None
        - end: None

    Both forms include:
        - rank: Positive integer indicating result position
        - score: Numeric relevance score
        - span_type: Type of span (default "text")
        - metadata: Optional additional information
        - schema_version: Schema version for forward compatibility

    Attributes:
        rank: Positive integer rank (1-indexed)
        score: Numeric relevance score
        document_id: Document identifier (required for span form, optional for chunk-text)
        start: Start offset (required for span form, None for chunk-text)
        end: End offset (required for span form, None for chunk-text)
        text: Text content (required for chunk-text form, None for span form)
        span_type: Type of span (default "text")
        metadata: Optional additional metadata
        schema_version: Schema version for forward compatibility
    """

    rank: int
    score: float
    document_id: str | None = None
    start: int | None = None
    end: int | None = None
    text: str | None = None
    span_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "0.1.0"

    def needs_mapping(self) -> bool:
        """Check if this result is in chunk-text form and needs mapping.

        Returns:
            True if this is a chunk-text result (has text but no document_id),
            False if this is already in span form.

        Examples:
            >>> # Span form - already mapped
            >>> span_result = RetrievalResult(
            ...     rank=1, score=0.95,
            ...     document_id="doc1", start=0, end=10
            ... )
            >>> span_result.needs_mapping()
            False

            >>> # Chunk-text form - needs mapping
            >>> chunk_result = RetrievalResult(
            ...     rank=1, score=0.95,
            ...     text="Some chunk text"
            ... )
            >>> chunk_result.needs_mapping()
            True

            >>> # Chunk with document hint - still needs mapping
            >>> chunk_with_hint = RetrievalResult(
            ...     rank=1, score=0.95,
            ...     text="Some chunk text",
            ...     document_id="doc1"
            ... )
            >>> chunk_with_hint.needs_mapping()
            True
        """
        return self.text is not None and self.document_id is None
