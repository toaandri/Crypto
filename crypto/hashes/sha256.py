"""Pure-Python SHA-256 implementation following FIPS 180-4."""

from __future__ import annotations

_INITIAL = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)
_K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)
_MASK = 0xFFFFFFFF


def _rotr(value: int, count: int) -> int:
    return ((value >> count) | (value << (32 - count))) & _MASK


def _compress(state: list[int], chunk: bytes) -> None:
    words = [int.from_bytes(chunk[index:index + 4], "big") for index in range(0, 64, 4)]
    for index in range(16, 64):
        s0 = _rotr(words[index - 15], 7) ^ _rotr(words[index - 15], 18) ^ (words[index - 15] >> 3)
        s1 = _rotr(words[index - 2], 17) ^ _rotr(words[index - 2], 19) ^ (words[index - 2] >> 10)
        words.append((words[index - 16] + s0 + words[index - 7] + s1) & _MASK)

    a, b, c, d, e, f, g, h = state
    for index in range(64):
        big_s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
        choice = (e & f) ^ ((~e) & g)
        temp1 = (h + big_s1 + choice + _K[index] + words[index]) & _MASK
        big_s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
        majority = (a & b) ^ (a & c) ^ (b & c)
        temp2 = (big_s0 + majority) & _MASK
        h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & _MASK, c, b, a, (temp1 + temp2) & _MASK
    for index, value in enumerate((a, b, c, d, e, f, g, h)):
        state[index] = (state[index] + value) & _MASK


def sha256(data: bytes) -> bytes:
    """Return the 32-byte SHA-256 digest of *data*."""
    if not isinstance(data, bytes):
        raise TypeError("sha256() requires bytes")
    state = list(_INITIAL)
    bit_length = len(data) * 8
    padded = data + b"\x80"
    padded += b"\x00" * ((56 - len(padded) % 64) % 64)
    padded += bit_length.to_bytes(8, "big")
    for offset in range(0, len(padded), 64):
        _compress(state, padded[offset:offset + 64])
    return b"".join(word.to_bytes(4, "big") for word in state)


class SHA256:
    """Small hashlib-like incremental SHA-256 interface."""

    def __init__(self, data: bytes = b"") -> None:
        self._data = bytearray()
        self.update(data)

    def update(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError("update() requires bytes")
        self._data.extend(data)

    def digest(self) -> bytes:
        return sha256(bytes(self._data))

    def hexdigest(self) -> str:
        return self.digest().hex()

    def copy(self) -> "SHA256":
        return SHA256(bytes(self._data))
