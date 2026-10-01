"""Gold-set bootstrap and import utilities.

Tools for importing existing retrieval datasets with chunk IDs or
chunk text into SPANCHOR source-anchored format.

This module helps users migrate from chunk-ID-based evaluation to
SPANCHOR's stable source-anchored evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spanchor.annotation.locate import locate_text
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document


@dataclass
class ImportResult:
    """Result of importing a query record into SPANCHOR format.

    Attributes:
        query_id: The query identifier
        status: 'success', 'partial', 'failed'
        anchors: List of successfully resolved Anchor objects (empty if failed)
        unresolved_chunks: List of chunks that couldn't be resolved
        reason: Why import failed (if status != 'success')
    """

    query_id: str
    status: str  # 'success', 'partial', 'failed'
    anchors: list[Anchor]
    unresolved_chunks: list[str]
    reason: str = ""


def import_from_chunks(
    query_id: str,
    question: str,
    chunk_texts: list[str],
    documents: dict[str, Document],
    allow_partial: bool = False,
) -> ImportResult:
    """Import query with chunk texts into SPANCHOR source-anchored format.

    Converts a list of chunk texts (retrieved evidence) into SPANCHOR Anchor
    objects by finding the chunks in source documents.

    Args:
        query_id: Unique query identifier
        question: The query question/text
        chunk_texts: List of chunk text strings to anchor to source
        documents: Mapping of document_id → Document (source documents)
        allow_partial: If True, return partial success if some chunks resolve

    Returns:
        ImportResult with status and anchors list

    Notes:
        - Each chunk is searched for in all documents
        - Uses exact match first, then whitespace-normalized fallback
        - Multiple matches in same chunk may produce multiple anchors
        - Ambiguous matches (multiple per chunk) are reported but not resolved
        - No anchors created for unresolved chunks unless allow_partial=True
    """
    if not chunk_texts:
        return ImportResult(
            query_id=query_id,
            status="failed",
            anchors=[],
            unresolved_chunks=[],
            reason="No chunk texts provided",
        )

    if not documents:
        return ImportResult(
            query_id=query_id,
            status="failed",
            anchors=[],
            unresolved_chunks=chunk_texts,
            reason="No source documents provided",
        )

    anchors: list[Anchor] = []
    unresolved: list[str] = []
    ambiguous: list[tuple[str, int]] = []  # (chunk_text, num_matches)

    for chunk_text in chunk_texts:
        if not chunk_text.strip():
            unresolved.append(chunk_text)
            continue

        # Try to locate chunk in documents
        matches = locate_text(chunk_text, documents)

        if len(matches) == 0:
            unresolved.append(chunk_text)
        elif len(matches) == 1:
            # Single match: create anchor
            match = matches[0]
            anchor = Anchor(
                document_id=match.document_id,
                start=match.start,
                end=match.end,
                expected_text_hash=match.text_hash,
            )
            anchors.append(anchor)
        else:
            # Multiple matches: ambiguous, don't resolve
            ambiguous.append((chunk_text, len(matches)))
            unresolved.append(chunk_text)

    # Determine status
    if len(anchors) == len(chunk_texts):
        status = "success"
    elif len(anchors) > 0 and allow_partial:
        status = "partial"
    else:
        status = "failed"

    if ambiguous:
        reason = f"{len(ambiguous)} chunk(s) had multiple matches (ambiguous): " + "; ".join(
            f"'{t[:30]}...' ({n} matches)" for t, n in ambiguous[:3]
        )
    else:
        reason = ""

    return ImportResult(
        query_id=query_id,
        status=status,
        anchors=anchors,
        unresolved_chunks=unresolved,
        reason=reason,
    )


def import_from_chunk_dict(
    record: dict[str, Any],
    documents: dict[str, Document],
    chunk_key: str = "chunks",
    query_id_key: str = "query_id",
    question_key: str = "question",
    allow_partial: bool = False,
) -> ImportResult:
    """Import a query record dict into SPANCHOR format.

    Expects record format like:
    {
        "query_id": "q1",
        "question": "What is X?",
        "chunks": ["chunk text 1", "chunk text 2"],
    }

    Args:
        record: Dictionary with query_id, question, and chunks
        documents: Mapping of document_id → Document
        chunk_key: Key for chunk texts list in record
        query_id_key: Key for query_id in record
        question_key: Key for question in record
        allow_partial: Allow partial success

    Returns:
        ImportResult with resolved anchors
    """
    query_id = record.get(query_id_key, "")
    question = record.get(question_key, "")
    chunk_texts = record.get(chunk_key, [])

    if not query_id:
        return ImportResult(
            query_id="",
            status="failed",
            anchors=[],
            unresolved_chunks=chunk_texts,
            reason=f"Missing or empty '{query_id_key}' field",
        )

    if not isinstance(chunk_texts, list):
        return ImportResult(
            query_id=query_id,
            status="failed",
            anchors=[],
            unresolved_chunks=[],
            reason=f"'{chunk_key}' field must be a list",
        )

    return import_from_chunks(
        query_id=query_id,
        question=question,
        chunk_texts=chunk_texts,
        documents=documents,
        allow_partial=allow_partial,
    )


def summarize_import_results(results: list[ImportResult]) -> dict[str, Any]:
    """Summarize batch import results.

    Args:
        results: List of ImportResult from batch import

    Returns:
        Summary dict with counts and statistics
    """
    successful = [r for r in results if r.status == "success"]
    partial = [r for r in results if r.status == "partial"]
    failed = [r for r in results if r.status == "failed"]

    total_chunks_processed = sum(len(r.anchors) + len(r.unresolved_chunks) for r in results)
    total_anchors_created = sum(len(r.anchors) for r in results)
    total_unresolved = sum(len(r.unresolved_chunks) for r in results)

    return {
        "total_queries": len(results),
        "successful": len(successful),
        "partial": len(partial),
        "failed": len(failed),
        "total_chunks_processed": total_chunks_processed,
        "total_anchors_created": total_anchors_created,
        "total_unresolved": total_unresolved,
        "success_rate": len(successful) / len(results) if results else 0.0,
        "anchor_creation_rate": total_anchors_created / total_chunks_processed
        if total_chunks_processed > 0
        else 0.0,
    }
