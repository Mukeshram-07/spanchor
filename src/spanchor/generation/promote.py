"""Explicit promotion of APPROVED candidates to gold Query + Anchor.

This module implements safe promotion of reviewed candidates into the existing
gold representation (Query + Anchor). Promotion is explicit and only allowed
for APPROVED candidates with valid metadata.

**Feature 7: Semi-Automated Gold-Set Generation**
"""

from uuid import uuid4

from spanchor.canonical.normalize import compute_hash
from spanchor.models.anchor import Anchor
from spanchor.models.candidate import Candidate, CandidateStatus
from spanchor.models.query import Query


def promote_candidate_to_gold(
    candidate: Candidate,
) -> tuple[Query, Anchor]:
    """Promote an APPROVED candidate to Query + Anchor.

    Converts an approved candidate with human review metadata into a gold
    Query + Anchor pair. This is an explicit operation that must be called
    by the user/CLI - candidates are never silently promoted.

    Safety invariants enforced:
    - PENDING candidates cannot be promoted (must be explicitly approved first)
    - REJECTED candidates cannot be promoted (explicitly rejected)
    - EDITED but PENDING candidates cannot be promoted (must be approved after editing)
    - APPROVED + valid anchor metadata can be promoted
    - APPROVED + missing human_question blocks promotion
    - APPROVED + invalid source span blocks promotion
    - APPROVED + missing source anchor blocks promotion

    Args:
        candidate: Candidate to promote (must be APPROVED with valid review metadata)

    Returns:
        Tuple of (Query, Anchor) where:
        - Query has query_id, question from human_question, and tuple containing single Anchor
        - Anchor has document_id, start/end from source span, and expected_text_hash

    Raises:
        ValueError: If candidate is not APPROVED or has invalid/missing metadata.
            Error message clearly indicates which safety invariant was violated.

    Examples:
        >>> from spanchor.models.candidate import Candidate, CandidateReview, CandidateStatus
        >>> review = CandidateReview(
        ...     status=CandidateStatus.APPROVED,
        ...     human_question="What is the capital?",
        ...     source_start=0,
        ...     source_end=15,
        ... )
        >>> candidate = Candidate(
        ...     candidate_id="doc1_0",
        ...     text="Original text",
        ...     document_id="doc1",
        ...     confidence=1.0,
        ...     review=review,
        ... )
        >>> query, anchor = promote_candidate_to_gold(candidate)
        >>> query.query_id  # auto-generated UUID-like ID
        'query_...'
        >>> query.question
        'What is the capital?'
        >>> anchor.document_id
        'doc1'

    **Validates: Feature 7 - Explicit candidate promotion**
    """
    # Check 1: Status must be APPROVED
    if candidate.review is None:
        raise ValueError(
            "Cannot promote PENDING candidate: review metadata required (must be APPROVED)"
        )

    if candidate.status == CandidateStatus.PENDING:
        raise ValueError(
            "Cannot promote PENDING candidate: must be explicitly approved before promotion"
        )

    if candidate.status == CandidateStatus.REJECTED:
        raise ValueError("Cannot promote REJECTED candidate: explicitly rejected during review")

    # Check 2: Human question must be present and non-empty
    if candidate.review.human_question is None:
        raise ValueError(
            "Cannot promote APPROVED candidate: missing human_question required for gold query"
        )

    human_question = candidate.review.human_question.strip()
    if not human_question:
        raise ValueError(
            "Cannot promote APPROVED candidate: human_question cannot be empty or whitespace-only"
        )

    # Check 3: Source anchor metadata must be valid
    if candidate.review.source_start is None or candidate.review.source_end is None:
        raise ValueError(
            "Cannot promote APPROVED candidate: missing source_start or "
            "source_end (required for anchor)"
        )

    source_start = candidate.review.source_start
    source_end = candidate.review.source_end

    # Validate source span bounds
    if source_start < 0:
        raise ValueError(
            f"Cannot promote APPROVED candidate: invalid source_start={source_start} (must be >= 0)"
        )

    if source_start >= source_end:
        raise ValueError(
            f"Cannot promote APPROVED candidate: invalid source span "
            f"[start={source_start}, end={source_end}] "
            f"(start must be < end)"
        )

    # Check 4: Document ID must be valid
    if not candidate.document_id or not candidate.document_id.strip():
        raise ValueError("Cannot promote APPROVED candidate: invalid document_id")

    # All safety checks passed - create Query + Anchor
    # Generate unique IDs
    query_id = f"query_{uuid4().hex[:8]}"

    # Create Anchor from source span
    # Note: expected_text_hash cannot be computed without access to the source document
    # For now, we use a placeholder hash. In a real system, the caller would provide the
    # actual document text or we'd need access to the document store.
    # The hash will be populated when validation occurs.
    # For promotion, we'll use the candidate text as best effort:
    expected_text_hash = compute_hash(candidate.review.edited_text or candidate.text)

    anchor = Anchor(
        document_id=candidate.document_id,
        start=source_start,
        end=source_end,
        expected_text_hash=expected_text_hash,
        schema_version="0.1.0",
    )

    # Create Query with the promoted anchor
    query = Query(
        query_id=query_id,
        question=human_question,
        anchors=(anchor,),
        schema_version="0.1.0",
        candidate_id=candidate.candidate_id,
    )

    return query, anchor
