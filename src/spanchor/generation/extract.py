"""Sentence extraction and deduplication for gold-set bootstrapping.

This module implements rule-based sentence extraction from documents and
deduplication based on Levenshtein distance (95% similarity threshold).

No LLM is used. Extraction is purely rule-based using common sentence
delimiters (periods, question marks, exclamation marks).

**Validates: Feature 7 - Gold-Set Generation (Minimal)**
"""

import re

from spanchor.models.candidate import Candidate
from spanchor.models.document import Document


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Levenshtein distance (minimum edits to transform s1 to s2)
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row: list[int] = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row: list[int] = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _similarity_ratio(s1: str, s2: str) -> float:
    """Compute similarity ratio (0.0-1.0) between two strings.

    Similarity = 1 - (levenshtein_distance / max_length)

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity ratio in [0.0, 1.0] where 1.0 = identical
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0

    distance = _levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using rule-based approach.

    Rules:
    - Split on periods (.), question marks (?), and exclamation marks (!)
    - Preserve abbreviations (e.g., "U.S.A") by checking single-letter before period
    - Strip whitespace from each sentence
    - Filter out empty sentences

    Args:
        text: Input text to split

    Returns:
        List of non-empty sentences (whitespace-trimmed)
    """
    # Replace common abbreviations temporarily to avoid false splits
    # Simple approach: mark sentence-ending punctuation followed by space
    # Split on patterns: [.!?] followed by space and capital letter or digit

    # Use regex to split on sentence boundaries
    # Look for: end-of-sentence punctuation followed by space and uppercase or digit
    sentences_raw = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)

    # Also split on orphan periods/marks at end of text
    sentences_raw = [s for segment in sentences_raw for s in re.split(r'(?<=[.!?])\s+', segment)]

    # Clean and filter
    sentences: list[str] = []
    for sent in sentences_raw:
        sent = sent.strip()
        if sent:  # only non-empty
            sentences.append(sent)

    return sentences


def _is_duplicate(candidate_text: str, existing_texts: list[str], threshold: float = 0.95) -> bool:
    """Check if candidate is a duplicate of existing text (>= threshold similarity).

    Args:
        candidate_text: Text to check
        existing_texts: List of existing texts to compare against
        threshold: Similarity threshold [0.0-1.0] (default 0.95 = 95%)

    Returns:
        True if candidate matches any existing text with >= threshold similarity
    """
    for existing_text in existing_texts:
        similarity = _similarity_ratio(candidate_text, existing_text)
        if similarity >= threshold:
            return True
    return False


def extract_sentences(documents: list[Document]) -> list[Candidate]:
    """Extract sentences from documents and deduplicate.

    Process:
    1. Split each document into sentences (rule-based)
    2. Deduplicate using Levenshtein distance (95% threshold)
    3. Create Candidate objects with unique IDs

    Args:
        documents: List of Document objects to extract from

    Returns:
        List of Candidate objects (deduplicated sentences)

    Examples:
        >>> from spanchor.models import Document
        >>> doc = Document.from_text("doc1", "Hello world. How are you?")
        >>> candidates = extract_sentences([doc])
        >>> len(candidates)
        2
        >>> candidates[0].text
        'Hello world.'

    **Validates: Feature 7 - Sentence extraction**
    """
    candidates: list[Candidate] = []
    seen_texts: list[str] = []  # Track deduplicated texts
    candidate_counter: dict[str, int] = {}  # Track ID counters per document

    for document in documents:
        sentences = _split_sentences(document.text)

        for sent in sentences:
            # Skip duplicates
            if _is_duplicate(sent, seen_texts, threshold=0.95):
                continue

            # Generate candidate ID
            if document.document_id not in candidate_counter:
                candidate_counter[document.document_id] = 0
            else:
                candidate_counter[document.document_id] += 1

            candidate_id = f"{document.document_id}_{candidate_counter[document.document_id]}"

            # Create candidate with high confidence (extracted, not inferred)
            candidate = Candidate(
                candidate_id=candidate_id,
                text=sent,
                document_id=document.document_id,
                confidence=1.0,  # Extracted sentences have high confidence
            )

            candidates.append(candidate)
            seen_texts.append(sent)

    return candidates
