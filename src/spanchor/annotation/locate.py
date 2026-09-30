"""Annotation helper for locating text in canonical documents.

Provides locate_text() to find exact or whitespace-normalized matches
across all documents, displaying document_id, offsets, text hash, and
surrounding context for each occurrence.
"""

import re
from dataclasses import dataclass

from spanchor.canonical.normalize import compute_hash
from spanchor.models.document import Document

# Number of characters to display before/after each match for context
DEFAULT_CONTEXT_CHARS = 80


@dataclass
class LocateMatch:
    """A single text match found in a document.

    Attributes:
        document_id: ID of the document containing the match
        start: Start offset (inclusive, Unicode code-point in canonical text)
        end: End offset (exclusive, Unicode code-point in canonical text)
        matched_text: The actual text at this span (canonical form)
        text_hash: SHA256 hash of the matched text
        context_before: Characters immediately before the match (for display)
        context_after: Characters immediately after the match (for display)
        occurrence_number: 1-based index when multiple matches exist
        is_normalized_match: True if found via whitespace normalization fallback
    """

    document_id: str
    start: int
    end: int
    matched_text: str
    text_hash: str
    context_before: str
    context_after: str
    occurrence_number: int = 1
    is_normalized_match: bool = False


def locate_text(
    search_text: str,
    documents: dict[str, Document],
    context_chars: int = DEFAULT_CONTEXT_CHARS,
) -> list[LocateMatch]:
    """Search for text in canonical documents and return annotated matches.

    First attempts exact substring search. If no exact matches are found,
    falls back to whitespace-normalized search.

    All offsets are Unicode code-point offsets into the canonical document text
    (NFC-normalized, \\n-only line endings). Half-open intervals [start, end).

    Args:
        search_text: Text to search for (searched as-is for exact, then normalized)
        documents: Mapping of document_id to Document objects to search in
        context_chars: Number of characters to include before/after each match
            for display context

    Returns:
        List of LocateMatch objects, one per occurrence found, sorted by
        document_id then start offset. Each match has occurrence_number set
        to its 1-based position in the returned list. Returns empty list if
        no matches found.

    Examples:
        >>> doc = Document.from_text("doc1", "The quick brown fox")
        >>> matches = locate_text("quick brown", {"doc1": doc})
        >>> len(matches)
        1
        >>> matches[0].start, matches[0].end
        (4, 15)
    """
    if not search_text:
        return []

    if not documents:
        return []

    # Phase 1: Exact substring search
    exact_matches = _find_exact_matches(search_text, documents, context_chars)
    if exact_matches:
        _assign_occurrence_numbers(exact_matches)
        return exact_matches

    # Phase 2: Whitespace-normalized fallback
    normalized_matches = _find_normalized_matches(search_text, documents, context_chars)
    _assign_occurrence_numbers(normalized_matches)
    return normalized_matches


def _find_exact_matches(
    search_text: str,
    documents: dict[str, Document],
    context_chars: int,
) -> list[LocateMatch]:
    """Find all exact substring occurrences across documents.

    Args:
        search_text: Text to search for verbatim
        documents: Documents to search in
        context_chars: Context window size in characters

    Returns:
        List of LocateMatch objects, sorted by document_id then start
    """
    matches: list[LocateMatch] = []

    for doc_id in sorted(documents.keys()):
        doc = documents[doc_id]
        text = doc.text
        search_len = len(search_text)

        pos = 0
        while True:
            idx = text.find(search_text, pos)
            if idx == -1:
                break

            end = idx + search_len
            matched = text[idx:end]

            matches.append(
                LocateMatch(
                    document_id=doc_id,
                    start=idx,
                    end=end,
                    matched_text=matched,
                    text_hash=compute_hash(matched),
                    context_before=_extract_context_before(text, idx, context_chars),
                    context_after=_extract_context_after(text, end, context_chars),
                    is_normalized_match=False,
                )
            )

            # Advance by 1 to catch overlapping matches
            pos = idx + 1

    return matches


def _normalize_whitespace(text: str) -> str:
    """Collapse all whitespace sequences to a single space and strip ends.

    Args:
        text: Input text

    Returns:
        Text with all whitespace sequences replaced by a single space, stripped
    """
    return re.sub(r"\s+", " ", text).strip()


def _build_offset_map(text: str) -> tuple[str, list[int]]:
    """Build a whitespace-normalized version of text with an offset map.

    The offset map maps each position in the normalized text back to the
    corresponding position in the original text.

    Args:
        text: Original text

    Returns:
        Tuple of (normalized_text, offset_map) where offset_map[i] is the
        original text index corresponding to normalized index i. offset_map
        has one extra entry at the end pointing to len(text).
    """
    norm_chars: list[str] = []
    offset_map: list[int] = []
    in_ws = False

    for i, ch in enumerate(text):
        if ch.isspace():
            if not in_ws and norm_chars:  # Don't emit leading space
                norm_chars.append(" ")
                offset_map.append(i)
                in_ws = True
        else:
            norm_chars.append(ch)
            offset_map.append(i)
            in_ws = False

    # Sentinel: maps end-of-normalized-text to end-of-original-text
    offset_map.append(len(text))

    return "".join(norm_chars), offset_map


