"""Unit tests for chunk-to-span mapper."""

import pytest

from spanchor.errors import AnchorResolutionError
from spanchor.mapping import ChunkMapper, MappingResult
from spanchor.models.document import Document


@pytest.fixture
def sample_docs() -> dict[str, Document]:
    """Create sample documents for testing."""
    doc1 = Document.from_text("doc1", "The quick brown fox jumps over the lazy dog.")
    doc2 = Document.from_text(
        "doc2", "The quick brown fox appears twice. The quick brown fox is here again."
    )
    doc3 = Document.from_text("doc3", "Text with   extra    whitespace   in it.")
    return {"doc1": doc1, "doc2": doc2, "doc3": doc3}


class TestChunkMapperExactMatching:
    """Test exact substring matching."""

    def test_exact_match_single_occurrence(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping a chunk with a single exact match."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("quick brown fox", document_id="doc1")

        assert result.status == "MAPPED_EXACT"
        assert len(result.spans) == 1
        assert result.spans[0] == ("doc1", 4, 19)
        assert result.method == "exact_substring"

    def test_exact_match_multiple_occurrences_first_unclaimed(
        self, sample_docs: dict[str, Document]
    ) -> None:
        """Test mapping a chunk that appears multiple times with first_unclaimed policy."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="first_unclaimed")

        # First mapping should get first occurrence
        result1 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result1.status == "MAPPED_EXACT"
        assert len(result1.spans) == 1
        assert result1.spans[0][1] == 4  # First occurrence at position 4

        # Second mapping should get second occurrence
        result2 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result2.status == "MAPPED_EXACT"
        assert len(result2.spans) == 1
        assert result2.spans[0][1] == 39  # Second occurrence at position 39

    def test_exact_match_multiple_occurrences_all(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping with all_occurrences policy."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="all_occurrences")
        result = mapper.map_chunk("quick brown fox", document_id="doc2")

        assert result.status == "AMBIGUOUS"
        assert len(result.spans) == 2
        # Should find both occurrences
        assert result.spans[0][1] == 4
        assert result.spans[1][1] == 39

    def test_exact_match_multiple_occurrences_fail(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping with fail policy raises error on ambiguity."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="fail")

        with pytest.raises(AnchorResolutionError) as exc_info:
            mapper.map_chunk("quick brown fox", document_id="doc2")

        assert "Ambiguous chunk" in str(exc_info.value)
        assert "2 occurrences" in str(exc_info.value)

    def test_exact_match_across_documents(self, sample_docs: dict[str, Document]) -> None:
        """Test searching across all documents when document_id not specified."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("lazy dog")  # Only in doc1

        assert result.status == "MAPPED_EXACT"
        assert len(result.spans) == 1
        assert result.spans[0][0] == "doc1"

    def test_exact_match_no_document_id_multiple_docs(
        self, sample_docs: dict[str, Document]
    ) -> None:
        """Test mapping without document_id when chunk appears in multiple docs."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="all_occurrences")
        result = mapper.map_chunk("quick brown fox")  # In both doc1 and doc2

        assert result.status == "AMBIGUOUS"
        assert len(result.spans) >= 2  # At least one in doc1 and one in doc2

    def test_exact_match_unmapped(self, sample_docs: dict[str, Document]) -> None:
        """Test chunk that doesn't exist in any document."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("nonexistent text", document_id="doc1")

        assert result.status == "UNMAPPED"
        assert len(result.spans) == 0
        assert result.method == "no_match"

    def test_exact_match_document_not_found(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping with nonexistent document_id."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("some text", document_id="nonexistent")

        assert result.status == "UNMAPPED"
        assert result.method == "document_not_found"


class TestChunkMapperNormalizedMatching:
    """Test whitespace-normalized matching."""

    def test_normalized_match_extra_whitespace(self, sample_docs: dict[str, Document]) -> None:
        """Test matching with extra whitespace."""
        mapper = ChunkMapper(sample_docs)
        # Search for text with different whitespace than original
        result = mapper.map_chunk("Text  with extra whitespace", document_id="doc3")

        assert result.status == "MAPPED_NORMALIZED"
        assert len(result.spans) == 1
        assert result.method == "whitespace_normalized"
        # Verify it maps to the correct range in original text
        doc = sample_docs["doc3"]
        matched_text = doc.text[result.spans[0][1] : result.spans[0][2]]
        # Normalized versions should match
        assert matched_text.split() == "Text with extra whitespace".split()

    def test_normalized_match_tabs_and_newlines(self) -> None:
        """Test normalization handles tabs and newlines."""
        doc = Document.from_text("doc1", "Hello\t\tworld\ntest")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("Hello world test", document_id="doc1")

        assert result.status == "MAPPED_NORMALIZED"
        assert len(result.spans) == 1

    def test_normalized_match_leading_trailing_whitespace(
        self, sample_docs: dict[str, Document]
    ) -> None:
        """Test normalization handles leading/trailing whitespace."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("  quick brown fox  ", document_id="doc1")

        assert result.status == "MAPPED_EXACT" or result.status == "MAPPED_NORMALIZED"
        assert len(result.spans) == 1

    def test_normalized_fallback_after_exact_fails(self, sample_docs: dict[str, Document]) -> None:
        """Test that normalized matching is tried after exact matching fails."""
        mapper = ChunkMapper(sample_docs)
        # This won't match exactly due to extra spaces
        result = mapper.map_chunk("Text  with   extra    whitespace", document_id="doc3")

        assert result.status == "MAPPED_NORMALIZED"
        assert len(result.spans) == 1

    def test_normalized_match_multiple_occurrences(self) -> None:
        """Test normalized matching with ambiguity."""
        doc = Document.from_text("doc1", "Hello  world. Some text. Hello   world again.")
        mapper = ChunkMapper({"doc1": doc}, ambiguity_policy="all_occurrences")

        result = mapper.map_chunk("Hello world", document_id="doc1")

        # Should find both occurrences
        assert len(result.spans) == 2


class TestChunkMapperOffsetMapping:
    """Test offset mapping from normalized to original text."""

    def test_offset_map_preserves_boundaries(self) -> None:
        """Test that offset mapping preserves word boundaries."""
        doc = Document.from_text("doc1", "one   two   three")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("two", document_id="doc1")

        assert result.status == "MAPPED_EXACT"
        matched_text = doc.text[result.spans[0][1] : result.spans[0][2]]
        assert matched_text == "two"

    def test_offset_map_multi_word_phrase(self) -> None:
        """Test offset mapping for multi-word phrases."""
        doc = Document.from_text("doc1", "The   quick    brown   fox")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("quick brown fox", document_id="doc1")

        assert result.status == "MAPPED_NORMALIZED"
        matched_text = doc.text[result.spans[0][1] : result.spans[0][2]]
        # Should match the original (with extra spaces)
        assert "quick" in matched_text and "brown" in matched_text and "fox" in matched_text

    def test_offset_map_at_document_boundaries(self) -> None:
        """Test offset mapping at start and end of document."""
        doc = Document.from_text("doc1", "  start text  ")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("start text", document_id="doc1")

        # Should map (exact or normalized both are fine for this test)
        assert result.status in ["MAPPED_EXACT", "MAPPED_NORMALIZED"]
        assert len(result.spans) == 1


class TestChunkMapperClaimsTracking:
    """Test claimed spans tracking for first_unclaimed policy."""

    def test_reset_claims(self, sample_docs: dict[str, Document]) -> None:
        """Test that reset_claims clears the claimed spans."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="first_unclaimed")

        # Map a chunk
        result1 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result1.spans[0][1] == 4  # First occurrence

        # Reset claims
        mapper.reset_claims()

        # Should get first occurrence again
        result2 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result2.spans[0][1] == 4  # First occurrence again

    def test_claims_persist_across_different_chunks(self, sample_docs: dict[str, Document]) -> None:
        """Test that claims persist when mapping different chunks."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="first_unclaimed")

        # Map first chunk
        result1 = mapper.map_chunk("quick brown fox", document_id="doc2")
        first_span = result1.spans[0]

        # Map different chunk
        mapper.map_chunk("lazy dog", document_id="doc1")

        # Map same chunk again - should get second occurrence
        result2 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result2.spans[0] != first_span

    def test_all_claims_exhausted(self, sample_docs: dict[str, Document]) -> None:
        """Test behavior when all occurrences are claimed."""
        mapper = ChunkMapper(sample_docs, ambiguity_policy="first_unclaimed")

        # Claim both occurrences
        result1 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result1.status == "MAPPED_EXACT"

        result2 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result2.status == "MAPPED_EXACT"

        # Third attempt - all claimed
        result3 = mapper.map_chunk("quick brown fox", document_id="doc2")
        assert result3.status == "AMBIGUOUS"


class TestChunkMapperEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_chunk_text(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping empty string."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("", document_id="doc1")

        assert result.status == "UNMAPPED"

    def test_chunk_longer_than_document(self, sample_docs: dict[str, Document]) -> None:
        """Test chunk that is longer than any document."""
        mapper = ChunkMapper(sample_docs)
        very_long_chunk = "x" * 10000
        result = mapper.map_chunk(very_long_chunk, document_id="doc1")

        assert result.status == "UNMAPPED"

    def test_empty_documents_dict(self) -> None:
        """Test mapper with no documents."""
        mapper = ChunkMapper({})
        result = mapper.map_chunk("test", document_id="doc1")

        assert result.status == "UNMAPPED"
        assert result.method == "document_not_found"

    def test_chunk_with_only_whitespace(self, sample_docs: dict[str, Document]) -> None:
        """Test mapping chunk that is only whitespace."""
        mapper = ChunkMapper(sample_docs)
        result = mapper.map_chunk("   \t\n   ", document_id="doc1")

        assert result.status == "UNMAPPED"

    def test_special_characters_in_chunk(self) -> None:
        """Test chunks with special regex characters."""
        doc = Document.from_text("doc1", "Cost is $100. Pattern: [a-z]+")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("$100", document_id="doc1")
        assert result.status == "MAPPED_EXACT"

        result = mapper.map_chunk("[a-z]+", document_id="doc1")
        assert result.status == "MAPPED_EXACT"

    def test_unicode_characters(self) -> None:
        """Test mapping with Unicode characters."""
        doc = Document.from_text("doc1", "Café résumé 日本語 🎉")
        mapper = ChunkMapper({"doc1": doc})

        result = mapper.map_chunk("Café", document_id="doc1")
        assert result.status == "MAPPED_EXACT"

        result = mapper.map_chunk("日本語", document_id="doc1")
        assert result.status == "MAPPED_EXACT"

        result = mapper.map_chunk("🎉", document_id="doc1")
        assert result.status == "MAPPED_EXACT"

    def test_overlapping_matches(self) -> None:
        """Test handling of overlapping matches."""
        doc = Document.from_text("doc1", "aaaa")
        mapper = ChunkMapper({"doc1": doc}, ambiguity_policy="all_occurrences")

        result = mapper.map_chunk("aa", document_id="doc1")

        # Should find overlapping matches
        assert result.status == "AMBIGUOUS"
        assert len(result.spans) >= 2


class TestMappingResult:
    """Test MappingResult dataclass."""

    def test_mapping_result_creation(self) -> None:
        """Test creating MappingResult."""
        result = MappingResult(
            status="MAPPED_EXACT",
            spans=[("doc1", 0, 10)],
            method="exact_substring",
        )

        assert result.status == "MAPPED_EXACT"
        assert len(result.spans) == 1
        assert result.method == "exact_substring"

    def test_mapping_result_default_values(self) -> None:
        """Test MappingResult default values."""
        result = MappingResult(status="UNMAPPED")

        assert result.status == "UNMAPPED"
        assert result.spans == []
        assert result.method == "none"

    def test_mapping_result_frozen(self) -> None:
        """Test that MappingResult is immutable."""
        result = MappingResult(status="MAPPED_EXACT")

        with pytest.raises(AttributeError):
            result.status = "UNMAPPED"  # type: ignore


class TestChunkMapperIntegration:
    """Integration tests for complete mapping workflows."""

    def test_mixed_exact_and_normalized_mappings(self) -> None:
        """Test a query with both exact and normalized matches."""
        doc = Document.from_text("doc1", "Exact match. Extra  space  match.")
        mapper = ChunkMapper({"doc1": doc})

        # First chunk: exact match
        result1 = mapper.map_chunk("Exact match", document_id="doc1")
        assert result1.status == "MAPPED_EXACT"

        # Second chunk: normalized match
        result2 = mapper.map_chunk("Extra space match", document_id="doc1")
        assert result2.status == "MAPPED_NORMALIZED"

    def test_multi_document_query(self) -> None:
        """Test mapping chunks across multiple documents."""
        doc1 = Document.from_text("doc1", "Content in first document")
        doc2 = Document.from_text("doc2", "Content in second document")
        mapper = ChunkMapper({"doc1": doc1, "doc2": doc2})

        # Should find in doc1
        result1 = mapper.map_chunk("first document")
        assert result1.status == "MAPPED_EXACT"
        assert result1.spans[0][0] == "doc1"

        # Should find in doc2
        result2 = mapper.map_chunk("second document")
        assert result2.status == "MAPPED_EXACT"
        assert result2.spans[0][0] == "doc2"

    def test_full_retrieval_simulation(self) -> None:
        """Simulate a complete retrieval result mapping workflow."""
        # Create a corpus
        doc1 = Document.from_text("doc1", "The answer is 42.")
        doc2 = Document.from_text("doc2", "Another answer is also 42.")
        docs = {"doc1": doc1, "doc2": doc2}

        # Create mapper
        mapper = ChunkMapper(docs, ambiguity_policy="first_unclaimed")

        # Simulate retrieval results
        chunks = [
            ("answer is 42", "doc1"),  # Exact match
            ("answer is also 42", "doc2"),  # Exact match
            ("answer  is  42", None),  # Ambiguous, normalized
        ]

        results = []
        for chunk_text, doc_id in chunks:
            result = mapper.map_chunk(chunk_text, document_id=doc_id)
            results.append(result)

        # Verify results
        assert results[0].status == "MAPPED_EXACT"
        assert results[1].status == "MAPPED_EXACT"
        # Third one is ambiguous but should map to first unclaimed
        assert results[2].status in ["MAPPED_NORMALIZED", "AMBIGUOUS"]
