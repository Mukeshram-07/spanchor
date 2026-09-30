"""Query model with associated gold anchors.

A Query represents a question with zero or more gold anchor references that
point to relevant evidence spans in source documents.
"""

from dataclasses import dataclass

from spanchor.models.anchor import Anchor


@dataclass(frozen=True, slots=True)
class Query:
    """Query with associated gold anchors.

    A Query contains a question and the set of gold-standard anchor references
    that point to relevant evidence in the source documents. Queries can have
    zero, one, or multiple anchors.

    Attributes:
        query_id: Unique identifier for this query
        question: The question text
        anchors: Tuple of gold anchor references (immutable, hashable)
        schema_version: Schema version for forward compatibility
    """

    query_id: str
    question: str
    anchors: tuple[Anchor, ...]
    schema_version: str = "0.1.0"
