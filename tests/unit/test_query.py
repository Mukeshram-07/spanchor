"""Unit tests for Query model."""

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query


class TestQueryModel:
    """Tests for Query dataclass."""

    def test_query_creation_with_anchors(self):
        """Query can be created with multiple anchors."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("hello"))
        anchor2 = Anchor("doc1", 6, 11, compute_hash("world"))

        query = Query(
            query_id="q1",
            question="What is hello world?",
            anchors=(anchor1, anchor2),
            schema_version="0.1.0",
        )

        assert query.query_id == "q1"
        assert query.question == "What is hello world?"
        assert len(query.anchors) == 2
        assert query.anchors[0] == anchor1
        assert query.anchors[1] == anchor2
        assert query.schema_version == "0.1.0"

    def test_query_with_single_anchor(self):
        """Query can be created with a single anchor (Requirement 3.2)."""
        anchor = Anchor("doc1", 0, 5, compute_hash("hello"))

        query = Query(
            query_id="q1",
            question="What is hello?",
            anchors=(anchor,),
        )

        assert query.query_id == "q1"
        assert len(query.anchors) == 1
        assert query.anchors[0] == anchor

    def test_query_with_zero_anchors(self):
        """Query can be created with zero anchors (Requirement 3.2)."""
        query = Query(
            query_id="q1",
            question="Open-ended question?",
            anchors=(),
        )

        assert query.query_id == "q1"
        assert len(query.anchors) == 0

    def test_query_frozen(self):
        """Query is immutable (frozen)."""
        anchor = Anchor("doc1", 0, 5, compute_hash("hello"))
        query = Query(
            query_id="q1",
            question="Test?",
            anchors=(anchor,),
        )

        with pytest.raises(AttributeError):
            query.question = "modified"  # type: ignore

    def test_query_anchors_tuple_immutable(self):
        """Query anchors are stored as tuple for immutability."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("hello"))
        anchor2 = Anchor("doc1", 6, 11, compute_hash("world"))

        query = Query(
            query_id="q1",
            question="Test?",
            anchors=(anchor1, anchor2),
        )

        # Tuple is immutable
        assert isinstance(query.anchors, tuple)
        with pytest.raises(TypeError):
            query.anchors[0] = anchor2  # type: ignore

    def test_schema_version_defaults(self):
        """Schema version defaults to 0.1.0 (Requirement 3.3)."""
        query = Query(
            query_id="q1",
            question="Test?",
            anchors=(),
        )

        assert query.schema_version == "0.1.0"

    def test_query_with_multiple_documents(self):
        """Query can have anchors from multiple documents."""
        anchor1 = Anchor("doc1", 0, 5, compute_hash("hello"))
        anchor2 = Anchor("doc2", 10, 15, compute_hash("world"))

        query = Query(
            query_id="q1",
            question="Cross-document query?",
            anchors=(anchor1, anchor2),
        )

        assert len(query.anchors) == 2
        assert query.anchors[0].document_id == "doc1"
        assert query.anchors[1].document_id == "doc2"

    def test_query_hashable(self):
        """Query is hashable (frozen with tuple anchors)."""
        anchor = Anchor("doc1", 0, 5, compute_hash("hello"))
        query1 = Query(
            query_id="q1",
            question="Test?",
            anchors=(anchor,),
        )
        query2 = Query(
            query_id="q1",
            question="Test?",
            anchors=(anchor,),
        )

        # Can be used in sets and as dict keys
        query_set = {query1, query2}
        assert len(query_set) == 1  # Same content

        query_dict = {query1: "value"}
        assert query_dict[query2] == "value"
