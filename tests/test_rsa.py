import pytest

from crypto.rsa import (
    EncryptedMessage, PrivateKey, PublicKey, decrypt_bytes, decrypt_int,
    decrypt_text, encrypt_bytes, encrypt_int, encrypt_text, generate_keypair,
)


@pytest.fixture(scope="module")
def keys():
    return generate_keypair(128)


def test_integer_round_trip(keys):
    public, private = keys
    assert decrypt_int(encrypt_int(42, public), private) == 42


def test_integer_range_validation(keys):
    public, private = keys
    with pytest.raises(ValueError):
        encrypt_int(public.n, public)
    with pytest.raises(ValueError):
        decrypt_int(-1, private)


@pytest.mark.parametrize("message", [b"", b"\x00\x00hello", b"a" * 100])
def test_bytes_round_trip_preserves_length_and_zeroes(keys, message):
    public, private = keys
    assert decrypt_bytes(encrypt_bytes(message, public), private) == message


def test_unicode_text_round_trip(keys):
    public, private = keys
    encrypted = encrypt_text("Bonjour, chiffrement 🔐", public)
    assert decrypt_text(encrypted, private) == "Bonjour, chiffrement 🔐"


def test_key_serialization(keys):
    public, private = keys
    assert PublicKey.from_json(public.to_json()) == public
    assert PrivateKey.from_json(private.to_json(include_primes=True)) == private


def test_malformed_encrypted_message_is_rejected(keys):
    _, private = keys
    with pytest.raises(ValueError):
        decrypt_bytes(EncryptedMessage((1,), 100), private)

