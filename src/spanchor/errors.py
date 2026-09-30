"""Typed exception hierarchy for spanchor.

All errors include:
- What happened (clear description)
- Values involved (document_id, query_id, hashes, offsets, etc.)
- Suggested action (how to fix it)
"""

from typing import Any


class SpanchorError(Exception):
    """Base exception for all spanchor errors."""

    pass


class InvalidSchemaError(SpanchorError):
    """Raised when a schema or format violation is detected.

    This includes:
    - Invalid JSON/JSONL format
    - Missing required fields
    - Type mismatches
    - Unsupported schema_version
    - Duplicate query_id values
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        field_name: str | None = None,
    ) -> None:
        """Initialize InvalidSchemaError.

        Args:
            message: Description of what went wrong
            file_path: Path to the file with the schema error
            line_number: Line number where the error occurred (1-indexed)
            field_name: Name of the problematic field
        """
        self.file_path = file_path
        self.line_number = line_number
        self.field_name = field_name

        details = [message]
        if file_path:
            details.append(f"File: {file_path}")
        if line_number:
            details.append(f"Line: {line_number}")
        if field_name:
            details.append(f"Field: {field_name}")

        details.append("Suggested action: Check the file format against the schema documentation.")

        super().__init__("\n".join(details))


class DocumentNotFoundError(SpanchorError):
    """Raised when a referenced document_id does not exist in the corpus.

    This typically occurs when:
    - An anchor references a document_id that wasn't loaded
    - A document was removed but anchors still reference it
    """

    def __init__(self, document_id: str, query_id: str | None = None) -> None:
        """Initialize DocumentNotFoundError.

        Args:
            document_id: The missing document identifier
            query_id: The query that references the missing document (if applicable)
        """
        self.document_id = document_id
        self.query_id = query_id

        message_parts = [
            f"Document not found: '{document_id}'",
        ]
        if query_id:
            message_parts.append(f"Referenced by query: '{query_id}'")

        message_parts.extend(
            [
                "Values involved:",
                f"  - document_id: {document_id}",
                "Suggested action: Ensure the document exists in the corpus directory "
                "or update anchors to reference valid documents.",
            ]
        )

        super().__init__("\n".join(message_parts))


class HashMismatchError(SpanchorError):
    """Raised when a document's current hash doesn't match the expected hash in an anchor.

    This indicates the source document has changed since the anchor was created.
    """

    def __init__(
        self,
        document_id: str,
        expected_hash: str,
        actual_hash: str,
        query_id: str | None = None,
    ) -> None:
        """Initialize HashMismatchError.

        Args:
            document_id: Identifier of the document with hash mismatch
            expected_hash: Hash stored in the anchor
            actual_hash: Current hash of the document
            query_id: Query containing the problematic anchor (if applicable)
        """
        self.document_id = document_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.query_id = query_id

        message_parts = [
            f"Hash mismatch for document '{document_id}'",
        ]
        if query_id:
            message_parts.append(f"In query: '{query_id}'")

        message_parts.extend(
            [
                "Values involved:",
                f"  - document_id: {document_id}",
                f"  - expected_hash: {expected_hash[:16]}...",
                f"  - actual_hash: {actual_hash[:16]}...",
                "Suggested action: The source document has changed. Either:",
                "  1. Restore the original document version, or",
                "  2. Re-validate and update the anchor with the new hash using 'spanchor validate'",
            ]
        )

        super().__init__("\n".join(message_parts))


class AnchorResolutionError(SpanchorError):
    """Raised when an anchor cannot be resolved to valid text in a document.

    This includes:
    - Offsets out of bounds
    - Text at offset doesn't match expected text
    - Ambiguous chunk mapping (when policy is 'fail')
    - Invalid offset values (negative, start >= end)
    """

    def __init__(
        self,
        document_id: str,
        start: int | None = None,
        end: int | None = None,
        expected_text: str | None = None,
        actual_text: str | None = None,
        query_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Initialize AnchorResolutionError.

        Args:
            document_id: Identifier of the document
            start: Start offset (inclusive)
            end: End offset (exclusive)
            expected_text: Text expected at the offset
            actual_text: Text actually found at the offset
            query_id: Query containing the problematic anchor (if applicable)
            reason: Additional context about why resolution failed
        """
        self.document_id = document_id
        self.start = start
        self.end = end
        self.expected_text = expected_text
        self.actual_text = actual_text
        self.query_id = query_id

        message_parts = [
            f"Cannot resolve anchor in document '{document_id}'",
        ]
        if query_id:
            message_parts.append(f"In query: '{query_id}'")
        if reason:
            message_parts.append(f"Reason: {reason}")

        message_parts.append("Values involved:")
        message_parts.append(f"  - document_id: {document_id}")
        if start is not None:
            message_parts.append(f"  - start: {start}")
        if end is not None:
            message_parts.append(f"  - end: {end}")
        if expected_text:
            preview = expected_text[:50] + "..." if len(expected_text) > 50 else expected_text
            message_parts.append(f"  - expected_text: {preview!r}")
        if actual_text:
            preview = actual_text[:50] + "..." if len(actual_text) > 50 else actual_text
            message_parts.append(f"  - actual_text: {preview!r}")

        message_parts.extend(
            [
                "Suggested action:",
                "  - Verify the document hasn't been modified (check hash)",
                "  - Verify offsets are within document bounds",
                "  - Re-create the anchor if the document has legitimately changed",
            ]
        )

        super().__init__("\n".join(message_parts))


