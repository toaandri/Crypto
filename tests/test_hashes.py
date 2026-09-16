import hashlib

import pytest

from crypto.hashes import SHA256, educational_hash, sha256


@pytest.mark.parametrize("message", [b"", b"abc", b"a" * 55, b"a" * 56, b"a" * 64, bytes(range(256))])
def test_sha256_reference_vectors(message):
    assert sha256(message) == hashlib.sha256(message).digest()


def test_known_sha256_hex_vector():
    assert sha256(b"abc").hex() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_incremental_interface_and_copy():
    digest = SHA256(b"Bon")
    clone = digest.copy()
    digest.update(b"jour")
    clone.update(b"soir")
    assert digest.hexdigest() == hashlib.sha256(b"Bonjour").hexdigest()
    assert clone.hexdigest() == hashlib.sha256(b"Bonsoir").hexdigest()


def test_educational_hash_is_deterministic_and_fixed_width():
    assert educational_hash(b"test") == educational_hash(b"test")
    assert 0 <= educational_hash(b"test") < 2**32


def test_sha256_requires_bytes():
    with pytest.raises(TypeError):
        sha256("abc")  # type: ignore[arg-type]

