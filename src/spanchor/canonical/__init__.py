"""Canonical text normalization and hashing.

Provides NFC Unicode normalization, newline normalization, and SHA256 hashing
to ensure stable anchor offsets across platforms.
"""

from spanchor.canonical.normalize import compute_hash, normalize_text

__all__ = ["normalize_text", "compute_hash"]
