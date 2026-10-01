"""Spanchor: Regression-testing for RAG retrieval pipelines using stable source-document anchors.

Core workflow:
1. Create gold set with anchors pointing to character spans in canonical source documents
2. Evaluate retrieval results against gold set (spans or chunk text)
3. Compare baseline vs candidate runs to detect regressions
4. Use in CI to prevent retrieval quality degradation

Example:
    >>> from spanchor import Document, Anchor, evaluate, compare
    >>> # Create documents
    >>> doc = Document.from_text("doc1", "Hello world! This is a test.")
    >>> # Evaluate retrieval (see docs for full API)

Requirements: 26.1, 26.2, 26.3, 26.4, 26.5, 26.6, 26.7
"""

from spanchor.comparison.compare import compare
from spanchor.errors import (
    AnchorResolutionError,
    ComparisonError,
    DocumentNotFoundError,
    EvaluationError,
    HashMismatchError,
    InvalidRetrievalResultError,
    InvalidSchemaError,
    OrphanedAnchorError,
    SpanchorError,
)
from spanchor.evaluation.engine import evaluate
from spanchor.models import Anchor, Document, Query, RetrievalResult, Run
from spanchor.validation import CorpusIssue, check_corpus

__version__ = "0.2.0"

__all__ = [
    # Models (req 26.1, 26.2, 26.3)
    "Anchor",
    "Document",
    "Query",
    "RetrievalResult",
    "Run",
    # Core functions (req 26.4, 26.5, 26.6)
    "evaluate",
    "compare",
    "check_corpus",
    "CorpusIssue",
    # Errors (req 26.7)
    "SpanchorError",
    "InvalidSchemaError",
    "DocumentNotFoundError",
    "HashMismatchError",
    "AnchorResolutionError",
    "OrphanedAnchorError",
    "InvalidRetrievalResultError",
    "EvaluationError",
    "ComparisonError",
    # Version
    "__version__",
]
