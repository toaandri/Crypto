"""Hash-then-RSA demonstration, NOT a production signature scheme."""

from crypto.hashes import sha256
from crypto.math import mod_pow
from crypto.rsa import PrivateKey, PublicKey


def _digest(message: bytes, modulus: int) -> int:
    if not isinstance(message, bytes):
        raise TypeError("message must be bytes")
    if modulus <= 2**256 - 1:
        raise ValueError("RSA modulus must accommodate every SHA-256 digest")
    return int.from_bytes(sha256(message), "big")


def sign(message: bytes, key: PrivateKey) -> int:
    """Sign a digest with textbook RSA; requires a modulus above 256 bits."""
    return mod_pow(_digest(message, key.n), key.d, key.n)


def verify(message: bytes, signature: int, key: PublicKey) -> bool:
    digest = _digest(message, key.n)
    if type(signature) is not int or not 0 <= signature < key.n:
        return False
    return mod_pow(signature, key.e, key.n) == digest
