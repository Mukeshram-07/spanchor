"""Property-based tests for storage functions.

These tests use Hypothesis to verify universal properties that must hold
across all possible inputs to storage operations.
"""

import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from spanchor.errors import InvalidSchemaError
from spanchor.storage.jsonl import read_gold_set


class TestStorageProperties:
    """Property-based tests for storage operations."""

    @given(
        query_ids=st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=2,
            max_size=10,
            unique=True,  # Ensure all IDs start unique
        ),
        dup_index=st.integers(min_value=1, max_value=9),  # Index 1+ for the duplicate
        question=st.text(min_size=1, max_size=500),  # question text
    )
    def test_duplicate_query_id_detection(
        self, query_ids: list[str], dup_index: int, question: str
    ) -> None:
        """Property 6: Query Set Duplicate Detection.

        **Validates: Requirements 3.5, 3.7**

        For any collection of Query objects with duplicate query_id values,
        loading as a Gold_Set SHALL raise InvalidSchemaError identifying
        the duplicated ID.

        This property ensures that:
        - Duplicate query_ids are always detected
        - The error message includes the duplicated query_id
        - The error includes the line number where the duplicate appears
        - Detection works regardless of where duplicates appear in the file
        """
        # Ensure dup_index is within bounds
        if dup_index >= len(query_ids):
            dup_index = len(query_ids) - 1

        # Create a duplicate: make the query at dup_index have the same ID as query 0
        duplicate_id = query_ids[0]
        query_ids[dup_index] = duplicate_id

        # Use tempfile to create temporary JSONL file
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_file = Path(tmpdir) / "gold_with_dup.jsonl"
            with jsonl_file.open("w", encoding="utf-8") as f:
                for query_id in query_ids:
                    data = {
                        "query_id": query_id,
                        "question": question,
                        "anchors": [],
                        "schema_version": "0.1.0",
                    }
                    f.write(json.dumps(data) + "\n")

            # Attempt to read the gold set - should raise InvalidSchemaError
            with pytest.raises(InvalidSchemaError) as exc_info:
                read_gold_set(jsonl_file)

            # Verify error message contains the duplicate ID
            error_message = str(exc_info.value)
            assert (
                "Duplicate query_id" in error_message
            ), f"Error message should mention 'Duplicate query_id', got: {error_message}"

            assert duplicate_id in error_message, (
                f"Error message should include the duplicated query_id '{duplicate_id}', "
                f"got: {error_message}"
            )

            # Verify error includes line number information
            assert (
                "Line:" in error_message
            ), f"Error message should include line number, got: {error_message}"

            # Verify the field name is included
            assert (
                "query_id" in error_message
            ), f"Error message should mention field 'query_id', got: {error_message}"

            # Verify the exception has the expected attributes
            assert exc_info.value.field_name == "query_id", (
                f"Exception field_name should be 'query_id', " f"got: {exc_info.value.field_name}"
            )

            assert exc_info.value.line_number is not None, "Exception should have line_number set"

            # The line number should be where the duplicate appears (1-indexed)
            # Line numbers are 1-indexed, so dup_index + 1 gives us the line number
            expected_line = dup_index + 1
            assert exc_info.value.line_number == expected_line, (
                f"Exception line_number should be {expected_line} "
                f"(the line with the duplicate), got: {exc_info.value.line_number}"
            )
