"""Unit tests for sentence extraction and deduplication.

Tests cover:
- Sentence extraction from documents (rule-based)
- Deduplication using Levenshtein distance (95% threshold)
- Output format (Candidate objects with valid IDs)
- Edge cases (empty documents, single sentence, many duplicates)

**Validates: Feature 7 - Gold-Set Generation (Minimal)**
"""

import pytest

from spanchor.generation.extract import (
    _is_duplicate,
    _levenshtein_distance,
    _similarity_ratio,
    _split_sentences,
    extract_sentences,
)
from spanchor.models.candidate import Candidate
from spanchor.models.document import Document


class TestLevenshteinDistance:
    """Tests for Levenshtein distance calculation."""

    def test_identical_strings(self) -> None:
        """Identical strings have distance 0."""
        assert _levenshtein_distance("hello", "hello") == 0

    def test_empty_string(self) -> None:
        """Distance from empty to non-empty is string length."""
        assert _levenshtein_distance("", "hello") == 5
        assert _levenshtein_distance("hello", "") == 5

    def test_both_empty(self) -> None:
        """Distance between two empty strings is 0."""
        assert _levenshtein_distance("", "") == 0

    def test_single_substitution(self) -> None:
        """One character difference has distance 1."""
        assert _levenshtein_distance("cat", "bat") == 1

    def test_insertion(self) -> None:
        """Insertion requires distance 1."""
        assert _levenshtein_distance("cat", "cats") == 1

    def test_deletion(self) -> None:
        """Deletion requires distance 1."""
        assert _levenshtein_distance("cats", "cat") == 1

    def test_completely_different(self) -> None:
        """Completely different strings have high distance."""
        assert _levenshtein_distance("abc", "xyz") == 3


class TestSimilarityRatio:
    """Tests for similarity ratio calculation."""

    def test_identical_strings(self) -> None:
        """Identical strings have ratio 1.0."""
        assert _similarity_ratio("hello", "hello") == 1.0

    def test_empty_strings(self) -> None:
        """Two empty strings have ratio 1.0."""
        assert _similarity_ratio("", "") == 1.0

    def test_one_empty(self) -> None:
        """One empty, one non-empty has ratio 0.0."""
        assert _similarity_ratio("", "hello") == 0.0
        assert _similarity_ratio("hello", "") == 0.0

    def test_high_similarity(self) -> None:
        """Similar strings have high ratio."""
        # "hello" vs "hallo" (1 substitution, len=5, ratio=1-1/5=0.8)
        ratio = _similarity_ratio("hello", "hallo")
        assert 0.79 < ratio < 0.81  # ~0.8

    def test_95_percent_threshold(self) -> None:
        """95% similarity means 5% difference."""
        # For a 100-char string, 5 edits = 95% similarity
        s1 = "a" * 100
        s2 = "a" * 95 + "b" * 5
        ratio = _similarity_ratio(s1, s2)
        assert ratio >= 0.95


class TestSplitSentences:
    """Tests for rule-based sentence splitting."""

    def test_split_on_period(self) -> None:
        """Split on period followed by space and uppercase."""
        sentences = _split_sentences("Hello world. How are you?")
        assert len(sentences) == 2
        assert sentences[0] == "Hello world."
        assert sentences[1] == "How are you?"

    def test_split_on_question_mark(self) -> None:
        """Split on question mark followed by space and uppercase."""
        sentences = _split_sentences("Who are you? I am fine.")
        assert len(sentences) == 2
        assert sentences[0] == "Who are you?"
        assert sentences[1] == "I am fine."

    def test_split_on_exclamation(self) -> None:
        """Split on exclamation mark followed by space and uppercase."""
        sentences = _split_sentences("Great job! Well done.")
        assert len(sentences) == 2
        assert sentences[0] == "Great job!"
        assert sentences[1] == "Well done."

    def test_single_sentence_no_split(self) -> None:
        """Single sentence without end punctuation stays intact."""
        sentences = _split_sentences("Hello world")
        assert len(sentences) == 1
        assert sentences[0] == "Hello world"

    def test_empty_string(self) -> None:
        """Empty string produces empty list."""
        sentences = _split_sentences("")
        assert len(sentences) == 0

    def test_trailing_whitespace_stripped(self) -> None:
        """Trailing/leading whitespace is stripped."""
        sentences = _split_sentences("  Hello world.  How are you?  ")
        assert len(sentences) == 2
        assert sentences[0] == "Hello world."
        assert sentences[1] == "How are you?"

    def test_multiple_spaces_between_sentences(self) -> None:
        """Multiple spaces between sentences handled correctly."""
        sentences = _split_sentences("Hello.  World.")
        assert len(sentences) == 2
        assert sentences[0] == "Hello."
        assert sentences[1] == "World."

    def test_paragraph_with_multiple_sentences(self) -> None:
        """Multi-sentence paragraph splits correctly."""
        text = "This is a test. It has multiple sentences. They should split properly."
        sentences = _split_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "This is a test."
        assert sentences[1] == "It has multiple sentences."
        assert sentences[2] == "They should split properly."


