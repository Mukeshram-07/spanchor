"""Shared pytest fixtures for spanchor tests.

Provides reusable fixtures for Documents, Anchors, Queries, and Runs
used across unit, integration, and regression test suites.
"""

from __future__ import annotations

import pytest

from spanchor.canonical.normalize import compute_hash
from spanchor.models.anchor import Anchor
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult
from spanchor.models.run import Run

# ---------------------------------------------------------------------------
# Document fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def doc1() -> Document:
    """A simple canonical document."""
    return Document.from_text(
        "doc1",
        "The quick brown fox jumps over the lazy dog.",
    )


@pytest.fixture
def doc2() -> Document:
    """A second canonical document."""
    return Document.from_text(
        "doc2",
        "Retrieval Augmented Generation improves answer quality by grounding responses in source documents.",
    )


@pytest.fixture
def documents(doc1: Document, doc2: Document) -> dict[str, Document]:
    """A dict of two canonical documents keyed by document_id."""
    return {"doc1": doc1, "doc2": doc2}


# ---------------------------------------------------------------------------
# Anchor fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def anchor_doc1(doc1: Document) -> Anchor:
    """A valid anchor pointing to 'quick brown fox' in doc1."""
    text = "quick brown fox"
    start = doc1.text.index(text)
    end = start + len(text)
    return Anchor(
        document_id="doc1",
        start=start,
        end=end,
        expected_text_hash=compute_hash(text),
    )


@pytest.fixture
def anchor_doc2(doc2: Document) -> Anchor:
    """A valid anchor pointing to 'source documents' in doc2."""
    text = "source documents"
    start = doc2.text.index(text)
    end = start + len(text)
    return Anchor(
        document_id="doc2",
        start=start,
        end=end,
        expected_text_hash=compute_hash(text),
    )


# ---------------------------------------------------------------------------
# Query fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def query1(anchor_doc1: Anchor) -> Query:
    """A query with one anchor in doc1."""
    return Query(
        query_id="q1",
        question="What animal jumps over the lazy dog?",
        anchors=(anchor_doc1,),
    )


@pytest.fixture
def query2(anchor_doc2: Anchor) -> Query:
    """A query with one anchor in doc2."""
    return Query(
        query_id="q2",
        question="What does RAG improve?",
        anchors=(anchor_doc2,),
    )


@pytest.fixture
def queries(query1: Query, query2: Query) -> list[Query]:
    """A list of two queries."""
    return [query1, query2]


# ---------------------------------------------------------------------------
# RetrievalResult fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def span_result_doc1(anchor_doc1: Anchor) -> RetrievalResult:
    """A span-form retrieval result covering the doc1 anchor exactly."""
    return RetrievalResult(
        rank=1,
        score=0.95,
        document_id=anchor_doc1.document_id,
        start=anchor_doc1.start,
        end=anchor_doc1.end,
    )


@pytest.fixture
def chunk_result() -> RetrievalResult:
    """A chunk-text retrieval result that needs mapping."""
    return RetrievalResult(
        rank=1,
        score=0.88,
        text="quick brown fox",
    )


# ---------------------------------------------------------------------------
# Run fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def baseline_run(queries: list[Query]) -> Run:
    """A baseline Run with decent metrics."""
    return Run(
        timestamp="2024-01-01T00:00:00Z",
        queries=tuple(queries),
        per_query_metrics={
            "q1": {"recall@5": 0.90, "precision@5": 0.85, "hit@5": 1.0},
            "q2": {"recall@5": 0.80, "precision@5": 0.75, "hit@5": 1.0},
        },
        aggregate_metrics={
            "recall@5": 0.85,
            "precision@5": 0.80,
            "hit@5": 1.0,
        },
        config={"k": 5, "min_overlap": 0.5},
        mapper_stats={"MAPPED_EXACT": 2, "UNMAPPED": 0},
    )


@pytest.fixture
def candidate_run_improved(queries: list[Query]) -> Run:
    """A candidate Run with improved metrics (no regressions)."""
    return Run(
        timestamp="2024-01-02T00:00:00Z",
        queries=tuple(queries),
        per_query_metrics={
            "q1": {"recall@5": 0.95, "precision@5": 0.90, "hit@5": 1.0},
            "q2": {"recall@5": 0.85, "precision@5": 0.80, "hit@5": 1.0},
        },
        aggregate_metrics={
            "recall@5": 0.90,
            "precision@5": 0.85,
            "hit@5": 1.0,
        },
        config={"k": 5, "min_overlap": 0.5},
        mapper_stats={"MAPPED_EXACT": 2, "UNMAPPED": 0},
    )


@pytest.fixture
def candidate_run_regressed(queries: list[Query]) -> Run:
    """A candidate Run with a regression in q1 recall."""
    return Run(
        timestamp="2024-01-02T00:00:00Z",
        queries=tuple(queries),
        per_query_metrics={
            "q1": {"recall@5": 0.60, "precision@5": 0.85, "hit@5": 1.0},  # recall dropped
            "q2": {"recall@5": 0.80, "precision@5": 0.75, "hit@5": 1.0},
        },
        aggregate_metrics={
            "recall@5": 0.70,
            "precision@5": 0.80,
            "hit@5": 1.0,
        },
        config={"k": 5, "min_overlap": 0.5},
        mapper_stats={"MAPPED_EXACT": 2, "UNMAPPED": 0},
    )
