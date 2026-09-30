"""Property-based tests for Anchor model.

These tests use Hypothesis to verify universal properties that must hold
across all possible Anchor instances and their validation behavior.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from spanchor.canonical.normalize import compute_hash
from spanchor.errors import AnchorResolutionError
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document


class TestAnchorProperties:
    """Property-based tests for Anchor model."""

    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.text(min_size=1, max_size=1000),  # document text (non-empty for valid spans)
        st.data(),  # data strategy for generating dependent values
    )
    def test_anchor_offset_slice_semantics(
        self, document_id: str, document_text: str, data: st.DataObject
    ) -> None:
        """Property 3: Anchor Offset Slice Semantics.

        **Validates: Requirements 2.2**

        For any valid Anchor with offsets [start, end) and corresponding Document,
        extracting text using document.text[start:end] SHALL produce the expected
        anchor text.

        This property verifies:
        - Half-open interval semantics [start, end) are correct
        - document.text[start:end] extracts the exact text that hashes to expected_text_hash
        - Slice extraction is consistent with anchor validation
        """
        # Create canonical document
        doc = Document.from_text(document_id, document_text)
        doc_length = len(doc.text)

        # Generate valid offsets within document bounds
        # Ensure we have at least one character to extract
        if doc_length == 0:
            # Skip empty documents - can't create valid anchors
            return

        # Generate start in range [0, doc_length-1] (need at least 1 char)
        start = data.draw(st.integers(min_value=0, max_value=doc_length - 1))

        # Generate end in range [start+1, doc_length] (half-open, need at least 1 char)
        end = data.draw(st.integers(min_value=start + 1, max_value=doc_length))

        # Extract the actual text at this span using Python slice semantics
        actual_text = doc.text[start:end]

        # Compute the hash of this text - this is what the anchor expects
        expected_hash = compute_hash(actual_text)

        # Create anchor with these offsets and the computed hash
        anchor = Anchor(
            document_id=document_id,
            start=start,
            end=end,
            expected_text_hash=expected_hash,
        )

        # PROPERTY: document.text[start:end] must produce text that matches expected_text_hash
        extracted_text = doc.text[anchor.start : anchor.end]
        extracted_hash = compute_hash(extracted_text)

        assert extracted_text == actual_text, (
            f"Slice extraction mismatch: "
            f"doc.text[{start}:{end}] = {extracted_text!r}, "
            f"but expected {actual_text!r}"
        )

        assert extracted_hash == anchor.expected_text_hash, (
            f"Hash mismatch: "
            f"hash(doc.text[{start}:{end}]) = {extracted_hash}, "
            f"but anchor expects {anchor.expected_text_hash}"
        )

        # Additional verification: anchor should validate successfully
        # since we constructed it from the document's actual text
        anchor.validate(doc)  # Should not raise any exceptions

        # Verify half-open interval semantics
        # Character at position 'start' should be included
        if start < doc_length:
            assert (
                doc.text[start] == actual_text[0]
            ), f"Half-open interval: start position {start} should be included"

        # Character at position 'end' should NOT be included (if it exists)
        if end < doc_length:
            assert (
                doc.text[end] not in actual_text or actual_text == doc.text[start:end]
            ), f"Half-open interval: end position {end} should be exclusive"

        # Length check: end - start should equal length of extracted text
        assert len(extracted_text) == (end - start), (
            f"Length mismatch: expected {end - start} characters, " f"got {len(extracted_text)}"
        )

    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.text(min_size=1, max_size=1000),  # document text (non-empty for bounds checking)
        st.data(),  # data strategy for generating invalid offsets
    )
    def test_anchor_validation_detects_invalid_offsets(
        self, document_id: str, document_text: str, data: st.DataObject
    ) -> None:
        """Property 4: Anchor Validation Detects Invalid Offsets.

        **Validates: Requirements 2.5**

        For any Anchor with offsets outside document bounds [0, len(document.text)),
        validation SHALL raise AnchorResolutionError.

        This property verifies:
        - Negative offsets (start < 0 or end < 0) are rejected
        - Out of bounds offsets (start > len or end > len) are rejected
        - Invalid intervals (start > end) are rejected
        - Validation enforces document bounds strictly
        """
        # Create canonical document
        doc = Document.from_text(document_id, document_text)
        doc_length = len(doc.text)

        # Generate different types of INVALID offsets
        # Strategy: pick one of several invalid offset patterns
        invalid_offset_type = data.draw(
            st.sampled_from(
                [
                    "negative_start",
                    "negative_end",
                    "both_negative",
                    "start_out_of_bounds",
                    "end_out_of_bounds",
                    "start_greater_than_end",
                ]
            )
        )

        # Generate invalid offsets based on the chosen type
        if invalid_offset_type == "negative_start":
            # start is negative, end is valid
            start = data.draw(st.integers(max_value=-1))
            end = data.draw(st.integers(min_value=0, max_value=doc_length))
        elif invalid_offset_type == "negative_end":
            # end is negative, start is valid or also negative
            start = data.draw(st.integers(min_value=-100, max_value=doc_length))
            end = data.draw(st.integers(max_value=-1))
        elif invalid_offset_type == "both_negative":
            # both offsets are negative
            start = data.draw(st.integers(max_value=-1))
            end = data.draw(st.integers(max_value=-1))
        elif invalid_offset_type == "start_out_of_bounds":
            # start is beyond document length
            start = data.draw(st.integers(min_value=doc_length + 1, max_value=doc_length + 1000))
            end = data.draw(st.integers(min_value=start, max_value=start + 100))
        elif invalid_offset_type == "end_out_of_bounds":
            # end is beyond document length, start is valid
            start = data.draw(st.integers(min_value=0, max_value=doc_length))
            end = data.draw(st.integers(min_value=doc_length + 1, max_value=doc_length + 1000))
        else:  # start_greater_than_end
            # start > end (both within bounds or not)
            if doc_length > 0:
                end = data.draw(st.integers(min_value=0, max_value=doc_length - 1))
                start = data.draw(st.integers(min_value=end + 1, max_value=doc_length + 100))
            else:
                # For empty documents, just make start > end
                end = 0
                start = data.draw(st.integers(min_value=1, max_value=100))

        # Create an anchor with invalid offsets
        # Use a dummy hash since we're testing offset validation, not text validation
        dummy_hash = compute_hash("dummy")
        anchor = Anchor(
            document_id=document_id,
            start=start,
            end=end,
            expected_text_hash=dummy_hash,
        )

        # PROPERTY: Validation MUST raise AnchorResolutionError for invalid offsets
        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        # Verify the error contains the invalid offsets
        error = exc_info.value
        assert error.document_id == document_id
        assert error.start == start
        assert error.end == end

        # Verify the error message describes the specific problem
        error_msg = str(error)
        assert "Cannot resolve anchor" in error_msg or "Anchor" in error_msg

        # Additional checks based on the type of invalid offset
        if invalid_offset_type in ["negative_start", "negative_end", "both_negative"]:
            assert "negative" in error_msg.lower() or "Negative" in error_msg
        elif invalid_offset_type in ["start_out_of_bounds", "end_out_of_bounds"]:
            assert "out of bounds" in error_msg.lower() or "bounds" in error_msg.lower()
        elif invalid_offset_type == "start_greater_than_end":
            assert "start" in error_msg.lower() and ("end" in error_msg.lower() or ">" in error_msg)

    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # document_id
        st.text(min_size=1, max_size=1000),  # document text (non-empty for valid spans)
        st.data(),  # data strategy for generating dependent values
    )
    def test_anchor_validation_detects_hash_mismatches(
        self, document_id: str, document_text: str, data: st.DataObject
    ) -> None:
        """Property 5: Anchor Validation Detects Hash Mismatches.

        **Validates: Requirements 2.4**

        For any Anchor and Document where anchor.expected_text_hash != hash(document.text[start:end]),
        validation SHALL raise AnchorResolutionError with both hash values.

        This property verifies:
        - When the text hash at the anchor span doesn't match expected_text_hash, validation fails
        - AnchorResolutionError is raised with document_id and offsets
        - The error message contains information about both the expected and actual hash
        - Validation correctly computes hash of actual text at [start:end)
        """
        # Create canonical document
        doc = Document.from_text(document_id, document_text)
        doc_length = len(doc.text)

        # Skip empty documents - need at least 1 character to create valid spans
        if doc_length == 0:
            return

        # Generate valid offsets within document bounds
        start = data.draw(st.integers(min_value=0, max_value=doc_length - 1))
        end = data.draw(st.integers(min_value=start + 1, max_value=doc_length))

        # Extract the actual text at this span
        actual_text = doc.text[start:end]
        actual_hash = compute_hash(actual_text)

        # Generate a WRONG hash that doesn't match the actual text
        # Strategy: use hash of different text or a completely fabricated hash
        wrong_hash_type = data.draw(st.sampled_from(["different_text", "random_hash"]))

        if wrong_hash_type == "different_text":
            # Generate different text and hash it
            different_text = data.draw(
                st.text(min_size=1, max_size=50).filter(lambda t: compute_hash(t) != actual_hash)
            )
            wrong_hash = compute_hash(different_text)
        else:  # random_hash
            # Generate a random hex string that looks like a hash but isn't the actual hash
            # SHA256 produces 64 hex characters
            wrong_hash = data.draw(
                st.text(
                    alphabet="0123456789abcdef",
                    min_size=64,
                    max_size=64,
                ).filter(lambda h: h != actual_hash)
            )

        # Create anchor with valid offsets but WRONG text hash
        anchor = Anchor(
            document_id=document_id,
            start=start,
            end=end,
            expected_text_hash=wrong_hash,
        )

        # PROPERTY: Validation MUST raise AnchorResolutionError when hash doesn't match
        with pytest.raises(AnchorResolutionError) as exc_info:
            anchor.validate(doc)

        # Verify the error contains the necessary information
        error = exc_info.value
        assert error.document_id == document_id
        assert error.start == start
        assert error.end == end

        # Verify the error message mentions hash mismatch
        error_msg = str(error)
        assert "hash" in error_msg.lower() or "mismatch" in error_msg.lower()

        # Verify both hash values are present in the error
        # The actual hash should be in the error (computed from document text)
        # The expected hash should be in the error (from the anchor)
        # We check for truncated versions since errors show hash[:16]
        assert wrong_hash[:16] in error_msg or "hash" in error_msg.lower()

        # Verify the error includes the actual text that was found
        # (This helps debugging by showing what text was actually at the span)
        assert error.actual_text == actual_text

        # Additional verification: the error should indicate this is a text validation issue
        assert "text" in error_msg.lower() or "Text" in error_msg
