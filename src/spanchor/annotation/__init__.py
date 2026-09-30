"""Annotation helpers for creating gold sets.

Provides utilities for locating text in documents and creating
validated anchor entries.
"""

from spanchor.annotation.add import (
    AmbiguousTextError,
    DuplicateQueryIdError,
    OccurrenceOutOfRangeError,
    TextNotFoundError,
    add_anchor,
)
from spanchor.annotation.locate import LocateMatch, format_matches, locate_text

__all__ = [
    "LocateMatch",
    "locate_text",
    "format_matches",
    "add_anchor",
    "AmbiguousTextError",
    "TextNotFoundError",
    "OccurrenceOutOfRangeError",
    "DuplicateQueryIdError",
]
