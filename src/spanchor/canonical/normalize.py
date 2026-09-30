"""Text normalization and hashing for canonical documents.

All offsets in spanchor use canonical text:
- NFC Unicode normalization
- Newline normalization (\r\n and \r -> \n)
"""

import hashlib
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize text to canonical form.

    Applies:
    1. NFC Unicode normalization
    2. Newline normalization: converts all \r\n and \r sequences to \n

    Args:
        text: Raw input text

    Returns:
        Canonicalized text with NFC normalization and \n-only line endings

    Examples:
        >>> normalize_text("café")  # if input is NFD
        'café'  # NFC form
        >>> normalize_text("hello\r\nworld\rtest")
        'hello\nworld\ntest'
    """
    # Apply NFC Unicode normalization
    nfc_text = unicodedata.normalize("NFC", text)

    # Normalize newlines: \r\n -> \n, then \r -> \n
    # Order matters: replace \r\n first to avoid double-converting
    normalized = nfc_text.replace("\r\n", "\n").replace("\r", "\n")

    return normalized


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of canonicalized text.

    Args:
        text: Canonical text (should be output of normalize_text)

    Returns:
        SHA256 hash as lowercase hex string

    Examples:
        >>> compute_hash("hello")
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
