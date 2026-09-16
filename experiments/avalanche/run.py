"""Measure how SHA-256 output changes after flipping each input bit."""

from dataclasses import dataclass
from statistics import mean

from crypto.hashes import sha256


def bit_difference(left: bytes, right: bytes) -> int:
    if len(left) != len(right):
        raise ValueError("digests must have equal lengths")
    return sum((a ^ b).bit_count() for a, b in zip(left, right, strict=True))


def flip_bit(data: bytes, bit_index: int) -> bytes:
    if not 0 <= bit_index < len(data) * 8:
        raise IndexError("bit index outside message")
    changed = bytearray(data)
    byte_index, within_byte = divmod(bit_index, 8)
    changed[byte_index] ^= 1 << (7 - within_byte)
    return bytes(changed)


@dataclass(frozen=True)
class AvalancheResult:
    samples: tuple[int, ...]

    @property
    def average(self) -> float:
        return mean(self.samples)

    @property
    def average_ratio(self) -> float:
        return self.average / 256


def measure(message: bytes) -> AvalancheResult:
    if not message:
        raise ValueError("message must not be empty")
    original = sha256(message)
    samples = tuple(
        bit_difference(original, sha256(flip_bit(message, bit_index)))
        for bit_index in range(len(message) * 8)
    )
    return AvalancheResult(samples)


if __name__ == "__main__":
    result = measure("Bonjour".encode())
    print(f"{len(result.samples)} essais; moyenne: {result.average:.2f}/256 ({result.average_ratio:.1%})")

