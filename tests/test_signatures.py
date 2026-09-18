import hashlib

import pytest

from crypto.rsa import generate_keypair
from crypto.signatures import sign, verify


@pytest.fixture(scope="module")
def keys():
    return generate_keypair(512)


@pytest.mark.parametrize("message", [b"", b"hello", bytes(range(256))])
def test_signature_roundtrip_and_reference(keys, message):
    public, private = keys
    signature = sign(message, private)
    assert signature == pow(int.from_bytes(hashlib.sha256(message).digest(), "big"), private.d, private.n)
    assert verify(message, signature, public)
    assert not verify(message + b"!", signature, public)


def test_wrong_key_and_invalid_signatures(keys):
    public, private = keys
    other, _ = generate_keypair(512)
    signature = sign(b"hello", private)
    assert not verify(b"hello", signature, other)
    for invalid in (-1, public.n, signature + public.n, None, True):
        assert not verify(b"hello", invalid, public)


def test_tiny_key_rejected():
    public, private = generate_keypair(128)
    with pytest.raises(ValueError):
        sign(b"hello", private)
    with pytest.raises(ValueError):
        verify(b"hello", 1, public)
