"""Candidate model for gold-set bootstrapping.

A Candidate represents an extracted sentence from a document that may become
part of the gold set after user review. Candidates are generated from documents
through sentence extraction and deduplication, then reviewed by humans.

**Feature 7: Semi-Automated Gold-Set Generation**
"""

from dataclasses import dataclass
from enum import Enum


class CandidateStatus(str, Enum):
    """Status of a candidate in the review workflow.

    PENDING: Candidate extracted, awaiting human review.
    APPROVED: Candidate reviewed and approved by human.
    REJECTED: Candidate reviewed and rejected by human.

    Note: EDITED is not a terminal state. Editing keeps candidate PENDING
    until explicitly approved.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class CandidateReview:
    """Review metadata for an approved/rejected candidate.

    Attributes:
        status: Current review status (PENDING/APPROVED/REJECTED)
        human_question: The evaluation question created by human (required for APPROVED)
        source_start: Start offset of source evidence in document (required)
        source_end: End offset of source evidence in document (required)
        edited_text: If candidate text was edited by human, the edited version
        was_edited: True if candidate text was edited before approval
        rejection_reason: Optional reason for rejection
    """

    status: CandidateStatus
    human_question: str | None = None
    source_start: int | None = None
    source_end: int | None = None
    edited_text: str | None = None
    was_edited: bool = False
    rejection_reason: str | None = None

    def __post_init__(self) -> None:
        """Validate review fields."""
        # APPROVED requires question
        if self.status == CandidateStatus.APPROVED and not self.human_question:
            raise ValueError("Approved candidate must have human_question")

        # APPROVED requires source span
        if self.status == CandidateStatus.APPROVED:
            if self.source_start is None or self.source_end is None:
                raise ValueError("Approved candidate must have source_start and source_end")
            if not (0 <= self.source_start < self.source_end):
                raise ValueError("Invalid source span: start must be >= 0 and < end")

        # Validate human_question if provided
        if self.human_question is not None and not self.human_question.strip():
            raise ValueError("human_question cannot be empty or whitespace-only")

        # Validate edited_text if provided
        if self.edited_text is not None and not self.edited_text.strip():
            raise ValueError("edited_text cannot be empty or whitespace-only")


@dataclass(frozen=True, slots=True)
class Candidate:
    """Extracted sentence candidate for gold-set bootstrapping.

    Candidates are sentences extracted from source documents and deduplicated.
    They represent potential annotation points that users can review and turn into
    gold-set anchors.

    Attributes:
        candidate_id: Unique identifier for this candidate (e.g., "doc1_0")
        text: The original candidate text (sentence)
        document_id: Unique identifier of the source document
        confidence: Confidence score [0.0-1.0] (1.0 for extracted sentences)
        review: Optional CandidateReview metadata (added during human review)
        schema_version: Schema version for forward compatibility
    """

    candidate_id: str
    text: str
    document_id: str
    confidence: float
    review: CandidateReview | None = None
    schema_version: str = "0.2.0"

    def __post_init__(self) -> None:
        """Validate candidate fields."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence must be in [0.0, 1.0], got {self.confidence}"
            )

        if not self.text.strip():
            raise ValueError("text cannot be empty or whitespace-only")

        if not self.candidate_id.strip():
            raise ValueError("candidate_id cannot be empty or whitespace-only")

        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty or whitespace-only")

    @property
    def status(self) -> CandidateStatus:
        """Get current status of candidate."""
        if self.review is None:
            return CandidateStatus.PENDING
        return self.review.status
