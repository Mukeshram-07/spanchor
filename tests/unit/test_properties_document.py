"""Property-based tests for Document model.

These tests use Hypothesis to verify universal properties that must hold
across all possible Document instances.
"""

from dataclasses import asdict

from hypothesis import given
from hypothesis import strategies as st

from spanchor.models.document import Document


class TestDocumentProperties:
    """Property-based tests for Document model."""

    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.text(min_size=0, max_size=1000),  # text content
    )
    def test_document_serialization_round_trip(self, document_id: str, text_content: str) -> None:
        """Property 2: Document Serialization Round-Trip.

        **Validates: Requirements 1.5**

        For any valid Document, serializing to JSON and deserializing SHALL
        preserve the document_id, canonical text, and sha256 hash exactly.

        This property ensures that:
        - Document → dict → Document preserves all fields
        - No information is lost during serialization
        - Hash integrity is maintained through the round-trip
        """
        # Create document from text (applies canonicalization and hashing)
        original = Document.from_text(document_id, text_content)

        # Serialize to dict (simulating JSON serialization)
        serialized = asdict(original)

        # Deserialize from dict
        deserialized = Document(**serialized)

        # Assert all fields are preserved exactly
        assert (
            deserialized.document_id == original.document_id
        ), f"document_id changed: {original.document_id!r} → {deserialized.document_id!r}"

        assert (
            deserialized.text == original.text
        ), f"text changed: {original.text!r} → {deserialized.text!r}"

        assert (
            deserialized.sha256 == original.sha256
        ), f"sha256 changed: {original.sha256!r} → {deserialized.sha256!r}"

        assert deserialized.schema_version == original.schema_version, (
            f"schema_version changed: {original.schema_version!r} → "
            f"{deserialized.schema_version!r}"
        )

        # Verify complete equality
        assert deserialized == original, "Deserialized document is not equal to original"
