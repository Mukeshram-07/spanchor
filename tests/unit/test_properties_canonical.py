"""Property-based tests for canonical document normalization and hashing.

These tests use Hypothesis to verify universal properties that must hold
across all possible inputs.
"""

import unicodedata

from hypothesis import given
from hypothesis import strategies as st

from spanchor.canonical.normalize import compute_hash, normalize_text


class TestCanonicalProperties:
    """Property-based tests for document canonicalization."""

    @given(
        st.text(
            alphabet=st.characters(
                # Include various Unicode categories and normalization forms
                blacklist_categories=("Cs",),  # Exclude surrogates
                blacklist_characters="\x00",  # Exclude null bytes
            ),
            min_size=0,
            max_size=1000,
        ).flatmap(
            lambda text: st.sampled_from(
                [
                    # Original text
                    text,
                    # NFD form (decomposed)
                    unicodedata.normalize("NFD", text),
                    # NFKC form (compatibility composed)
                    unicodedata.normalize("NFKC", text),
                    # NFKD form (compatibility decomposed)
                    unicodedata.normalize("NFKD", text),
                ]
            )
        ),
        st.sampled_from(
            [
                # Various newline patterns
                lambda t: t.replace("\n", "\r\n"),  # LF to CRLF
                lambda t: t.replace("\n", "\r"),  # LF to CR
                lambda t: t.replace("\n", "\r\n\r"),  # LF to mixed
                lambda t: t,  # No change
            ]
        ),
    )
    def test_canonicalization_idempotence(self, text: str, newline_transformer) -> None:
        """Property 1: Document Canonicalization Idempotence.

        **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

        For any text string with arbitrary Unicode normalization form and newline
        sequences, applying canonicalization once and applying it twice SHALL
        produce identical results with identical SHA256 hashes.

        This property ensures that:
        - normalize_text(normalize_text(text)) == normalize_text(text)
        - compute_hash(normalize_text(text)) is stable across re-normalization
        """
        # Apply newline transformation to introduce various line ending patterns
        transformed_text = newline_transformer(text)

        # First canonicalization pass
        canonical_once = normalize_text(transformed_text)
        hash_once = compute_hash(canonical_once)

        # Second canonicalization pass (idempotence test)
        canonical_twice = normalize_text(canonical_once)
        hash_twice = compute_hash(canonical_twice)

        # Assert idempotence: applying normalization twice == applying once
        assert canonical_once == canonical_twice, (
            "Canonicalization is not idempotent: "
            "normalize(normalize(text)) != normalize(text)"
        )

        # Assert hash stability: hash is stable after canonicalization
        assert hash_once == hash_twice, (
            "Hash is not stable after canonicalization: "
            f"hash changed from {hash_once} to {hash_twice}"
        )

        # Verify output is in canonical form
        assert unicodedata.is_normalized("NFC", canonical_once), (
            "Output is not in NFC form"
        )

        # Verify all line endings are normalized to \n
        assert "\r\n" not in canonical_once, "Found CRLF in canonical text"
        assert "\r" not in canonical_once, "Found CR in canonical text"

    @given(st.text(min_size=0, max_size=500))
    def test_hash_deterministic_across_calls(self, text: str) -> None:
        """Hash computation is deterministic.

        **Validates: Requirements 1.3**

        For any canonicalized text, computing the hash multiple times SHALL
        produce the same result.
        """
        canonical = normalize_text(text)

        # Compute hash multiple times
        hash1 = compute_hash(canonical)
        hash2 = compute_hash(canonical)
        hash3 = compute_hash(canonical)

        assert hash1 == hash2 == hash3, (
            "Hash computation is not deterministic"
        )

    @given(st.text(min_size=0, max_size=500))
    def test_normalized_output_is_nfc(self, text: str) -> None:
        """Normalized text is always in NFC form.

        **Validates: Requirements 1.1**

        For any input text, the output of normalize_text SHALL be in NFC
        Unicode normalization form.
        """
        result = normalize_text(text)
        assert unicodedata.is_normalized("NFC", result), (
            f"Output is not NFC normalized: {result!r}"
        )

    @given(st.text(min_size=0, max_size=500))
    def test_normalized_output_has_only_lf(self, text: str) -> None:
        """Normalized text only contains LF line endings.

        **Validates: Requirements 1.2**

        For any input text, the output of normalize_text SHALL contain only \n
        line endings (no \r\n or \r).
        """
        result = normalize_text(text)

        assert "\r\n" not in result, "Found CRLF in normalized output"
        assert "\r" not in result, "Found CR in normalized output"

    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=500),
    )
    def test_different_texts_different_hashes(self, text1: str, text2: str) -> None:
        """Different texts produce different hashes (collision resistance).

        **Validates: Requirements 1.3**

        For any two different canonicalized texts, their SHA256 hashes SHALL
        be different (with overwhelming probability).
        """
        canonical1 = normalize_text(text1)
        canonical2 = normalize_text(text2)

        # Only test if the canonical forms are actually different
        if canonical1 != canonical2:
            hash1 = compute_hash(canonical1)
            hash2 = compute_hash(canonical2)

            assert hash1 != hash2, (
                f"Hash collision detected: {canonical1!r} and {canonical2!r} "
                f"both hash to {hash1}"
            )

    @given(st.text(min_size=0, max_size=500))
    def test_hash_format_is_valid_sha256(self, text: str) -> None:
        """Hash output is valid SHA256 hex format.

        **Validates: Requirements 1.3**

        For any input, compute_hash SHALL return a 64-character lowercase
        hexadecimal string.
        """
        canonical = normalize_text(text)
        hash_value = compute_hash(canonical)

        # Check length (SHA256 = 256 bits = 64 hex chars)
        assert len(hash_value) == 64, f"Hash length is {len(hash_value)}, expected 64"

        # Check all characters are lowercase hex
        assert all(c in "0123456789abcdef" for c in hash_value), (
            f"Hash contains non-hex characters: {hash_value}"
        )
