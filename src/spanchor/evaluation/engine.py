"""Evaluation engine for computing retrieval metrics against gold anchors.

This module provides the main evaluate() API that orchestrates:
- Anchor validation against documents
- Chunk-to-span mapping for retrieval results
- Metric computation (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU)
- Aggregate metric calculation
- Unmapped rate checking
- Corpus and gold-set versioning (hashing and mismatch detection)
- Pluggable metric registry (optional)
"""

import warnings
from collections import defaultdict
from datetime import UTC, datetime
from typing import Literal

from spanchor.corpus.fingerprint import compute_corpus_hash, compute_gold_set_hash
from spanchor.errors import DocumentNotFoundError, EvaluationError
from spanchor.evaluation.aggregation import aggregate_metrics
from spanchor.evaluation.intervals import Interval
from spanchor.evaluation.metrics import MetricRegistry
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
    gold_set_hash: str | None = None,
    corpus_mismatch_policy: Literal["warn", "fail", "ignore"] = "warn",
    metric_registry: MetricRegistry | None = None,
) -> Run:
    """Evaluate retrieval results against gold anchors.

    This is the main evaluation API that:
    1. Validates all anchors against their referenced documents
    2. Maps chunk-text results to canonical document spans
    3. Computes per-query metrics (Recall@K, Precision@K, Hit@K, FullEvidence@K, IoU)
    4. Computes aggregate metrics (macro-average across queries by default)
    5. Checks unmapped rate against threshold
    6. Computes corpus and gold-set hashes for versioning
    7. Validates mismatch (if gold_set_hash provided)

    Args:
        documents: Dictionary mapping document_id to Document objects
        queries: List of Query objects with gold anchors
        retrieval_results: Dictionary mapping query_id to list of RetrievalResult objects
        k: K value for metrics (Recall@K, Precision@K, etc.) (default: 5)
        min_overlap: Minimum overlap fraction for Hit@K and FullEvidence@K (default: 0.5)
        max_unmapped_rate: Maximum allowed unmapped chunk rate (default: 0.1)
        ambiguity_policy: How to handle ambiguous chunk mappings
            (default: "first_unclaimed")
        aggregation_method: Aggregation strategy - "macro" (default) or "micro"
            - "macro": Equal weight per query (average metric values)
            - "micro": Weight proportional to gold span size
              (aggregate spans first)
        gold_set_hash: Expected SHA256 hash of gold-set structure (str | None).
            If provided, computed hash must match or mismatch policy is applied.
        corpus_mismatch_policy: How to handle hash mismatches ("warn", "fail", "ignore")
            - "warn": Emit UserWarning if hash mismatch detected, continue
            - "fail": Raise EvaluationError if hash mismatch detected
            - "ignore": Don't check hash, skip mismatch detection
        metric_registry: Optional MetricRegistry for pluggable metrics.
            If None, a default registry is created with all 5 standard metrics.

    Returns:
        Run object containing all metrics, statistics, configuration, and hashes

    Raises:
        DocumentNotFoundError: If an anchor references a missing document
        EvaluationError: If validation, metric computation, or hash mismatch fails
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
        >>> len(run.corpus_hash) > 0  # SHA256 hash computed
        True

    **Validates: Requirements 11.3, 11.4, 11.5, 11.6, 11.7, 5.11, 5.12, 10.1, 10.2**
    """
    # Create default registry if not provided (Requirement: backward compat)
    if metric_registry is None:
        metric_registry = MetricRegistry(k=k, min_overlap=min_overlap)

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
                for _, start, end in mapping_result.spans:
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
            message = (
                f"Unmapped chunk rate ({unmapped_rate:.2%}) "
                f"exceeds threshold ({max_unmapped_rate:.2%})"
            )
            raise EvaluationError(
                message=message,
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
            # Match the exact keys from the registry
            default_metrics: dict[str, float] = {}
            for metric_name in metric_registry.get_all_metrics():
                default_metrics[metric_name] = 0.0
            default_metrics["retrieved_chars"] = 0.0
            per_query_metrics[query_id] = default_metrics
            continue

        # Get retrieved spans for this query
        query_spans = mapped_retrieval_spans.get(query_id, [])
        retrieved_spans: list[Interval] = [span for span, _, _ in query_spans]

        # Compute metrics using registry (Requirement 11.5)
        metrics: dict[str, float] = {}

        try:
            # For standard metrics (Recall, Precision, Hit, FullEvidence, IoU)
            # Compute from gold and retrieved spans
            registry_metrics = metric_registry.compute_all(gold_spans, retrieved_spans)
            metrics.update(registry_metrics)

            # For set-level metrics (Span Concentration, Fragmentation, Pairwise Overlap)
            # Build retrieved_spans with document_id info
            # Map back from intervals to their original document_id by re-scanning
            # mapped_retrieval_spans. We need to reconstruct: list[tuple[doc_id, start, end]]
            #
            # Unfortunately, after mapping, we've lost document_id info on the query_spans.
            # We need to track document_id through the mapping process.
            #
            # For now, we'll compute set-level metrics separately by building the info from
            # the results
            retrieved_spans_with_doc: list[tuple[str, int, int]] = []
            for result in retrieval_results.get(query_id, []):
                if result.needs_mapping():
                    # This was chunk-text form that got mapped
                    # The mapping gives us (doc_id, start, end) from the ChunkMapper
                    mapping_result = mapper.map_chunk(
                        chunk_text=result.text or "",
                        document_id=result.document_id,
                    )
                    for _, start, end in mapping_result.spans:
                        if result.document_id:  # Use the mapped document_id
                            retrieved_spans_with_doc.append((result.document_id, start, end))
                else:
                    # Span form - already has document_id
                    if result.document_id and result.start is not None and result.end is not None:
                        retrieved_spans_with_doc.append(
                            (result.document_id, result.start, result.end)
                        )

            # Compute set-level metrics only if they're registered in the metric registry
            # This respects custom registries that may not include these metrics
            for metric_name in ["span_concentration", "fragmentation_ratio", "pairwise_overlap"]:
                if metric_registry.get(metric_name):
                    if retrieved_spans_with_doc:
                        # Compute via registry
                        metrics[metric_name] = metric_registry.compute_metric(
                            metric_name=metric_name,
                            gold_spans=[],  # Set-wise metrics don't use gold spans
                            retrieved_spans=retrieved_spans_with_doc,  # type: ignore
                        )
                    else:
                        # No retrieved spans - set to 0.0
                        metrics[metric_name] = 0.0

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
            ) from e

        per_query_metrics[query_id] = metrics

    # Step 6: Compute aggregate metrics (macro-average by default) (Requirement 11.6)
    aggregate_metrics_result = aggregate_metrics(
        per_query_metrics=per_query_metrics,
        queries=queries,
        aggregation_method=aggregation_method,  # Use the parameter (Requirement 10.1, 10.2)
    )

    # Step 6.5: Compute corpus hash and validate gold-set hash (Feature 1)
    # Per D1: Corpus hash = SHA256(JSON of sorted documents by doc_id)
    documents_list = list(documents.values())
    computed_corpus_hash = compute_corpus_hash(documents_list)

    # Per D2: Gold-set hash = SHA256(JSON of query structure only (not text))
    computed_gold_set_hash = compute_gold_set_hash(queries)

    # Validate gold-set hash mismatch if provided
    if gold_set_hash is not None and corpus_mismatch_policy != "ignore":
        if computed_gold_set_hash != gold_set_hash:
            mismatch_msg = (
                f"Gold-set hash mismatch: "
                f"expected {gold_set_hash[:16]}..., "
                f"got {computed_gold_set_hash[:16]}..."
            )

            if corpus_mismatch_policy == "warn":
                warnings.warn(
                    f"{mismatch_msg}. This may indicate changes to anchors or queries.",
                    UserWarning,
                    stacklevel=2,
                )
            elif corpus_mismatch_policy == "fail":
                raise EvaluationError(
                    message=mismatch_msg,
                    metric_name="evaluate",
                    values={
                        "expected_hash": gold_set_hash,
                        "computed_hash": computed_gold_set_hash,
                    },
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
        corpus_hash=computed_corpus_hash,
        gold_set_hash=computed_gold_set_hash,
    )

    return run
