"""Property-based tests for ChunkMapper.

These tests use Hypothesis to verify universal properties that must hold
across all possible chunk mapping scenarios.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from spanchor.mapping.mapper import ChunkMapper
from spanchor.models.document import Document


@st.composite
def document_and_exact_substring(draw: st.DrawFn) -> tuple[str, str]:
    """Generate a (document_text, substring) pair where substring is a valid exact substring.

    Strategy:
    - Draw a document text with min_size=1
    - Ensure the canonical document text has at least one non-whitespace character
      (so we can always find a non-whitespace-only substring to map)
    - Draw start and end indices into the canonical document text
    - Return the document text and a non-whitespace-only substring
    """
    # Use a text that contains at least one non-whitespace character so the
    # canonical form is guaranteed to have a mappable substring.
    raw_text = draw(st.text(min_size=1).filter(lambda t: any(not c.isspace() for c in t)))
    doc = Document.from_text("doc1", raw_text)
    doc_text = doc.text

    # Find all positions of non-whitespace characters to guarantee a non-empty
    # non-whitespace-only substring exists.
    non_ws_positions = [i for i, c in enumerate(doc_text) if not c.isspace()]
    # At least one must exist (guaranteed by the filter above).
    # Pick start <= some non-ws position and end > that position.
    anchor_pos = draw(st.sampled_from(non_ws_positions))

    # start can be anywhere from 0 up to anchor_pos (inclusive)
    start = draw(st.integers(min_value=0, max_value=anchor_pos))
    # end must be at least anchor_pos+1 so the substring contains that non-ws char
    end = draw(st.integers(min_value=anchor_pos + 1, max_value=len(doc_text)))

    substring = doc_text[start:end]
    return doc_text, substring


class TestChunkMapperExactSubstringProperties:
    """Property-based tests for exact substring detection in ChunkMapper."""

    @given(doc_and_sub=document_and_exact_substring())
    @settings(max_examples=200)
    def test_exact_substring_maps_to_mapped_exact(self, doc_and_sub: tuple[str, str]) -> None:
        """Property 10: Chunk Mapper Exact Substring Detection.

        **Validates: Requirements 5.1, 5.2**

        For any chunk text that is an exact substring of a document, the
        ChunkMapper SHALL find the chunk and return MAPPED_EXACT status.

        This property verifies:
        - Any valid substring of a document always produces MAPPED_EXACT status
        - The returned span text equals the original substring exactly
        - The span offsets are valid half-open intervals within the document
        """
        doc_text, substring = doc_and_sub

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="first_unclaimed")

        result = mapper.map_chunk(substring, document_id="doc1")

        # PROPERTY: exact substring MUST produce MAPPED_EXACT
        assert result.status == "MAPPED_EXACT", (
            f"Expected MAPPED_EXACT for exact substring, got {result.status!r}. "
            f"substring={substring!r}, doc_text={doc_text!r}"
        )

        # PROPERTY: at least one span must be returned
        assert len(result.spans) >= 1, (
            f"Expected at least one span, got {result.spans}. " f"substring={substring!r}"
        )

        # PROPERTY: the matched span text equals the original substring
        doc_id, start, end = result.spans[0]
        matched_text = doc.text[start:end]

        assert matched_text == substring, (
            f"Matched span text mismatch: "
            f"doc.text[{start}:{end}] = {matched_text!r}, "
            f"expected {substring!r}"
        )

        # PROPERTY: span offsets are valid half-open intervals within the document
        assert (
            0 <= start < end <= len(doc.text)
        ), f"Span [{start}, {end}) out of bounds for document of length {len(doc.text)}"


class TestChunkMapperPolicyProperties:
    """Property-based tests for ChunkMapper ambiguity resolution policies."""

    @given(
        chunk_text=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),  # no surrogates
                blacklist_characters=("\x00",),
            ),
            min_size=1,
            max_size=20,
        ).filter(lambda t: t.strip()),  # non-empty, non-whitespace-only
    )
    def test_first_unclaimed_policy_successive_calls_return_unique_spans(
        self, chunk_text: str
    ) -> None:
        """Property 14: Chunk Mapper Policy Enforcement - First Unclaimed.

        **Validates: Requirements 5.5**

        For any AMBIGUOUS chunk with policy="first_unclaimed", each successive
        mapping call SHALL return the next unclaimed occurrence.

        This property verifies:
        1. Each of the N calls returns MAPPED_EXACT with a unique span.
        2. All returned spans are distinct from each other.
        3. A (N+1)th call (all occurrences claimed) returns AMBIGUOUS.
        """
        N = 3

        # Build document text as N copies of chunk_text separated by a unique separator
        # Use a separator that cannot appear in chunk_text to prevent accidental extra matches
        separator = "|SEP|"
        doc_text = separator.join([chunk_text] * N)

        # Safety: confirm the chunk appears exactly N times
        # (If chunk_text itself contains the separator, we might get more matches.
        # The filter below skips those degenerate cases.)
        count = doc_text.count(chunk_text)
        if count != N:
            # chunk_text overlaps with separator — skip this example
            return

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="first_unclaimed")

        collected_spans: list[tuple[str, int, int]] = []

        # --- N successive calls: each should resolve to a distinct MAPPED_EXACT span ---
        for call_idx in range(N):
            result = mapper.map_chunk(chunk_text, document_id="doc1")

            assert result.status == "MAPPED_EXACT", (
                f"Call {call_idx + 1}: expected MAPPED_EXACT, got {result.status!r}. "
                f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
            )
            assert (
                len(result.spans) == 1
            ), f"Call {call_idx + 1}: expected exactly 1 span, got {result.spans}"

            span = result.spans[0]

            assert span not in collected_spans, (
                f"Call {call_idx + 1}: span {span} was already returned by a previous call. "
                f"Collected so far: {collected_spans}"
            )

            collected_spans.append(span)

        # Verify all N spans are mutually distinct
        assert (
            len(set(collected_spans)) == N
        ), f"Expected {N} unique spans, but got duplicates: {collected_spans}"

        # --- (N+1)th call: all occurrences are claimed → should return AMBIGUOUS ---
        overflow_result = mapper.map_chunk(chunk_text, document_id="doc1")

        assert overflow_result.status == "AMBIGUOUS", (
            f"(N+1)th call: expected AMBIGUOUS (all occurrences claimed), "
            f"got {overflow_result.status!r}. "
            f"chunk_text={chunk_text!r}, collected_spans={collected_spans}"
        )

    @given(
        chunk_text=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),  # no surrogates
                blacklist_characters=("\x00",),
            ),
            min_size=1,
            max_size=20,
        ).filter(lambda t: t.strip()),  # non-empty, non-whitespace-only
    )
    def test_all_occurrences_policy_returns_n_spans(self, chunk_text: str) -> None:
        """Property 15: Chunk Mapper Policy Enforcement - All Occurrences.

        **Validates: Requirements 5.6**

        For any AMBIGUOUS chunk with policy="all_occurrences" appearing N times,
        mapping SHALL create N span results.

        This property verifies:
        1. Result status is AMBIGUOUS (multiple occurrences found).
        2. Result contains exactly N spans.
        3. All N spans are distinct from each other.
        """
        N = 3

        # Build document text as N copies of chunk_text separated by a unique separator
        # Use a separator that cannot appear in chunk_text to prevent accidental extra matches
        separator = "|SEP|"
        doc_text = separator.join([chunk_text] * N)

        # Safety: confirm the chunk appears exactly N times
        # (If chunk_text itself contains the separator, we might get more matches.
        # The filter below skips those degenerate cases.)
        count = doc_text.count(chunk_text)
        if count != N:
            # chunk_text overlaps with separator — skip this example
            return

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="all_occurrences")

        result = mapper.map_chunk(chunk_text, document_id="doc1")

        # PROPERTY: result status must be AMBIGUOUS for N > 1 occurrences
        assert result.status == "AMBIGUOUS", (
            f"Expected AMBIGUOUS for chunk appearing {N} times, got {result.status!r}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )

        # PROPERTY: result must contain exactly N spans
        assert len(result.spans) == N, (
            f"Expected exactly {N} spans, got {len(result.spans)}: {result.spans}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )

        # PROPERTY: all N spans must be distinct
        assert len(set(result.spans)) == N, (
            f"Expected {N} unique spans but got duplicates: {result.spans}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )


import string


class TestChunkMapperWhitespaceNormalizationFallback:
    """Property-based tests for ChunkMapper whitespace normalization fallback."""

    @given(
        words=st.lists(
            st.text(alphabet=string.ascii_letters, min_size=1, max_size=8),
            min_size=2,
            max_size=5,
        )
    )
    @settings(max_examples=100)
    def test_whitespace_normalization_fallback_maps_to_mapped_normalized(
        self, words: list[str]
    ) -> None:
        """Property 11: Chunk Mapper Whitespace Normalization Fallback.

        **Validates: Requirements 5.3**

        For any chunk text that differs from document text only by whitespace,
        the ChunkMapper SHALL successfully map it with MAPPED_NORMALIZED status.

        This property verifies:
        - Chunk text joined with single spaces maps via whitespace normalization
        - Document text joined with 2-3 spaces guarantees no exact match
        - Result status is MAPPED_NORMALIZED
        - At least one span is returned
        """
        chunk_text = " ".join(words)
        # Join with 2 spaces to guarantee no exact match with chunk_text
        doc_text = "  ".join(words)

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="first_unclaimed")

        result = mapper.map_chunk(chunk_text, document_id="doc1")

        assert result.status == "MAPPED_NORMALIZED", (
            f"Expected MAPPED_NORMALIZED for whitespace-only diff, got {result.status!r}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )

        assert len(result.spans) >= 1, (
            f"Expected at least one span, got {result.spans}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )


class TestChunkMapperAmbiguityDetection:
    """Property-based tests for ChunkMapper ambiguity detection."""

    @given(
        chunk_text=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),
                blacklist_characters=("\x00",),
            ),
            min_size=1,
            max_size=15,
        ).filter(lambda t: t.strip())
    )
    @settings(max_examples=100)
    def test_duplicate_chunk_marked_ambiguous_with_all_occurrences_policy(
        self, chunk_text: str
    ) -> None:
        """Property 12: Chunk Mapper Ambiguity Detection.

        **Validates: Requirements 5.4**

        For any chunk text appearing N > 1 times in the search space, the
        ChunkMapper SHALL mark the result as AMBIGUOUS when using all_occurrences policy.

        This property verifies:
        - Any chunk text that appears exactly twice in a document is AMBIGUOUS
        - The result contains exactly 2 spans
        """
        doc_text = "|SEP1|" + chunk_text + "|SEP2|" + chunk_text + "|SEP3|"

        # Skip if chunk_text overlaps with the separators causing extra matches
        if doc_text.count(chunk_text) != 2:
            return

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="all_occurrences")

        result = mapper.map_chunk(chunk_text, document_id="doc1")

        assert result.status == "AMBIGUOUS", (
            f"Expected AMBIGUOUS for chunk appearing twice, got {result.status!r}. "
            f"chunk_text={chunk_text!r}, doc_text={doc_text!r}"
        )

        assert len(result.spans) == 2, (
            f"Expected exactly 2 spans, got {len(result.spans)}: {result.spans}. "
            f"chunk_text={chunk_text!r}"
        )


class TestChunkMapperUnmappedDetection:
    """Property-based tests for ChunkMapper unmapped detection."""

    @given(
        doc_text=st.text(
            alphabet=string.ascii_lowercase + " ",
            min_size=5,
            max_size=50,
        )
    )
    @settings(max_examples=100)
    def test_chunk_not_in_corpus_returns_unmapped(self, doc_text: str) -> None:
        """Property 13: Chunk Mapper Unmapped Detection.

        **Validates: Requirements 5.9**

        For any chunk text not present in the document corpus (even after
        whitespace normalization), the ChunkMapper SHALL return UNMAPPED status.

        This property verifies:
        - A sentinel chunk guaranteed absent from the document returns UNMAPPED
        - The result spans list is empty
        """
        # Sentinel contains uppercase letters + digits — never present in
        # doc_text whose alphabet is ascii_lowercase + space only.
        sentinel_chunk = "ZZZNOTFOUNDZZZZ"

        doc = Document.from_text("doc1", doc_text)
        mapper = ChunkMapper(documents={"doc1": doc}, ambiguity_policy="first_unclaimed")

        result = mapper.map_chunk(sentinel_chunk, document_id="doc1")

        assert result.status == "UNMAPPED", (
            f"Expected UNMAPPED for chunk not in corpus, got {result.status!r}. "
            f"chunk={sentinel_chunk!r}, doc_text={doc_text!r}"
        )

        assert result.spans == [], (
            f"Expected empty spans for UNMAPPED result, got {result.spans}. "
            f"chunk={sentinel_chunk!r}, doc_text={doc_text!r}"
        )
