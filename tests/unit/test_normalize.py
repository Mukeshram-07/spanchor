"""Unit tests for text normalization and hashing functions."""

import unicodedata

from spanchor.canonical.normalize import compute_hash, normalize_text


class TestNormalizeText:
    """Tests for normalize_text function."""

    def test_nfc_normalization(self):
        """NFC Unicode normalization is applied."""
        # café in NFD form (e + combining acute accent)
        nfd_text = "cafe\u0301"
        # café in NFC form (single character é)
        nfc_text = "café"

        assert normalize_text(nfd_text) == nfc_text
        assert unicodedata.is_normalized("NFC", normalize_text(nfd_text))

    def test_crlf_to_lf(self):
        """\\r\\n sequences are converted to \\n."""
        text = "hello\r\nworld\r\ntest"
        expected = "hello\nworld\ntest"
        assert normalize_text(text) == expected

    def test_cr_to_lf(self):
        """\\r sequences are converted to \\n."""
        text = "hello\rworld\rtest"
        expected = "hello\nworld\ntest"
        assert normalize_text(text) == expected

    def test_mixed_line_endings(self):
        """Mixed \\r\\n and \\r sequences are all converted to \\n."""
        text = "line1\r\nline2\rline3\nline4"
        expected = "line1\nline2\nline3\nline4"
        assert normalize_text(text) == expected

    def test_already_normalized_unchanged(self):
        """Text that is already normalized remains unchanged."""
        text = "hello\nworld"
        assert normalize_text(text) == text

    def test_empty_string(self):
        """Empty string is handled correctly."""
        assert normalize_text("") == ""

    def test_unicode_with_line_endings(self):
        """NFC normalization and newline normalization work together."""
        # NFD café with CRLF
        text = "cafe\u0301\r\nworld"
        expected = "café\nworld"
        result = normalize_text(text)
        assert result == expected
        assert unicodedata.is_normalized("NFC", result)

    def test_preserves_other_whitespace(self):
        """Other whitespace characters (tabs, spaces) are preserved."""
        text = "hello\t\tworld  test"
        assert normalize_text(text) == text


class TestComputeHash:
    """Tests for compute_hash function."""

    def test_deterministic_hash(self):
        """Same input produces same hash."""
        text = "hello world"
        hash1 = compute_hash(text)
        hash2 = compute_hash(text)
        assert hash1 == hash2

    def test_sha256_format(self):
        """Hash is SHA256 in hex format (64 characters)."""
        text = "test"
        hash_val = compute_hash(text)
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_known_hash_value(self):
        """Verify against known SHA256 hash."""
        text = "hello"
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert compute_hash(text) == expected

    def test_different_text_different_hash(self):
        """Different inputs produce different hashes."""
        hash1 = compute_hash("hello")
        hash2 = compute_hash("world")
        assert hash1 != hash2

    def test_empty_string_hash(self):
        """Empty string produces valid hash."""
        hash_val = compute_hash("")
        assert len(hash_val) == 64
        # Known SHA256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_val == expected

    def test_unicode_text_hash(self):
        """Unicode text is hashed correctly."""
        text = "café ☕"
        hash_val = compute_hash(text)
        assert len(hash_val) == 64
        # Verify deterministic
        assert hash_val == compute_hash(text)


class TestRoundTripProperty:
    """Test round-trip stability property from requirements."""

    def test_normalize_then_hash_is_stable(self):
        """Normalizing and hashing produces stable results (Requirement 1.5)."""
        raw_text = "café\r\nworld\rtest"

        # First pass
        canonical1 = normalize_text(raw_text)
        hash1 = compute_hash(canonical1)

        # Second pass (simulating export and reload)
        canonical2 = normalize_text(canonical1)
        hash2 = compute_hash(canonical2)

        assert canonical1 == canonical2
        assert hash1 == hash2

    def test_nfc_idempotent(self):
        """Normalizing already normalized text is idempotent."""
        # Start with NFD text
        nfd_text = "e\u0301"  # é in NFD

        first_pass = normalize_text(nfd_text)
        second_pass = normalize_text(first_pass)

        assert first_pass == second_pass
        assert compute_hash(first_pass) == compute_hash(second_pass)