class TestIsDuplicate:
    """Tests for duplicate detection using Levenshtein distance."""

    def test_exact_duplicate(self) -> None:
        """Exact match is detected as duplicate."""
        existing = ["Hello world", "How are you"]
        assert _is_duplicate("Hello world", existing, threshold=0.95) is True

    def test_no_duplicates(self) -> None:
        """Completely different text is not a duplicate."""
        existing = ["Hello world", "How are you"]
        assert _is_duplicate("Goodbye", existing, threshold=0.95) is False

    def test_95_percent_similar_is_duplicate(self) -> None:
        """95% similar text is detected as duplicate."""
        existing = ["a" * 100]
        candidate = "a" * 95 + "b" * 5  # 95% similar
        assert _is_duplicate(candidate, existing, threshold=0.95) is True

    def test_94_percent_similar_not_duplicate(self) -> None:
        """94% similar text is not detected as duplicate (threshold=0.95)."""
        existing = ["a" * 100]
        candidate = "a" * 94 + "b" * 6  # ~94% similar
        assert _is_duplicate(candidate, existing, threshold=0.95) is False

    def test_empty_existing_list(self) -> None:
        """Empty existing list means no duplicates."""
        assert _is_duplicate("Hello", [], threshold=0.95) is False

    def test_threshold_parameter(self) -> None:
        """Threshold parameter affects duplicate detection."""
        existing = ["a" * 100]
        candidate = "a" * 90 + "b" * 10  # 90% similar

        # At 90% threshold, it's a duplicate
        assert _is_duplicate(candidate, existing, threshold=0.90) is True

        # At 95% threshold, it's not a duplicate
        assert _is_duplicate(candidate, existing, threshold=0.95) is False


