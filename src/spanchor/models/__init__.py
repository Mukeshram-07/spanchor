"""Data models for spanchor.

All models use frozen, slotted dataclasses with explicit validators.
Every serialized model includes a schema_version field for forward compatibility.
"""

from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult
from spanchor.models.run import Run

__all__: list[str] = ["Anchor", "Document", "Query", "RetrievalResult", "Run"]