class OrphanedAnchorError(SpanchorError):
    """Raised when an anchor references a document that has been deleted or is missing.

    This is similar to DocumentNotFoundError but specifically for cleanup/maintenance operations.
    """

    def __init__(
        self,
        document_id: str,
        query_ids: list[str],
    ) -> None:
        """Initialize OrphanedAnchorError.

        Args:
            document_id: The missing document identifier
            query_ids: List of query IDs that reference this document
        """
        self.document_id = document_id
        self.query_ids = query_ids

        message_parts = [
            f"Orphaned anchors detected: document '{document_id}' is missing",
            f"Number of affected queries: {len(query_ids)}",
        ]

        if len(query_ids) <= 5:
            message_parts.append(f"Affected query IDs: {', '.join(query_ids)}")
        else:
            message_parts.append(f"First 5 affected query IDs: {', '.join(query_ids[:5])}")

        message_parts.extend(
            [
                "Values involved:",
                f"  - document_id: {document_id}",
                f"  - affected_queries: {len(query_ids)}",
                "Suggested action:",
                "  1. Restore the missing document to the corpus, or",
                "  2. Remove the affected queries from the gold set, or",
                "  3. Update the queries to reference different documents",
            ]
        )

        super().__init__("\n".join(message_parts))


class InvalidRetrievalResultError(SpanchorError):
    """Raised when a retrieval result is malformed or contains invalid data.

    This includes:
    - Invalid rank values (non-positive)
    - Invalid score values (non-numeric)
    - Missing required fields based on result type
    - Inconsistent field combinations
    """

    def __init__(
        self,
        message: str,
        query_id: str | None = None,
        rank: int | None = None,
        result_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize InvalidRetrievalResultError.

        Args:
            message: Description of what's wrong with the result
            query_id: Query associated with this result
            rank: Rank of the problematic result
            result_data: The problematic result data
        """
        self.query_id = query_id
        self.rank = rank
        self.result_data = result_data

        message_parts = [
            f"Invalid retrieval result: {message}",
        ]
        if query_id:
            message_parts.append(f"Query: '{query_id}'")
        if rank is not None:
            message_parts.append(f"Rank: {rank}")

        message_parts.append("Suggested action: Check the retrieval result format and values.")

        super().__init__("\n".join(message_parts))


class EvaluationError(SpanchorError):
    """Raised when evaluation computation fails.

    This includes:
    - Empty gold spans (when recall/precision require non-empty gold)
    - Invalid K values (K <= 0)
    - Invalid min_overlap values (not in [0, 1])
    - Mathematical errors in metric computation
    """

    def __init__(
        self,
        message: str,
        query_id: str | None = None,
        metric_name: str | None = None,
        values: dict[str, Any] | None = None,
    ) -> None:
        """Initialize EvaluationError.

        Args:
            message: Description of the evaluation error
            query_id: Query where evaluation failed
            metric_name: Name of the metric being computed
            values: Relevant values involved in the error
        """
        self.query_id = query_id
        self.metric_name = metric_name
        self.values = values or {}

        message_parts = [
            f"Evaluation error: {message}",
        ]
        if query_id:
            message_parts.append(f"Query: '{query_id}'")
        if metric_name:
            message_parts.append(f"Metric: {metric_name}")

        if values:
            message_parts.append("Values involved:")
            for key, value in values.items():
                message_parts.append(f"  - {key}: {value}")

        message_parts.append(
            "Suggested action: Verify input parameters and ensure gold spans are valid."
        )

        super().__init__("\n".join(message_parts))


class ComparisonError(SpanchorError):
    """Raised when comparison between runs fails.

    This includes:
    - Incompatible runs (different query sets)
    - Minimum query count not met
    - Invalid policy thresholds
    - Schema version mismatches
    """

    def __init__(
        self,
        message: str,
        baseline_info: dict[str, Any] | None = None,
        candidate_info: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ComparisonError.

        Args:
            message: Description of the comparison error
            baseline_info: Information about the baseline run
            candidate_info: Information about the candidate run
        """
        self.baseline_info = baseline_info or {}
        self.candidate_info = candidate_info or {}

        message_parts = [
            f"Comparison error: {message}",
        ]

        if baseline_info:
            message_parts.append("Baseline run:")
            for key, value in baseline_info.items():
                message_parts.append(f"  - {key}: {value}")

        if candidate_info:
            message_parts.append("Candidate run:")
            for key, value in candidate_info.items():
                message_parts.append(f"  - {key}: {value}")

        message_parts.append(
            "Suggested action: Ensure both runs use compatible gold sets and schema versions."
        )

        super().__init__("\n".join(message_parts))
