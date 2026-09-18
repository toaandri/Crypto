import random

import pytest

from crypto.symmetric import AES, gcm_decrypt, gcm_encrypt


@pytest.mark.parametrize("key,expected", [
    ("000102030405060708090a0b0c0d0e0f", "69c4e0d86a7b0430d8cdb78070b4c55a"),
    ("000102030405060708090a0b0c0d0e0f1011121314151617", "dda97ca4864cdfe06eaf70a0ec0d7191"),
    ("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
     "8ea2b7ca516745bfeafc49904b496089"),
])
def test_fips197_block_vectors(key, expected):
    cipher = AES(bytes.fromhex(key))
    plaintext = bytes.fromhex("00112233445566778899aabbccddeeff")
    ciphertext = bytes.fromhex(expected)
    assert cipher.encrypt_block(plaintext) == ciphertext
    assert cipher.decrypt_block(ciphertext) == plaintext


@pytest.mark.parametrize("message,expected_ciphertext,expected_tag", [
    (b"", "", "58e2fccefa7e3061367f1d57a4e7455a"),
    (bytes(16), "0388dace60b6a392f328c2b971b2fe78", "ab6e47d42cec13bdf53a67b21257bddf"),
])
def test_gcm_known_vectors(message, expected_ciphertext, expected_tag):
    nonce, ciphertext, tag = gcm_encrypt(message, bytes(16), bytes(12))
    assert ciphertext.hex() == expected_ciphertext
    assert tag.hex() == expected_tag
    assert gcm_decrypt(ciphertext, bytes(16), nonce, tag) == message


@pytest.mark.parametrize("key_length", [16, 24, 32])
@pytest.mark.parametrize("nonce_length", [8, 12, 16, 31])
def test_matches_independent_library(key_length, nonce_length):
    aead = pytest.importorskip("cryptography.hazmat.primitives.ciphers.aead")
    ciphers = pytest.importorskip("cryptography.hazmat.primitives.ciphers")
    rng = random.Random(key_length * 100 + nonce_length)
    key, nonce = rng.randbytes(key_length), rng.randbytes(nonce_length)
    for length in (0, 1, 15, 16, 17, 65):
        message, aad = rng.randbytes(length), rng.randbytes(length + 3)
        _, ciphertext, tag = gcm_encrypt(message, key, nonce, aad)
        assert ciphertext + tag == aead.AESGCM(key).encrypt(nonce, message, aad)
        assert gcm_decrypt(ciphertext, key, nonce, tag, aad) == message
    block = rng.randbytes(16)
    encryptor = ciphers.Cipher(ciphers.algorithms.AES(key), ciphers.modes.ECB()).encryptor()
    expected = encryptor.update(block) + encryptor.finalize()
    assert AES(key).encrypt_block(block) == expected
    assert AES(key).decrypt_block(expected) == block


@pytest.mark.parametrize("field", ["ciphertext", "nonce", "tag", "aad", "key"])
def test_every_authenticated_input_tampered(field, monkeypatch):
    nonce, ciphertext, tag = gcm_encrypt(b"secret", b"k" * 16, aad=b"header")
    args = dict(ciphertext=ciphertext, key=b"k" * 16, nonce=nonce, tag=tag, aad=b"header")
    value = args[field]
    args[field] = bytes([value[0] ^ 1]) + value[1:]
    def forbidden(*args):
        pytest.fail("decryption attempted before authentication")
    monkeypatch.setattr("crypto.symmetric.gcm._crypt", forbidden)
    with pytest.raises(ValueError):
        gcm_decrypt(**args)


def test_validation_and_default_nonce():
    for size in (0, 15, 17, 25, 33):
        with pytest.raises(ValueError):
            AES(bytes(size))
    for block in (b"", bytes(15), bytes(17), "x" * 16):
        with pytest.raises(ValueError):
            AES(bytes(16)).encrypt_block(block)
    with pytest.raises(ValueError):
        gcm_encrypt(b"", bytes(16), b"")
    with pytest.raises(TypeError):
        gcm_encrypt("text", bytes(16))
    nonce, ciphertext, tag = gcm_encrypt(b"", bytes(16))
    assert len(nonce) == 12 and len(tag) == 16
    with pytest.raises(ValueError):
        gcm_decrypt(ciphertext, bytes(16), nonce, tag[:-1])