def _find_normalized_matches(
    search_text: str,
    documents: dict[str, Document],
    context_chars: int,
) -> list[LocateMatch]:
    """Find matches using whitespace normalization and offset mapping.

    Normalizes whitespace in both search text and document text, finds matches,
    then maps back to original offsets.

    Args:
        search_text: Text to search for (will be whitespace-normalized)
        documents: Documents to search in
        context_chars: Context window size in characters

    Returns:
        List of LocateMatch objects, sorted by document_id then start
    """
    search_normalized = _normalize_whitespace(search_text)
    if not search_normalized:
        return []

    matches: list[LocateMatch] = []

    for doc_id in sorted(documents.keys()):
        doc = documents[doc_id]
        doc_normalized, offset_map = _build_offset_map(doc.text)

        pos = 0
        while True:
            idx = doc_normalized.find(search_normalized, pos)
            if idx == -1:
                break

            norm_end = idx + len(search_normalized)

            # Map back to original offsets
            original_start = offset_map[idx]
            # norm_end may equal len(doc_normalized), handled by sentinel
            original_end = offset_map[min(norm_end, len(offset_map) - 1)]

            matched = doc.text[original_start:original_end]

            matches.append(
                LocateMatch(
                    document_id=doc_id,
                    start=original_start,
                    end=original_end,
                    matched_text=matched,
                    text_hash=compute_hash(matched),
                    context_before=_extract_context_before(doc.text, original_start, context_chars),
                    context_after=_extract_context_after(doc.text, original_end, context_chars),
                    is_normalized_match=True,
                )
            )

            pos = idx + 1

    return matches


def _extract_context_before(text: str, start: int, context_chars: int) -> str:
    """Extract up to context_chars characters before the match start.

    Args:
        text: Full document text
        start: Start offset of the match
        context_chars: Maximum characters to include

    Returns:
        Context string (may be shorter than context_chars if near document start)
    """
    ctx_start = max(0, start - context_chars)
    return text[ctx_start:start]


def _extract_context_after(text: str, end: int, context_chars: int) -> str:
    """Extract up to context_chars characters after the match end.

    Args:
        text: Full document text
        end: End offset of the match (exclusive)
        context_chars: Maximum characters to include

    Returns:
        Context string (may be shorter than context_chars if near document end)
    """
    ctx_end = min(len(text), end + context_chars)
    return text[end:ctx_end]


def _assign_occurrence_numbers(matches: list[LocateMatch]) -> None:
    """Assign 1-based occurrence numbers to a list of matches in-place.

    Mutates each match's occurrence_number field.

    Args:
        matches: List of LocateMatch objects to number
    """
    for i, match in enumerate(matches, start=1):
        # LocateMatch is a regular dataclass (not frozen), so direct assignment is fine
        match.occurrence_number = i


def format_matches(matches: list[LocateMatch], show_context: bool = True) -> str:
    """Format locate matches as a human-readable string.

    Produces output suitable for terminal display. Each match shows:
    - Occurrence number (when multiple matches)
    - document_id, start offset, end offset
    - text hash (SHA256)
    - surrounding context (if show_context=True)
    - match indicator noting if whitespace normalization was used

    Args:
        matches: List of LocateMatch objects from locate_text()
        show_context: Whether to include surrounding context in output

    Returns:
        Formatted string ready for display, or a "no matches" message
    """
    if not matches:
        return "No matches found."

    lines: list[str] = []
    total = len(matches)

    for match in matches:
        if total > 1:
            lines.append(f"[{match.occurrence_number}/{total}]")

        method_note = " (whitespace-normalized)" if match.is_normalized_match else ""
        lines.append(f"  document_id : {match.document_id}")
        lines.append(f"  offsets     : [{match.start}, {match.end}){method_note}")
        lines.append(f"  text_hash   : {match.text_hash}")

        if show_context:
            before = _render_context(match.context_before)
            after = _render_context(match.context_after)
            matched = match.matched_text.replace("\n", "\\n")
            lines.append(f"  context     : ...{before}»{matched}«{after}...")

        if total > 1 and match.occurrence_number < total:
            lines.append("")  # blank line between matches

    return "\n".join(lines)


def _render_context(ctx: str) -> str:
    """Render a context snippet, escaping newlines for single-line display.

    Args:
        ctx: Context string

    Returns:
        Rendered string with newlines replaced by \\n
    """
    return ctx.replace("\n", "\\n")
