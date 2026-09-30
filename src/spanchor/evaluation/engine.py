"""Evaluation engine for computing retrieval metrics against gold anchors.

This module provides the main evaluate() API that orchestrates:
- Anchor validation against documents
- Chunk-to-span mapping for retrieval results
- Metric computation (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU)
- Aggregate metric calculation
- Unmapped rate checking
"""

import warnings
from collections import defaultdict
from datetime import UTC, datetime
from typing import Literal

from spanchor.errors import DocumentNotFoundError, EvaluationError
from spanchor.evaluation.aggregation import aggregate_metrics
from spanchor.evaluation.hit import full_evidence_at_k, hit_at_k
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.iou import iou
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k
from spanchor.mapping.mapper import ChunkMapper
from spanchor.models.document import Document
from spanchor.models.query import Query
from spanchor.models.retrieval import RetrievalResult
from spanchor.models.run import Run


def evaluate(
    documents: dict[str, Document],
    queries: list[Query],
    retrieval_results: dict[str, list[RetrievalResult]],
    k: int = 5,
    min_overlap: float = 0.5,
    max_unmapped_rate: float = 0.1,
    ambiguity_policy: Literal["first_unclaimed", "all_occurrences", "fail"] = "first_unclaimed",
    aggregation_method: Literal["macro", "micro"] = "macro",
) -> Run:
    """Evaluate retrieval results against gold anchors.

    This is the main evaluation API that:
    1. Validates all anchors against their referenced documents
    2. Maps chunk-text results to canonical document spans
    3. Computes per-query metrics (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU)
    4. Computes aggregate metrics (macro-average across queries by default)
    5. Checks unmapped rate against threshold

    Args:
        documents: Dictionary mapping document_id to Document objects
        queries: List of Query objects with gold anchors
        retrieval_results: Dictionary mapping query_id to list of RetrievalResult objects
        k: K value for metrics (Recall@K, Precision@K, etc.) (default: 5)
        min_overlap: Minimum overlap fraction for Hit@K and FullEvidence@K (default: 0.5)
        max_unmapped_rate: Maximum allowed unmapped chunk rate (default: 0.1)
        ambiguity_policy: How to handle ambiguous chunk mappings (default: "first_unclaimed")
        aggregation_method: Aggregation strategy - "macro" (default) or "micro"
            - "macro": Equal weight per query (average metric values)
            - "micro": Weight proportional to gold span size (aggregate spans first)

    Returns:
        Run object containing all metrics, statistics, and configuration

    Raises:
        DocumentNotFoundError: If an anchor references a missing document
        EvaluationError: If validation or metric computation fails
        AnchorResolutionError: If an anchor cannot be validated against its document
        HashMismatchError: If document hash doesn't match anchor expectations

    Examples:
        >>> from spanchor.models import Document, Query, Anchor, RetrievalResult
        >>> doc = Document.from_text("doc1", "Hello world")
        >>> # Create anchor for "Hello"
        >>> from spanchor.canonical.normalize import compute_hash
        >>> anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        >>> query = Query("q1", "What is the greeting?", (anchor,))
        >>> # Retrieval result covering the gold span
        >>> result = RetrievalResult(rank=1, score=0.95, document_id="doc1", start=0, end=5)
        >>> run = evaluate(
        ...     documents={"doc1": doc},
        ...     queries=[query],
        ...     retrieval_results={"q1": [result]},
        ...     k=5
        ... )
        >>> run.aggregate_metrics["mean_recall@5"]
        1.0

    **Validates: Requirements 11.3, 11.4, 11.5, 11.6, 11.7, 5.11, 5.12, 10.1, 10.2**
    """
    # Validate K parameter
    if k <= 0:
        raise EvaluationError(
            message="K must be positive",
            metric_name="evaluate",
            values={"k": k},
        )

    # Validate min_overlap parameter
    if not (0.0 <= min_overlap <= 1.0):
        raise EvaluationError(
            message="min_overlap must be between 0 and 1",
            metric_name="evaluate",
            values={"min_overlap": min_overlap},
        )

    # Validate max_unmapped_rate parameter
    if not (0.0 <= max_unmapped_rate <= 1.0):
        raise EvaluationError(
            message="max_unmapped_rate must be between 0 and 1",
            metric_name="evaluate",
            values={"max_unmapped_rate": max_unmapped_rate},
        )

    # Small-sample warning (Requirement 24.1, 24.2, 24.3)
    if len(queries) < 30:
        warnings.warn(
            f"Warning: Gold set has only {len(queries)} queries. "
            "Statistical confidence may be low. "
            "Consider expanding the gold set to at least 30 queries for reliable results.",
            UserWarning,
            stacklevel=2,
        )

    # Step 1: Validate all anchors against documents (Requirement 11.3)
    for query in queries:
        for anchor in query.anchors:
            # Check document exists
            if anchor.document_id not in documents:
                raise DocumentNotFoundError(
                    document_id=anchor.document_id,
                    query_id=query.query_id,
                )
            # Validate anchor against document (raises on failure)
            doc = documents[anchor.document_id]
            anchor.validate(doc)

    # Step 2: Initialize chunk mapper (Requirement 11.4)
    mapper = ChunkMapper(documents=documents, ambiguity_policy=ambiguity_policy)

    # Track mapping statistics
    mapper_stats: dict[str, int] = defaultdict(int)

    # Step 3: Map chunk-text results to spans and build span sets per query
    mapped_retrieval_spans: dict[str, list[tuple[Interval, int, float]]] = {}

    for query_id, results in retrieval_results.items():
        # Reset claimed spans for each query
        mapper.reset_claims()

        query_spans: list[tuple[Interval, int, float]] = []

        for result in results:
            if result.needs_mapping():
                # Chunk-text form - needs mapping (Requirement 11.4)
                mapping_result = mapper.map_chunk(
                    chunk_text=result.text or "",
                    document_id=result.document_id,
                )

                # Update mapper statistics
                mapper_stats[mapping_result.status] += 1

                # Add mapped spans to query results
                for doc_id, start, end in mapping_result.spans:
                    # Create interval for this span
                    interval = (start, end)
                    query_spans.append((interval, result.rank, result.score))

            else:
                # Span form - already mapped
                if result.document_id and result.start is not None and result.end is not None:
                    interval = (result.start, result.end)
                    query_spans.append((interval, result.rank, result.score))
                    mapper_stats["MAPPED_EXACT"] += 1

        # Sort by rank to ensure proper ordering for @K metrics
        query_spans.sort(key=lambda x: x[1])  # Sort by rank
        mapped_retrieval_spans[query_id] = query_spans

    # Step 4: Check unmapped rate (Requirement 5.12)
    total_chunks = sum(mapper_stats.values())
    unmapped_count = mapper_stats.get("UNMAPPED", 0)

    if total_chunks > 0:
        unmapped_rate = unmapped_count / total_chunks
        if unmapped_rate > max_unmapped_rate:
            raise EvaluationError(
                message=f"Unmapped chunk rate ({unmapped_rate:.2%}) exceeds threshold ({max_unmapped_rate:.2%})",
                metric_name="evaluate",
                values={
                    "unmapped_count": unmapped_count,
                    "total_chunks": total_chunks,
                    "unmapped_rate": unmapped_rate,
                    "max_unmapped_rate": max_unmapped_rate,
                },
            )

    # Step 5: Compute per-query metrics (Requirement 11.5)
    per_query_metrics: dict[str, dict[str, float]] = {}

    for query in queries:
        query_id = query.query_id

        # Build gold span list from anchors
        gold_spans: list[Interval] = []
        for anchor in query.anchors:
            gold_spans.append((anchor.start, anchor.end))

        # Skip queries with no gold spans (cannot compute meaningful metrics)
        if not gold_spans:
            # Store zeros for queries with no gold anchors
            per_query_metrics[query_id] = {
                f"recall@{k}": 0.0,
                f"precision@{k}": 0.0,
                f"hit@{k}": 0.0,
                f"full_evidence@{k}": 0.0,
                "iou": 0.0,
                "retrieved_chars": 0,
            }
            continue

        # Get retrieved spans for this query
        query_spans = mapped_retrieval_spans.get(query_id, [])
        retrieved_spans: list[Interval] = [span for span, _, _ in query_spans]

        # Compute metrics (Requirement 11.5)
        metrics: dict[str, float] = {}

        try:
            # Recall@K (Requirement 11.5)
            metrics[f"recall@{k}"] = recall_at_k(gold_spans, retrieved_spans, k)

            # Precision@K (Requirement 11.5)
            metrics[f"precision@{k}"] = precision_at_k(gold_spans, retrieved_spans, k)

            # Hit@K (Requirement 11.5)
            metrics[f"hit@{k}"] = float(hit_at_k(gold_spans, retrieved_spans, k, min_overlap))

            # FullEvidence@K (Requirement 11.5)
            metrics[f"full_evidence@{k}"] = float(
                full_evidence_at_k(gold_spans, retrieved_spans, k, min_overlap)
            )

            # IoU (Requirement 11.5)
            metrics["iou"] = iou(gold_spans, retrieved_spans)

            # Retrieved character count (token-cost proxy) (Requirement 10.3)
            from spanchor.evaluation.intervals import length, union

            retrieved_chars = length(union(retrieved_spans[:k]))
            metrics["retrieved_chars"] = float(retrieved_chars)

        except EvaluationError as e:
            # Re-raise with query context
            raise EvaluationError(
                message=e.args[0] if e.args else "Evaluation failed",
                query_id=query_id,
                metric_name=e.metric_name,
                values=e.values,
            )

        per_query_metrics[query_id] = metrics

    # Step 6: Compute aggregate metrics (macro-average by default) (Requirement 11.6)
    aggregate_metrics_result = aggregate_metrics(
        per_query_metrics=per_query_metrics,
        queries=queries,
        aggregation_method=aggregation_method,  # Use the parameter (Requirement 10.1, 10.2)
    )

    # Step 7: Create Run object (Requirement 11.7)
    timestamp = datetime.now(UTC).isoformat()

    config = {
        "k": k,
        "min_overlap": min_overlap,
        "max_unmapped_rate": max_unmapped_rate,
        "ambiguity_policy": ambiguity_policy,
        "aggregation_method": aggregation_method,
    }

    run = Run(
        timestamp=timestamp,
        queries=tuple(queries),
        per_query_metrics=per_query_metrics,
        aggregate_metrics=aggregate_metrics_result,
        config=config,
        mapper_stats=dict(mapper_stats),
    )

    return run
