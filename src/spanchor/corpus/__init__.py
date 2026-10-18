"""Corpus versioning and fingerprinting.

This module provides deterministic hashing for corpus documents and gold sets,
enabling validation and tracking of data consistency across evaluation runs.
"""

from spanchor.corpus.fingerprint import (
    compute_corpus_hash,
    compute_gold_set_hash,
)

__all__ = [
    "compute_corpus_hash",
    "compute_gold_set_hash",
]
