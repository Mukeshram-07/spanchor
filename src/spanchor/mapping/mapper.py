"""Chunk-to-span mapper for converting retrieval results to canonical spans.

The mapper handles both exact substring matching and whitespace-normalized fallback,
with configurable ambiguity resolution policies.
"""

import re
from dataclasses import dataclass, field
from typing import Literal

from spanchor.canonical.normalize import normalize_text
from spanchor.errors import AnchorResolutionError
from spanchor.models.document import Document


@dataclass(frozen=True, slots=True)
class MappingResult:
    """Result of mapping a chunk to canonical document spans.

    Attributes:
        status: Mapping status (MAPPED_EXACT, MAPPED_NORMALIZED, AMBIGUOUS, UNMAPPED)
        spans: List of (document_id, start, end) tuples for matched spans
        method: Description of mapping method used
    """

    status: Literal["MAPPED_EXACT", "MAPPED_NORMALIZED", "AMBIGUOUS", "UNMAPPED"]
    spans: list[tuple[str, int, int]] = field(default_factory=list)
    method: str = "none"


class ChunkMapper:
    """Maps chunk text to canonical document spans.

    The mapper searches for exact substring matches first, then falls back to
    whitespace-normalized matching. Handles ambiguity according to configured policy.

    Attributes:
        documents: Dictionary of document_id -> Document
        ambiguity_policy: How to handle ambiguous matches
        claimed_spans: Set of spans already claimed by other chunks
    """

    def __init__(
        self,
        documents: dict[str, Document],
        ambiguity_policy: Literal["first_unclaimed", "all_occurrences", "fail"] = "first_unclaimed",
    ) -> None:
        """Initialize ChunkMapper.

        Args:
            documents: Dictionary mapping document_id to Document objects
            ambiguity_policy: Policy for resolving ambiguous matches:
                - first_unclaimed: Use first occurrence not claimed by another chunk
                - all_occurrences: Return all occurrences as separate spans
                - fail: Raise AnchorResolutionError for ambiguous matches
        """
        self.documents = documents
        self.policy = ambiguity_policy
        self.claimed_spans: set[tuple[str, int, int]] = set()

    def map_chunk(self, chunk_text: str, document_id: str | None = None) -> MappingResult:
        """Map chunk text to canonical document span(s).

        Search order:
        1. Exact substring match in specified document or across corpus
        2. Whitespace-normalized match with offset mapping
        3. Mark as UNMAPPED if no match found

        Args:
            chunk_text: The chunk text to map
            document_id: Optional document_id to constrain search

        Returns:
            MappingResult with status and matched spans

        Raises:
            AnchorResolutionError: If ambiguous and policy is 'fail'
        """
        # Handle empty chunk
        if not chunk_text or not chunk_text.strip():
            return MappingResult(status="UNMAPPED", method="empty_chunk")

        # Normalize chunk text to canonical form (NFC + newline normalization)
        # This ensures we search for the same form that appears in canonical documents
        canonical_chunk = normalize_text(chunk_text)

        # Handle case where normalization resulted in empty/whitespace-only text
        if not canonical_chunk or not canonical_chunk.strip():
            return MappingResult(status="UNMAPPED", method="empty_chunk")

        # Determine search space
        if document_id:
            if document_id not in self.documents:
                return MappingResult(status="UNMAPPED", method="document_not_found")
            search_docs = {document_id: self.documents[document_id]}
        else:
            search_docs = self.documents

        # Try exact substring matching
        exact_matches = self._find_exact_matches(canonical_chunk, search_docs)
        if exact_matches:
            return self._handle_matches(
                exact_matches, canonical_chunk, "exact_substring", is_normalized=False
            )

        # Try whitespace-normalized matching
        normalized_matches = self._find_normalized_matches(canonical_chunk, search_docs)
        if normalized_matches:
            return self._handle_matches(
                normalized_matches, canonical_chunk, "whitespace_normalized", is_normalized=True
            )

        # No match found
        return MappingResult(status="UNMAPPED", method="no_match")

    def _find_exact_matches(
        self, chunk_text: str, search_docs: dict[str, Document]
    ) -> list[tuple[str, int, int]]:
        """Find all exact substring matches in the search space.

        Args:
            chunk_text: Text to search for
            search_docs: Documents to search in

        Returns:
            List of (document_id, start, end) tuples for all matches
        """
        matches: list[tuple[str, int, int]] = []

        for doc_id, doc in search_docs.items():
            # Find all occurrences in this document
            start = 0
            while True:
                pos = doc.text.find(chunk_text, start)
                if pos == -1:
                    break
                end = pos + len(chunk_text)
                matches.append((doc_id, pos, end))
                start = pos + 1  # Continue searching for overlapping matches

        return matches

    def _find_normalized_matches(
        self, chunk_text: str, search_docs: dict[str, Document]
    ) -> list[tuple[str, int, int]]:
        """Find matches using whitespace normalization.

        This normalizes both the chunk and document text by collapsing all
        whitespace sequences to single spaces, then maps back to original offsets.

        Args:
            chunk_text: Text to search for
            search_docs: Documents to search in

        Returns:
            List of (document_id, start, end) tuples for all matches
        """
        matches: list[tuple[str, int, int]] = []

        # Normalize the chunk text
        chunk_normalized = self._normalize_whitespace(chunk_text)
        if not chunk_normalized:
            return matches

        for doc_id, doc in search_docs.items():
            # Create normalized version and offset map
            doc_normalized, offset_map = self._create_offset_map(doc.text)

            # Find matches in normalized text
            start = 0
            while True:
                pos = doc_normalized.find(chunk_normalized, start)
                if pos == -1:
                    break

                # Map back to original offsets
                original_start = offset_map[pos]
                normalized_end = pos + len(chunk_normalized)
                # Handle case where normalized_end is beyond the offset_map
                if normalized_end >= len(offset_map):
                    original_end = len(doc.text)
                else:
                    original_end = offset_map[normalized_end]

                matches.append((doc_id, original_start, original_end))
                start = pos + 1

        return matches

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace by collapsing sequences to single spaces.

        Args:
            text: Text to normalize

        Returns:
            Text with all whitespace sequences replaced by single spaces
        """
        # Replace all whitespace sequences with single space
        normalized = re.sub(r"\s+", " ", text)
        # Strip leading/trailing whitespace
        return normalized.strip()

    def _create_offset_map(self, text: str) -> tuple[str, list[int]]:
        """Create a whitespace-normalized version with offset mapping.

        Args:
            text: Original text

        Returns:
            Tuple of (normalized_text, offset_map) where offset_map[i] gives
            the original text offset corresponding to normalized position i
        """
        normalized_chars: list[str] = []
        offset_map: list[int] = []
        in_whitespace = False

        for i, char in enumerate(text):
            if char.isspace():
                # Only add a space if we're not already in whitespace
                if not in_whitespace and normalized_chars:  # Don't start with space
                    normalized_chars.append(" ")
                    offset_map.append(i)
                    in_whitespace = True
            else:
                normalized_chars.append(char)
                offset_map.append(i)
                in_whitespace = False

        # Build normalized text
        normalized = "".join(normalized_chars)

        # Add final offset for end-of-string mapping
        offset_map.append(len(text))

        return normalized, offset_map

    def _handle_matches(
        self,
        matches: list[tuple[str, int, int]],
        chunk_text: str,
        method: str,
        is_normalized: bool,
    ) -> MappingResult:
        """Handle found matches according to ambiguity policy.

        Args:
            matches: List of (document_id, start, end) tuples
            chunk_text: Original chunk text (for error messages)
            method: Description of matching method used
            is_normalized: Whether this was a normalized match

        Returns:
            MappingResult with appropriate status and spans

        Raises:
            AnchorResolutionError: If ambiguous and policy is 'fail'
        """

        def get_status() -> Literal["MAPPED_EXACT", "MAPPED_NORMALIZED"]:
            return "MAPPED_NORMALIZED" if is_normalized else "MAPPED_EXACT"

        if len(matches) == 1:
            # Unique match
            self.claimed_spans.add(matches[0])
            return MappingResult(status=get_status(), spans=matches, method=method)

        # Multiple matches - handle ambiguity
        if len(matches) > 1:
            if self.policy == "fail":
                raise AnchorResolutionError(
                    document_id=matches[0][0],
                    reason=f"Ambiguous chunk: found {len(matches)} occurrences",
                )

            elif self.policy == "first_unclaimed":
                # Find first unclaimed match
                for match in matches:
                    if match not in self.claimed_spans:
                        self.claimed_spans.add(match)
                        return MappingResult(status=get_status(), spans=[match], method=method)

                # All matches claimed - mark as ambiguous
                return MappingResult(status="AMBIGUOUS", spans=matches, method=method)

            elif self.policy == "all_occurrences":
                # Return all occurrences
                for match in matches:
                    self.claimed_spans.add(match)
                return MappingResult(status="AMBIGUOUS", spans=matches, method=method)

        # Should not reach here
        return MappingResult(status="UNMAPPED", method=method)

    def reset_claims(self) -> None:
        """Reset claimed spans tracker.

        This should be called between mapping different queries to ensure
        the first_unclaimed policy works correctly per-query.
        """
        self.claimed_spans.clear()
