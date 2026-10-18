"""Deterministic hashing for corpus and gold set versioning.

This module implements corpus and gold-set hashing per PHASE_1_DESIGN_LOCK.md:

D1: Corpus hash = SHA256(JSON of sorted documents)
   - Deterministic: same docs → same hash
   - Order-independent: sorted by document_id
   - Schema-versioned: allows future format changes

D2: Gold-set hash = SHA256(JSON of query structure)
   - Hash identifies gold set STRUCTURE (anchors), not question text
   - Question text is editorial; anchors are evaluation source of truth
   - Changes to question text won't break hash
"""

import hashlib
import json
from typing import Any

from spanchor.models.document import Document
from spanchor.models.query import Query


def compute_corpus_hash(documents: list[Document]) -> str:
    """Compute deterministic SHA256 hash of corpus documents.

    Per D1 (PHASE_1_DESIGN_LOCK.md):
    - Hash = SHA256(JSON representation of all documents)
    - Documents sorted alphabetically by document_id
    - Schema-versioned for forward compatibility
    - Output format: "sha256:<hex_string>"

    This hash is:
    - Deterministic: same documents always produce same hash
    - Order-independent: sorted by doc_id before hashing
    - Sensitive: any document change produces different hash
    - Stable: used to detect corpus modifications

    Args:
        documents: List of Document objects to hash

    Returns:
        String in format "sha256:<hex_digest>" where hex_digest is 64 chars

    Examples:
        >>> from spanchor.models import Document
        >>> doc1 = Document.from_text("doc1", "Hello")
        >>> doc2 = Document.from_text("doc2", "World")
        >>> hash1 = compute_corpus_hash([doc1, doc2])
        >>> hash2 = compute_corpus_hash([doc2, doc1])  # reordered
        >>> hash1 == hash2  # order-independent
        True
        >>> len(hash1)  # format: "sha256:" + 64 hex chars
        71

    **Validates: D1**
    """
    # Build sorted document list by doc_id
    sorted_docs = sorted(documents, key=lambda d: d.document_id)

    # Create canonical JSON structure
    corpus_dict: dict[str, Any] = {
        "schema": "spanchor_corpus_0.1.0",
        "documents": {},
    }

    for doc in sorted_docs:
        corpus_dict["documents"][doc.document_id] = {
            "id": doc.document_id,
            "sha256": doc.sha256,
        }

    # Serialize to JSON with sorted keys (deterministic)
    corpus_json = json.dumps(corpus_dict, sort_keys=True, separators=(",", ":"))

    # Compute SHA256 hash
    hash_digest = hashlib.sha256(corpus_json.encode("utf-8")).hexdigest()

    return f"sha256:{hash_digest}"


def compute_gold_set_hash(queries: list[Query]) -> str:
    """Compute deterministic SHA256 hash of gold-set query structure.

    Per D2 (PHASE_1_DESIGN_LOCK.md):
    - Hash = SHA256(JSON of query STRUCTURE, NOT question text)
    - Identifies gold set by anchors and their spans, not editorial text
    - Question text changes → SAME hash (intended)
    - Anchor changes → DIFFERENT hash (intended)
    - Queries sorted by query_id, anchors sorted by document_id + start

    This hash is:
    - Deterministic: same structure always produces same hash
    - Order-independent: sorted by query_id, then anchor spans
    - Question-text-agnostic: question changes don't invalidate hash
    - Sensitive to structure: anchor changes detected

    Args:
        queries: List of Query objects to hash

    Returns:
        String in format "sha256:<hex_digest>" where hex_digest is 64 chars

    Examples:
        >>> from spanchor.models import Query, Anchor
        >>> from spanchor.canonical.normalize import compute_hash
        >>> anchor = Anchor("doc1", 0, 5, compute_hash("Hello"))
        >>> q1 = Query("q1", "What is greeting?", (anchor,))
        >>> q2 = Query("q1", "What's the greeting?", (anchor,))  # different text
        >>> compute_gold_set_hash([q1]) == compute_gold_set_hash([q2])  # same hash!
        True

    **Validates: D2**
    """
    # Build sorted query list by query_id
    sorted_queries = sorted(queries, key=lambda q: q.query_id)

    # Create canonical JSON structure
    gold_set_dict: dict[str, Any] = {
        "schema": "spanchor_gold_set_0.1.0",
        "queries": [],
    }

    for query in sorted_queries:
        # Sort anchors by document_id, then by start offset
        sorted_anchors = sorted(
            query.anchors,
            key=lambda a: (a.document_id, a.start, a.end),
        )

        query_entry: dict[str, Any] = {
            "query_id": query.query_id,
            "anchors": [],
        }

        for anchor in sorted_anchors:
            query_entry["anchors"].append(
                {
                    "document_id": anchor.document_id,
                    "start": anchor.start,
                    "end": anchor.end,
                }
            )

        gold_set_dict["queries"].append(query_entry)

    # Serialize to JSON with sorted keys (deterministic)
    gold_set_json = json.dumps(gold_set_dict, sort_keys=True, separators=(",", ":"))

    # Compute SHA256 hash
    hash_digest = hashlib.sha256(gold_set_json.encode("utf-8")).hexdigest()

    return f"sha256:{hash_digest}"