class TestExtractSentences:
    """Tests for sentence extraction and deduplication."""

    def test_extract_from_single_document(self) -> None:
        """Extract sentences from a single document."""
        doc = Document.from_text("doc1", "Hello world. How are you?")
        candidates = extract_sentences([doc])

        assert len(candidates) == 2
        assert candidates[0].text == "Hello world."
        assert candidates[1].text == "How are you?"

    def test_candidate_structure(self) -> None:
        """Extracted candidates have correct structure."""
        doc = Document.from_text("doc1", "Hello world. How are you?")
        candidates = extract_sentences([doc])

        candidate = candidates[0]
        assert isinstance(candidate, Candidate)
        assert candidate.candidate_id == "doc1_0"
        assert candidate.document_id == "doc1"
        assert candidate.confidence == 1.0
        assert candidate.schema_version == "0.2.0"

    def test_candidate_id_increments(self) -> None:
        """Candidate IDs increment per document."""
        doc = Document.from_text("doc1", "First. Second. Third.")
        candidates = extract_sentences([doc])

        assert candidates[0].candidate_id == "doc1_0"
        assert candidates[1].candidate_id == "doc1_1"
        assert candidates[2].candidate_id == "doc1_2"

    def test_deduplication_removes_near_duplicates(self) -> None:
        """Deduplication removes sentences with >95% similarity."""
        # Create a document with nearly identical sentences
        text = "This is a test sentence. This is a test sentense."  # typo in second
        doc = Document.from_text("doc1", text)
        candidates = extract_sentences([doc])

        # Should only extract the first one (second is duplicate)
        assert len(candidates) == 1
        assert candidates[0].text == "This is a test sentence."

    def test_multiple_documents(self) -> None:
        """Extract from multiple documents."""
        doc1 = Document.from_text("doc1", "Hello. World.")
        doc2 = Document.from_text("doc2", "Goodbye. See you.")
        candidates = extract_sentences([doc1, doc2])

        assert len(candidates) == 4
        assert candidates[0].document_id == "doc1"
        assert candidates[1].document_id == "doc1"
        assert candidates[2].document_id == "doc2"
        assert candidates[3].document_id == "doc2"

    def test_empty_document_list(self) -> None:
        """Empty document list produces empty candidates."""
        candidates = extract_sentences([])
        assert len(candidates) == 0

    def test_document_with_no_sentences(self) -> None:
        """Document without sentence boundaries produces single entry."""
        doc = Document.from_text("doc1", "Hello world")
        candidates = extract_sentences([doc])

        assert len(candidates) == 1
        assert candidates[0].text == "Hello world"

    def test_global_deduplication_across_documents(self) -> None:
        """Deduplication works across multiple documents."""
        doc1 = Document.from_text("doc1", "Hello world. Goodbye.")
        doc2 = Document.from_text("doc2", "Hello world. See you.")  # duplicate from doc1
        candidates = extract_sentences([doc1, doc2])

        # Only 3 unique sentences
        assert len(candidates) == 3
        # First two from doc1, third from doc2
        assert candidates[0].document_id == "doc1"
        assert candidates[1].document_id == "doc1"
        assert candidates[2].document_id == "doc2"
        assert candidates[2].text == "See you."

    def test_realistic_document(self) -> None:
        """Extract from realistic multi-sentence document."""
        text = (
            "Retrieval-Augmented Generation (RAG) is a technique that enhances "
            "large language model outputs by grounding them in retrieved source documents. "
            "Instead of relying solely on parametric knowledge baked into model weights, "
            "RAG pipelines fetch relevant passages at inference time and pass them as context to the model. "
            "This approach reduces hallucinations and keeps answers up to date without retraining."
        )
        doc = Document.from_text("rag_intro", text)
        candidates = extract_sentences([doc])

        # Should extract multiple sentences
        assert len(candidates) > 0
        # Each candidate should be non-empty
        for candidate in candidates:
            assert len(candidate.text) > 0
            assert candidate.document_id == "rag_intro"

    def test_confidence_always_one_for_extracted(self) -> None:
        """Extracted sentences have confidence=1.0."""
        doc = Document.from_text("doc1", "First sentence. Second sentence.")
        candidates = extract_sentences([doc])

        for candidate in candidates:
            assert candidate.confidence == 1.0


class TestCandidateValidation:
    """Tests for Candidate dataclass validation."""

    def test_candidate_creation(self) -> None:
        """Candidate can be created with valid data."""
        candidate = Candidate(
            candidate_id="doc1_0",
            text="Hello world",
            document_id="doc1",
            confidence=0.9,
        )
        assert candidate.candidate_id == "doc1_0"

    def test_candidate_confidence_validation(self) -> None:
        """Confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValueError, match="confidence must be in"):
            Candidate(
                candidate_id="doc1_0",
                text="Hello",
                document_id="doc1",
                confidence=1.5,
            )

        with pytest.raises(ValueError, match="confidence must be in"):
            Candidate(
                candidate_id="doc1_0",
                text="Hello",
                document_id="doc1",
                confidence=-0.1,
            )

    def test_candidate_empty_text_validation(self) -> None:
        """Text cannot be empty."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            Candidate(
                candidate_id="doc1_0",
                text="",
                document_id="doc1",
                confidence=1.0,
            )

        with pytest.raises(ValueError, match="text cannot be empty"):
            Candidate(
                candidate_id="doc1_0",
                text="   ",
                document_id="doc1",
                confidence=1.0,
            )

    def test_candidate_frozen(self) -> None:
        """Candidate is immutable."""
        candidate = Candidate(
            candidate_id="doc1_0",
            text="Hello",
            document_id="doc1",
            confidence=1.0,
        )

        with pytest.raises(AttributeError):
            candidate.text = "Modified"  # type: ignore
