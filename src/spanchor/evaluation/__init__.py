"""Evaluation metrics and interval algebra.

Provides character-level recall, precision, hit, full evidence, and IoU metrics
using efficient sorted-interval merging algorithms.
"""

from spanchor.evaluation.hit import full_evidence_at_k, hit_at_k
from spanchor.evaluation.intervals import Interval, intersection, length, union
from spanchor.evaluation.iou import iou
from spanchor.evaluation.precision import precision_at_k
from spanchor.evaluation.recall import recall_at_k

__all__ = [
    "Interval",
    "union",
    "intersection",
    "length",
    "recall_at_k",
    "precision_at_k",
    "hit_at_k",
    "full_evidence_at_k",
    "iou",
]
