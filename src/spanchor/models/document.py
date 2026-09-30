"""Document model with canonical text and validation.

The Document is the core model for source documents, storing canonicalized text
and a SHA256 hash for integrity verification.
"""

from dataclasses import dataclass

from spanchor.canonical.normalize import compute_hash, normalize_text


@dataclass(frozen=True, slots=True)
class Document:
    """Canonical source document with stable hash.

    Documents are immutable and store canonicalized text (NFC Unicode, \n-only
    line endings) with a SHA256 hash for integrity verification. Anchors reference
    character spans in this canonical text.

    Attributes:
        document_id: Unique identifier for this document
        text: Canonicalized text (NFC + normalized newlines)
        sha256: SHA256 hash of the canonical text
        schema_version: Schema version for forward compatibility
    """

    document_id: str
    text: str
    sha256: str
    schema_version: str = "0.1.0"

    @classmethod
    def from_text(cls, document_id: str, raw_text: str) -> "Document":
        """Create a Document from raw text.

        This factory method applies canonical normalization (NFC Unicode and
        newline normalization) and computes the SHA256 hash.

        Args:
            document_id: Unique identifier for this document
            raw_text: Raw input text (any encoding, any line endings)

        Returns:
            Document with canonicalized text and computed hash

        Examples:
            >>> doc = Document.from_text("doc1", "Hello\r\nWorld")
            >>> doc.text
            'Hello\nWorld'
            >>> len(doc.sha256)
            64
        """
        canonical = normalize_text(raw_text)
        hash_value = compute_hash(canonical)

        return cls(
            document_id=document_id,
            text=canonical,
            sha256=hash_value,
        )
