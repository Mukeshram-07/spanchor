"""Tests for gold-set import functionality."""

from __future__ import annotations

import pytest

from spanchor.annotation.import_gold import (
    import_from_chunk_dict,
    import_from_chunks,
    summarize_import_results,
)
from spanchor.models.document import Document


class TestImportFromChunks:
    """Tests for import_from_chunks function."""

    @pytest.fixture
    def documents(self) -> dict[str, Document]:
        """Sample documents for testing."""
        return {
            "doc1": Document.from_text(
                "doc1",
                "CloudSync is a cloud storage service. It syncs files across devices.",
            ),
            "doc2": Document.from_text(
                "doc2",
                "The API provides authentication via OAuth2. Use tokens for requests.",
            ),
        }

    def test_single_chunk_success(self, documents: dict[str, Document]) -> None:
        """Import single chunk successfully."""
        result = import_from_chunks(
            query_id="q1",
            question="What is CloudSync?",
            chunk_texts=["CloudSync is a cloud storage service."],
            documents=documents,
        )

        assert result.status == "success"
        assert len(result.anchors) == 1
        assert result.anchors[0].document_id == "doc1"
        assert result.unresolved_chunks == []

    def test_multiple_chunks_success(self, documents: dict[str, Document]) -> None:
        """Import multiple chunks from different documents."""
        result = import_from_chunks(
            query_id="q1",
            question="Multiple chunks",
            chunk_texts=[
                "CloudSync is a cloud storage service.",
                "The API provides authentication via OAuth2.",
            ],
            documents=documents,
        )

        assert result.status == "success"
        assert len(result.anchors) == 2
        assert result.unresolved_chunks == []

    def test_unresolved_chunk(self, documents: dict[str, Document]) -> None:
        """Handle unresolved chunks."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["This text does not exist in any document"],
            documents=documents,
        )

        assert result.status == "failed"
        assert len(result.anchors) == 0
        assert len(result.unresolved_chunks) == 1

    def test_partial_success_without_allow_partial(self, documents: dict[str, Document]) -> None:
        """Partial success treated as failed when allow_partial=False."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=[
                "CloudSync is a cloud storage service.",
                "Nonexistent text",
            ],
            documents=documents,
            allow_partial=False,
        )

        assert result.status == "failed"
        assert len(result.anchors) == 1
        assert len(result.unresolved_chunks) == 1

    def test_partial_success_with_allow_partial(self, documents: dict[str, Document]) -> None:
        """Partial success allowed when allow_partial=True."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=[
                "CloudSync is a cloud storage service.",
                "Nonexistent text",
            ],
            documents=documents,
            allow_partial=True,
        )

        assert result.status == "partial"
        assert len(result.anchors) == 1
        assert len(result.unresolved_chunks) == 1

    def test_empty_chunks_list(self, documents: dict[str, Document]) -> None:
        """Handle empty chunks list."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=[],
            documents=documents,
        )

        assert result.status == "failed"
        assert len(result.anchors) == 0
        assert "No chunk texts" in result.reason

    def test_empty_documents(self) -> None:
        """Handle empty documents dict."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["CloudSync is a cloud storage service."],
            documents={},
        )

        assert result.status == "failed"
        assert "No source documents" in result.reason

    def test_whitespace_normalized_fallback(self) -> None:
        """Use whitespace-normalized fallback when exact match fails."""
        doc = Document.from_text(
            "doc1",
            "CloudSync  is   a  cloud  storage  service.",
        )
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["CloudSync is a cloud storage service."],
            documents={"doc1": doc},
        )

        # Should find match via normalized search
        assert result.status == "success"
        assert len(result.anchors) == 1

    def test_empty_string_chunk_skipped(self, documents: dict[str, Document]) -> None:
        """Skip empty or whitespace-only chunks."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["   ", "CloudSync is a cloud storage service."],
            documents=documents,
        )

        assert len(result.anchors) == 1
        assert result.unresolved_chunks == ["   "]

    def test_anchor_validation(self, documents: dict[str, Document]) -> None:
        """Created anchors are valid."""
        result = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["CloudSync is a cloud storage service."],
            documents=documents,
        )

        anchor = result.anchors[0]
        # Should be able to validate without error
        anchor.validate(documents["doc1"])

    def test_query_id_preservation(self, documents: dict[str, Document]) -> None:
        """Query ID is preserved in result."""
        result = import_from_chunks(
            query_id="my_custom_query_id",
            question="Test",
            chunk_texts=["CloudSync is a cloud storage service."],
            documents=documents,
        )

        assert result.query_id == "my_custom_query_id"


