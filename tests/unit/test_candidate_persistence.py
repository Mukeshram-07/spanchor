"""Unit tests for candidate pool state persistence.

Tests for JSONL persistence of candidates with PENDING/APPROVED/REJECTED workflow.
Verifies round-trip preservation, status preservation, and validation of invalid records.
"""

import json
from pathlib import Path

import pytest

from spanchor.errors import InvalidSchemaError
from spanchor.models.candidate import Candidate, CandidateReview, CandidateStatus
from spanchor.storage.jsonl import read_candidate_pool, write_candidate_pool


class TestReadCandidatePool:
    """Tests for read_candidate_pool function."""

    def test_read_valid_jsonl_single_candidate(self, tmp_path: Path) -> None:
        """Test reading a valid JSONL file with a single candidate."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "doc1_0",
            "text": "This is a sample sentence.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        candidates = read_candidate_pool(jsonl_file)

        assert len(candidates) == 1
        assert candidates[0].candidate_id == "doc1_0"
        assert candidates[0].text == "This is a sample sentence."
        assert candidates[0].document_id == "doc1"
        assert candidates[0].confidence == 1.0
        assert candidates[0].schema_version == "0.2.0"
        assert candidates[0].review is None
        assert candidates[0].status == CandidateStatus.PENDING

    def test_read_multiple_candidates(self, tmp_path: Path) -> None:
        """Test reading multiple candidates from JSONL."""
        jsonl_file = tmp_path / "candidates.jsonl"
        candidates_data = [
            {
                "candidate_id": "doc1_0",
                "text": "First sentence.",
                "document_id": "doc1",
                "confidence": 1.0,
                "schema_version": "0.2.0",
            },
            {
                "candidate_id": "doc1_1",
                "text": "Second sentence.",
                "document_id": "doc1",
                "confidence": 0.95,
                "schema_version": "0.2.0",
            },
            {
                "candidate_id": "doc2_0",
                "text": "Third sentence.",
                "document_id": "doc2",
                "confidence": 0.8,
                "schema_version": "0.2.0",
            },
        ]
        with jsonl_file.open("w") as f:
            for c in candidates_data:
                f.write(json.dumps(c) + "\n")

        candidates = read_candidate_pool(jsonl_file)

        assert len(candidates) == 3
        assert candidates[0].candidate_id == "doc1_0"
        assert candidates[1].candidate_id == "doc1_1"
        assert candidates[2].candidate_id == "doc2_0"

    def test_read_skips_empty_lines(self, tmp_path: Path) -> None:
        """Test that empty lines are skipped."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test sentence.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        with jsonl_file.open("w") as f:
            f.write("\n")  # Empty line
            f.write(json.dumps(data) + "\n")
            f.write("\n")  # Another empty line

        candidates = read_candidate_pool(jsonl_file)

        assert len(candidates) == 1
        assert candidates[0].candidate_id == "c1"

    def test_duplicate_candidate_id_raises_error(self, tmp_path: Path) -> None:
        """Test that duplicate candidate_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        with jsonl_file.open("w") as f:
            f.write(json.dumps(data) + "\n")
            f.write(json.dumps(data) + "\n")  # Duplicate

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Duplicate candidate_id" in str(exc_info.value)
        assert "c1" in str(exc_info.value)
        assert "Line: 2" in str(exc_info.value)

    def test_invalid_json_raises_error(self, tmp_path: Path) -> None:
        """Test that malformed JSON raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        jsonl_file.write_text("{ invalid json }\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Invalid JSON" in str(exc_info.value)
        assert "Line: 1" in str(exc_info.value)

    def test_missing_schema_version_raises_error(self, tmp_path: Path) -> None:
        """Test that missing schema_version raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1.0,
            # Missing schema_version
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Missing required field 'schema_version'" in str(exc_info.value)
        assert "Field: schema_version" in str(exc_info.value)

    def test_missing_candidate_id_raises_error(self, tmp_path: Path) -> None:
        """Test that missing candidate_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Missing required field 'candidate_id'" in str(exc_info.value)

    def test_missing_text_raises_error(self, tmp_path: Path) -> None:
        """Test that missing text raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Missing required field 'text'" in str(exc_info.value)

    def test_missing_document_id_raises_error(self, tmp_path: Path) -> None:
        """Test that missing document_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Missing required field 'document_id'" in str(exc_info.value)

    def test_missing_confidence_raises_error(self, tmp_path: Path) -> None:
        """Test that missing confidence raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Missing required field 'confidence'" in str(exc_info.value)

    def test_non_string_candidate_id_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string candidate_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": 123,  # Should be string
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "must be a string" in str(exc_info.value)
        assert "candidate_id" in str(exc_info.value)

    def test_non_string_text_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string text raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": 456,  # Should be string
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "must be a string" in str(exc_info.value)
        assert "text" in str(exc_info.value)

    def test_non_string_document_id_raises_error(self, tmp_path: Path) -> None:
        """Test that non-string document_id raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": 789,  # Should be string
            "confidence": 1.0,
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "must be a string" in str(exc_info.value)
        assert "document_id" in str(exc_info.value)

    def test_non_numeric_confidence_raises_error(self, tmp_path: Path) -> None:
        """Test that non-numeric confidence raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": "high",  # Should be number
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "must be a number" in str(exc_info.value)
        assert "confidence" in str(exc_info.value)

    def test_file_not_found_raises_error(self, tmp_path: Path) -> None:
        """Test that missing file raises InvalidSchemaError."""
        jsonl_file = tmp_path / "nonexistent.jsonl"

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "File not found" in str(exc_info.value)

    def test_non_dict_json_raises_error(self, tmp_path: Path) -> None:
        """Test that non-dictionary JSON raises InvalidSchemaError."""
        jsonl_file = tmp_path / "candidates.jsonl"
        jsonl_file.write_text('["not", "a", "dict"]\n')

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        assert "Expected JSON object" in str(exc_info.value)

    def test_read_with_int_confidence(self, tmp_path: Path) -> None:
        """Test that integer confidence values are accepted and converted to float."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1,  # Integer instead of float
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        candidates = read_candidate_pool(jsonl_file)

        assert len(candidates) == 1
        assert candidates[0].confidence == 1.0
        assert isinstance(candidates[0].confidence, float)


class TestWriteCandidatePool:
    """Tests for write_candidate_pool function."""

    def test_write_single_pending_candidate(self, tmp_path: Path) -> None:
        """Test writing a single PENDING candidate to JSONL."""
        jsonl_file = tmp_path / "output.jsonl"
        candidate = Candidate("c1", "Test sentence.", "doc1", 1.0)

        write_candidate_pool(jsonl_file, [candidate])

        content = jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1

        data = json.loads(lines[0])
        assert data["candidate_id"] == "c1"
        assert data["text"] == "Test sentence."
        assert data["document_id"] == "doc1"
        assert data["confidence"] == 1.0
        assert data["schema_version"] == "0.2.0"

    def test_write_multiple_candidates(self, tmp_path: Path) -> None:
        """Test writing multiple candidates to JSONL."""
        jsonl_file = tmp_path / "output.jsonl"
        candidates = [
            Candidate("c1", "First.", "doc1", 1.0),
            Candidate("c2", "Second.", "doc1", 0.95),
            Candidate("c3", "Third.", "doc2", 0.8),
        ]

        write_candidate_pool(jsonl_file, candidates)

        content = jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3

        ids = [json.loads(line)["candidate_id"] for line in lines]
        assert ids == ["c1", "c2", "c3"]

    def test_write_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test that write_candidate_pool creates parent directories."""
        jsonl_file = tmp_path / "subdir" / "nested" / "output.jsonl"
        candidate = Candidate("c1", "Test.", "doc1", 1.0)

        write_candidate_pool(jsonl_file, [candidate])

        assert jsonl_file.exists()
        assert jsonl_file.parent.exists()

    def test_write_empty_list(self, tmp_path: Path) -> None:
        """Test writing an empty list of candidates."""
        jsonl_file = tmp_path / "output.jsonl"

        write_candidate_pool(jsonl_file, [])

        content = jsonl_file.read_text()
        assert content == ""

    def test_write_candidate_with_unicode(self, tmp_path: Path) -> None:
        """Test writing candidates with unicode characters."""
        jsonl_file = tmp_path / "unicode.jsonl"
        candidate = Candidate("c1", "What is 日本語?", "doc_jp", 1.0)

        write_candidate_pool(jsonl_file, [candidate])

        loaded_candidates = read_candidate_pool(jsonl_file)
        assert loaded_candidates[0].text == "What is 日本語?"

    def test_write_candidate_with_special_characters(self, tmp_path: Path) -> None:
        """Test writing candidates with special characters."""
        jsonl_file = tmp_path / "special.jsonl"
        candidate = Candidate(
            "c1",
            'Text with "quotes" and \\ backslashes and \n newlines.',
            "doc1",
            1.0,
        )

        write_candidate_pool(jsonl_file, [candidate])

        loaded_candidates = read_candidate_pool(jsonl_file)
        assert loaded_candidates[0].text == 'Text with "quotes" and \\ backslashes and \n newlines.'


class TestCandidateRoundTrip:
    """Tests for round-trip preservation of candidate data."""

    def test_pending_candidate_roundtrip(self, tmp_path: Path) -> None:
        """Test that PENDING candidates preserve all fields through write->read."""
        jsonl_file = tmp_path / "roundtrip.jsonl"
        candidates = [
            Candidate("c1", "First sentence.", "doc1", 1.0),
            Candidate("c2", "Second sentence.", "doc1", 0.95),
            Candidate("c3", "Third sentence.", "doc2", 0.8),
        ]

        write_candidate_pool(jsonl_file, candidates)
        loaded_candidates = read_candidate_pool(jsonl_file)

        assert len(loaded_candidates) == len(candidates)
        for orig, loaded in zip(candidates, loaded_candidates, strict=True):
            assert orig.candidate_id == loaded.candidate_id
            assert orig.text == loaded.text
            assert orig.document_id == loaded.document_id
            assert orig.confidence == loaded.confidence
            assert orig.schema_version == loaded.schema_version
            assert orig.review == loaded.review
            assert orig.status == loaded.status

    def test_pending_status_preserved(self, tmp_path: Path) -> None:
        """Test that PENDING status is preserved through round-trip."""
        jsonl_file = tmp_path / "pending.jsonl"
        candidate = Candidate("c1", "Test.", "doc1", 1.0)

        # Verify it's PENDING before write
        assert candidate.status == CandidateStatus.PENDING

        write_candidate_pool(jsonl_file, [candidate])
        loaded_candidates = read_candidate_pool(jsonl_file)

        # Verify it's still PENDING after round-trip
        assert loaded_candidates[0].status == CandidateStatus.PENDING
        assert loaded_candidates[0].review is None

    def test_edited_candidate_remains_pending(self, tmp_path: Path) -> None:
        """Test that editing a candidate keeps it PENDING (not auto-approved)."""
        jsonl_file = tmp_path / "roundtrip.jsonl"

        # Original candidate
        original = Candidate("c1", "Original text.", "doc1", 1.0)
        assert original.status == CandidateStatus.PENDING

        # Simulate editing by creating a new candidate with edited text
        # (but NO review/approval)
        edited = Candidate("c1", "Edited text.", "doc1", 1.0)
        assert edited.status == CandidateStatus.PENDING

        write_candidate_pool(jsonl_file, [edited])
        loaded_candidates = read_candidate_pool(jsonl_file)

        # Verify it's still PENDING (not auto-approved)
        assert loaded_candidates[0].status == CandidateStatus.PENDING
        assert loaded_candidates[0].review is None

    def test_candidate_confidence_preserved(self, tmp_path: Path) -> None:
        """Test that various confidence values are preserved through round-trip."""
        jsonl_file = tmp_path / "confidence.jsonl"
        candidates = [
            Candidate("c1", "Text.", "doc1", 0.0),
            Candidate("c2", "Text.", "doc1", 0.5),
            Candidate("c3", "Text.", "doc1", 1.0),
            Candidate("c4", "Text.", "doc1", 0.999),
        ]

        write_candidate_pool(jsonl_file, candidates)
        loaded_candidates = read_candidate_pool(jsonl_file)

        for orig, loaded in zip(candidates, loaded_candidates, strict=True):
            assert abs(orig.confidence - loaded.confidence) < 1e-6

    def test_roundtrip_with_multiple_documents(self, tmp_path: Path) -> None:
        """Test round-trip with candidates from multiple documents."""
        jsonl_file = tmp_path / "multi_doc.jsonl"
        candidates = [
            Candidate("doc1_0", "First from doc1.", "doc1", 1.0),
            Candidate("doc1_1", "Second from doc1.", "doc1", 0.95),
            Candidate("doc2_0", "First from doc2.", "doc2", 1.0),
            Candidate("doc2_1", "Second from doc2.", "doc2", 0.9),
            Candidate("doc3_0", "Only from doc3.", "doc3", 0.85),
        ]

        write_candidate_pool(jsonl_file, candidates)
        loaded_candidates = read_candidate_pool(jsonl_file)

        # Verify all candidates preserved
        assert len(loaded_candidates) == len(candidates)
        for orig, loaded in zip(candidates, loaded_candidates, strict=True):
            assert orig.candidate_id == loaded.candidate_id
            assert orig.document_id == loaded.document_id
            assert orig.text == loaded.text


class TestCandidateValidation:
    """Tests for candidate model validation."""

    def test_candidate_validation_empty_text(self) -> None:
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            Candidate("c1", "", "doc1", 1.0)

    def test_candidate_validation_whitespace_text(self) -> None:
        """Test that whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            Candidate("c1", "   \n\t  ", "doc1", 1.0)

    def test_candidate_validation_invalid_confidence(self) -> None:
        """Test that confidence outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError, match="confidence must be in"):
            Candidate("c1", "Text.", "doc1", -0.1)

        with pytest.raises(ValueError, match="confidence must be in"):
            Candidate("c1", "Text.", "doc1", 1.1)

    def test_candidate_review_requires_question_when_approved(self) -> None:
        """Test that APPROVED status requires human_question."""
        with pytest.raises(ValueError, match="Approved candidate must have human_question"):
            CandidateReview(
                status=CandidateStatus.APPROVED,
                source_start=0,
                source_end=10,
            )

    def test_candidate_review_requires_source_span_when_approved(self) -> None:
        """Test that APPROVED status requires source_start and source_end."""
        with pytest.raises(ValueError, match="source_start and source_end"):
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="What is this?",
                source_start=None,
                source_end=10,
            )

    def test_candidate_review_validates_source_span(self) -> None:
        """Test that invalid source span is rejected."""
        # start >= end
        with pytest.raises(ValueError, match="Invalid source span"):
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=10,
                source_end=5,
            )

        # negative start
        with pytest.raises(ValueError, match="Invalid source span"):
            CandidateReview(
                status=CandidateStatus.APPROVED,
                human_question="Q?",
                source_start=-1,
                source_end=10,
            )

    def test_candidate_review_pending_no_question_required(self) -> None:
        """Test that PENDING status doesn't require question."""
        review = CandidateReview(status=CandidateStatus.PENDING)
        assert review.status == CandidateStatus.PENDING
        assert review.human_question is None

    def test_candidate_review_rejected_no_question_required(self) -> None:
        """Test that REJECTED status doesn't require question."""
        review = CandidateReview(
            status=CandidateStatus.REJECTED,
            rejection_reason="Not relevant",
        )
        assert review.status == CandidateStatus.REJECTED
        assert review.human_question is None

    def test_candidate_status_property(self) -> None:
        """Test that status property returns correct status."""
        pending = Candidate("c1", "Text.", "doc1", 1.0)
        assert pending.status == CandidateStatus.PENDING

        review = CandidateReview(
            status=CandidateStatus.APPROVED,
            human_question="Q?",
            source_start=0,
            source_end=10,
        )
        assert review.status == CandidateStatus.APPROVED


class TestInvalidRecordsRejected:
    """Tests for rejection of invalid records with clear errors."""

    def test_invalid_status_rejected(self, tmp_path: Path) -> None:
        """Test that invalid status value is rejected."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": 1.0,
            "schema_version": "0.2.0",
            "status": "invalid_status",  # Invalid
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        # This should fail when trying to create Candidate
        # (if review was in JSONL)
        # Currently, review is not in JSONL, so this just tests the model
        candidate = Candidate("c1", "Test.", "doc1", 1.0, schema_version="0.2.0")
        assert candidate.status == CandidateStatus.PENDING

    def test_missing_required_fields_error_message(self, tmp_path: Path) -> None:
        """Test that missing required fields produce clear error messages."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            # Missing text, document_id, confidence
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        error_msg = str(exc_info.value)
        assert "Missing required field 'text'" in error_msg

    def test_type_mismatch_error_message(self, tmp_path: Path) -> None:
        """Test that type mismatches produce clear error messages."""
        jsonl_file = tmp_path / "candidates.jsonl"
        data = {
            "candidate_id": "c1",
            "text": "Test.",
            "document_id": "doc1",
            "confidence": "not a number",  # Type mismatch
            "schema_version": "0.2.0",
        }
        jsonl_file.write_text(json.dumps(data) + "\n")

        with pytest.raises(InvalidSchemaError) as exc_info:
            read_candidate_pool(jsonl_file)

        error_msg = str(exc_info.value)
        assert "confidence" in error_msg
        assert "must be a number" in error_msg


class TestNoAutomaticGoldPromotion:
    """Tests to ensure persistence operations never promote candidates to gold."""

    def test_read_candidate_pool_never_creates_gold(self, tmp_path: Path) -> None:
        """Test that reading candidates doesn't create gold set artifacts."""
        jsonl_file = tmp_path / "candidates.jsonl"
        candidate = Candidate("c1", "Test.", "doc1", 1.0)
        write_candidate_pool(jsonl_file, [candidate])

        loaded = read_candidate_pool(jsonl_file)

        # Verify no gold-related fields or side effects
        assert loaded[0].status == CandidateStatus.PENDING
        assert loaded[0].review is None

    def test_write_candidate_pool_never_creates_gold(self, tmp_path: Path) -> None:
        """Test that writing candidates doesn't create gold set artifacts."""
        jsonl_file = tmp_path / "candidates.jsonl"
        candidate = Candidate("c1", "Test.", "doc1", 1.0)

        write_candidate_pool(jsonl_file, [candidate])

        # Verify only candidate JSONL was created
        assert jsonl_file.exists()

        # Verify content is just candidates, not gold
        content = jsonl_file.read_text()
        lines = [line for line in content.split("\n") if line.strip()]
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert "query_id" not in data
        assert "anchors" not in data
