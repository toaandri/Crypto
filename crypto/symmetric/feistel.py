"""A reversible 64-bit Feistel cipher designed only for experimentation."""

from crypto.hashes.sha256 import sha256

BLOCK_SIZE = 8
ROUNDS = 16
_MASK32 = 0xFFFFFFFF


def _rotl32(value: int, count: int) -> int:
    return ((value << count) | (value >> (32 - count))) & _MASK32


def _round_function(half: int, round_key: int) -> int:
    value = (half + round_key) & _MASK32
    value ^= _rotl32(value, 7) ^ _rotl32(value, 19)
    value = (value * 0x9E3779B1) & _MASK32
    return value ^ (value >> 16)


class FeistelCipher:
    """Educational block cipher with an 8-byte block and a >= 8-byte key.

    Its construction demonstrates rounds, confusion and diffusion, but has not
    been cryptanalysed and must not protect sensitive information.
    """

    block_size = BLOCK_SIZE

    def __init__(self, key: bytes) -> None:
        if not isinstance(key, bytes) or len(key) < 8:
            raise ValueError("key must contain at least 8 bytes")
        material = sha256(b"feistel-educational-key-schedule\x00" + key)
        self._round_keys = tuple(
            int.from_bytes(material[(index * 4) % 32:(index * 4) % 32 + 4], "big")
            ^ ((index + 1) * 0x9E3779B9 & _MASK32)
            for index in range(ROUNDS)
        )

    def encrypt_block(self, block: bytes) -> bytes:
        left, right = self._split(block)
        for round_key in self._round_keys:
            left, right = right, left ^ _round_function(right, round_key)
        return left.to_bytes(4, "big") + right.to_bytes(4, "big")

    def decrypt_block(self, block: bytes) -> bytes:
        left, right = self._split(block)
        for round_key in reversed(self._round_keys):
            left, right = right ^ _round_function(left, round_key), left
        return left.to_bytes(4, "big") + right.to_bytes(4, "big")

    @staticmethod
    def _split(block: bytes) -> tuple[int, int]:
        if not isinstance(block, bytes) or len(block) != BLOCK_SIZE:
            raise ValueError(f"block must contain exactly {BLOCK_SIZE} bytes")
        return int.from_bytes(block[:4], "big"), int.from_bytes(block[4:], "big")