class TestImportFromChunkDict:
    """Tests for import_from_chunk_dict function."""

    @pytest.fixture
    def documents(self) -> dict[str, Document]:
        """Sample documents."""
        return {
            "doc1": Document.from_text("doc1", "CloudSync is a storage service."),
        }

    def test_basic_import(self, documents: dict[str, Document]) -> None:
        """Import from dict record."""
        record = {
            "query_id": "q1",
            "question": "What is CloudSync?",
            "chunks": ["CloudSync is a storage service."],
        }

        result = import_from_chunk_dict(record, documents)

        assert result.status == "success"
        assert len(result.anchors) == 1

    def test_custom_field_names(self, documents: dict[str, Document]) -> None:
        """Support custom field names."""
        record = {
            "id": "q1",
            "query": "What is it?",
            "evidence": ["CloudSync is a storage service."],
        }

        result = import_from_chunk_dict(
            record,
            documents,
            chunk_key="evidence",
            query_id_key="id",
            question_key="query",
        )

        assert result.status == "success"
        assert len(result.anchors) == 1

    def test_missing_query_id(self, documents: dict[str, Document]) -> None:
        """Handle missing query_id."""
        record = {"question": "What?", "chunks": ["CloudSync is a storage service."]}

        result = import_from_chunk_dict(record, documents)

        assert result.status == "failed"
        assert "Missing" in result.reason

    def test_invalid_chunks_type(self, documents: dict[str, Document]) -> None:
        """Handle chunks field that's not a list."""
        record = {
            "query_id": "q1",
            "question": "What?",
            "chunks": "not a list",
        }

        result = import_from_chunk_dict(record, documents)

        assert result.status == "failed"
        assert "must be a list" in result.reason

    def test_missing_optional_fields(self, documents: dict[str, Document]) -> None:
        """Handle missing optional fields (question)."""
        record = {
            "query_id": "q1",
            "chunks": ["CloudSync is a storage service."],
        }

        result = import_from_chunk_dict(record, documents)

        assert result.status == "success"
        assert len(result.anchors) == 1


class TestSummarizeResults:
    """Tests for summarize_import_results function."""

    def test_all_successful(self) -> None:
        """Summary for all successful imports."""
        doc = Document.from_text("doc1", "Test text")
        results = []
        for i in range(3):
            result = import_from_chunks(
                query_id=f"q{i}",
                question="Test",
                chunk_texts=["Test text"],
                documents={"doc1": doc},
            )
            results.append(result)

        summary = summarize_import_results(results)

        assert summary["total_queries"] == 3
        assert summary["successful"] == 3
        assert summary["partial"] == 0
        assert summary["failed"] == 0
        assert summary["success_rate"] == 1.0
        assert summary["total_anchors_created"] == 3

    def test_mixed_results(self) -> None:
        """Summary for mixed success/failure."""
        doc = Document.from_text("doc1", "Test text")
        results = []

        # Success
        result1 = import_from_chunks(
            query_id="q1",
            question="Test",
            chunk_texts=["Test text"],
            documents={"doc1": doc},
        )
        results.append(result1)

        # Partial (if allow_partial set during creation)
        result2 = import_from_chunks(
            query_id="q2",
            question="Test",
            chunk_texts=["Test text", "Nonexistent"],
            documents={"doc1": doc},
            allow_partial=True,
        )
        results.append(result2)

        # Failed
        result3 = import_from_chunks(
            query_id="q3",
            question="Test",
            chunk_texts=["Nonexistent text"],
            documents={"doc1": doc},
        )
        results.append(result3)

        summary = summarize_import_results(results)

        assert summary["total_queries"] == 3
        assert summary["successful"] == 1
        assert summary["partial"] == 1
        assert summary["failed"] == 1
        assert summary["total_anchors_created"] == 2

    def test_empty_results(self) -> None:
        """Summary for empty results list."""
        summary = summarize_import_results([])

        assert summary["total_queries"] == 0
        assert summary["success_rate"] == 0.0
