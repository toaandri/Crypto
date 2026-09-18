"""AES-GCM with full 128-bit tags (NIST SP 800-38D).

    Callers must never reuse a nonce with the same key. Educational only.
"""

from secrets import compare_digest, token_bytes

from .aes import AES

_R = 0xE1000000000000000000000000000000


def _gf_multiply(left: int, right: int) -> int:
    result = 0
    for bit in range(127, -1, -1):
        if left & (1 << bit):
            result ^= right
        right = (right >> 1) ^ (_R if right & 1 else 0)
    return result


def _ghash(h: int, data: bytes) -> bytes:
    state = 0
    for offset in range(0, len(data), 16):
        state = _gf_multiply(state ^ int.from_bytes(data[offset:offset + 16], "big"), h)
    return state.to_bytes(16, "big")


def _pad(data: bytes) -> bytes:
    return data + b"\x00" * (-len(data) % 16)


def _xor(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def _prepare(key: bytes, nonce: bytes, data: bytes, aad: bytes) -> tuple[AES, int, bytes]:
    if not all(isinstance(value, bytes) for value in (nonce, data, aad)):
        raise TypeError("nonce, data and associated data must be bytes")
    if not nonce or len(nonce) >= 2**61 or len(aad) >= 2**61:
        raise ValueError("invalid nonce or associated-data length")
    if len(data) > 2**36 - 32:
        raise ValueError("GCM plaintext/ciphertext length limit exceeded")
    cipher = AES(key)
    h = int.from_bytes(cipher.encrypt_block(bytes(16)), "big")
    j0 = (nonce + b"\x00\x00\x00\x01" if len(nonce) == 12 else
          _ghash(h, _pad(nonce) + bytes(8) + (len(nonce) * 8).to_bytes(8, "big")))
    return cipher, h, j0


def _crypt(cipher: AES, j0: bytes, data: bytes) -> bytes:
    counter = int.from_bytes(j0[-4:], "big")
    output = bytearray()
    for offset in range(0, len(data), 16):
        counter = (counter + 1) % 2**32
        stream = cipher.encrypt_block(j0[:12] + counter.to_bytes(4, "big"))
        output.extend(_xor(data[offset:offset + 16], stream))
    return bytes(output)


def _tag(cipher: AES, h: int, j0: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    lengths = (len(aad) * 8).to_bytes(8, "big") + (len(ciphertext) * 8).to_bytes(8, "big")
    return _xor(cipher.encrypt_block(j0), _ghash(h, _pad(aad) + _pad(ciphertext) + lengths))


def gcm_encrypt(plaintext: bytes, key: bytes, nonce: bytes | None = None,
                aad: bytes = b"") -> tuple[bytes, bytes, bytes]:
    """Return (nonce, ciphertext, tag); default nonce is 12 random bytes."""
    nonce = token_bytes(12) if nonce is None else nonce
    cipher, h, j0 = _prepare(key, nonce, plaintext, aad)
    ciphertext = _crypt(cipher, j0, plaintext)
    return nonce, ciphertext, _tag(cipher, h, j0, ciphertext, aad)


def gcm_decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes,
                aad: bytes = b"") -> bytes:
    """Verify the full tag before producing any plaintext."""
    cipher, h, j0 = _prepare(key, nonce, ciphertext, aad)
    if not isinstance(tag, bytes) or len(tag) != 16:
        raise ValueError("GCM requires a 16-byte authentication tag")
    if not compare_digest(_tag(cipher, h, j0, ciphertext, aad), tag):
        raise ValueError("GCM authentication failed")
    return _crypt(cipher, j0, ciphertext)
