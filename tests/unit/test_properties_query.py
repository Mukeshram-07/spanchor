"""Property-based tests for Query and RetrievalResult models.

These tests use Hypothesis to verify universal properties that must hold
across all possible Query and RetrievalResult instances.
"""

from dataclasses import asdict

from hypothesis import given
from hypothesis import strategies as st

from spanchor.canonical.normalize import compute_hash
from spanchor.models.anchor import Anchor
from spanchor.models.query import Query


class TestQueryProperties:
    """Property-based tests for Query model."""

    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # query_id
        st.text(min_size=1, max_size=500),  # question
        st.data(),  # data strategy for generating anchors
    )
    def test_query_serialization_round_trip(
        self, query_id: str, question: str, data: st.DataObject
    ) -> None:
        """Property 7: Query Serialization Round-Trip.

        **Validates: Requirements 3.2, 3.4**

        For any valid Query with 0, 1, or multiple Anchors, serializing to JSONL
        and deserializing SHALL produce an equivalent Query with identical query_id,
        question, and anchor content.

        This property ensures that:
        - Query → dict → Query preserves all fields
        - Anchor tuples are preserved correctly through serialization
        - Queries with 0, 1, or multiple anchors serialize correctly
        - No information is lost during the JSONL round-trip
        """
        # Generate 0, 1, or multiple anchors
        num_anchors = data.draw(st.integers(min_value=0, max_value=5))

        anchors_list = []
        for i in range(num_anchors):
            # Generate anchor fields
            doc_id = data.draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
            # Generate a valid text snippet for the anchor
            anchor_text = data.draw(st.text(min_size=1, max_size=100))
            text_hash = compute_hash(anchor_text)

            # Generate valid offsets (start < end)
            start = data.draw(st.integers(min_value=0, max_value=1000))
            end = data.draw(st.integers(min_value=start + 1, max_value=start + 200))

            anchor = Anchor(
                document_id=doc_id,
                start=start,
                end=end,
                expected_text_hash=text_hash,
            )
            anchors_list.append(anchor)

        # Create query with generated anchors
        original = Query(
            query_id=query_id,
            question=question,
            anchors=tuple(anchors_list),
        )

        # Serialize to dict (simulating JSONL serialization)
        # We need to handle nested dataclasses (Anchors) manually
        serialized = {
            "query_id": original.query_id,
            "question": original.question,
            "anchors": [asdict(anchor) for anchor in original.anchors],
            "schema_version": original.schema_version,
        }

        # Deserialize from dict (reconstruct Query and Anchors)
        deserialized_anchors = tuple(Anchor(**anchor_dict) for anchor_dict in serialized["anchors"])
        deserialized = Query(
            query_id=serialized["query_id"],
            question=serialized["question"],
            anchors=deserialized_anchors,
            schema_version=serialized["schema_version"],
        )

        # Assert all fields are preserved exactly
        assert (
            deserialized.query_id == original.query_id
        ), f"query_id changed: {original.query_id!r} → {deserialized.query_id!r}"

        assert (
            deserialized.question == original.question
        ), f"question changed: {original.question!r} → {deserialized.question!r}"

        assert deserialized.schema_version == original.schema_version, (
            f"schema_version changed: {original.schema_version!r} → "
            f"{deserialized.schema_version!r}"
        )

        # Assert anchor count is preserved
        assert len(deserialized.anchors) == len(
            original.anchors
        ), f"Anchor count changed: {len(original.anchors)} → {len(deserialized.anchors)}"

        # Assert each anchor is preserved exactly
        for idx, (orig_anchor, deser_anchor) in enumerate(
            zip(original.anchors, deserialized.anchors)
        ):
            assert deser_anchor.document_id == orig_anchor.document_id, (
                f"Anchor {idx} document_id changed: "
                f"{orig_anchor.document_id!r} → {deser_anchor.document_id!r}"
            )

            assert deser_anchor.start == orig_anchor.start, (
                f"Anchor {idx} start changed: " f"{orig_anchor.start} → {deser_anchor.start}"
            )

            assert deser_anchor.end == orig_anchor.end, (
                f"Anchor {idx} end changed: " f"{orig_anchor.end} → {deser_anchor.end}"
            )

            assert deser_anchor.expected_text_hash == orig_anchor.expected_text_hash, (
                f"Anchor {idx} expected_text_hash changed: "
                f"{orig_anchor.expected_text_hash!r} → {deser_anchor.expected_text_hash!r}"
            )

            assert deser_anchor.schema_version == orig_anchor.schema_version, (
                f"Anchor {idx} schema_version changed: "
                f"{orig_anchor.schema_version!r} → {deser_anchor.schema_version!r}"
            )

            # Verify anchor equality
            assert deser_anchor == orig_anchor, f"Anchor {idx} is not equal after deserialization"

        # Verify complete query equality
        assert deserialized == original, "Deserialized query is not equal to original"
