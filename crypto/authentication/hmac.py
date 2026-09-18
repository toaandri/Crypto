"""RFC 2104 construction; educational Python implementation."""

from secrets import compare_digest

from crypto.hashes import sha256


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """Return a full 32-byte HMAC-SHA256 tag."""
    if not isinstance(key, bytes) or not isinstance(message, bytes):
        raise TypeError("key and message must be bytes")
    if len(key) > 64:
        key = sha256(key)
    key = key.ljust(64, b"\x00")
    inner = bytes(value ^ 0x36 for value in key)
    outer = bytes(value ^ 0x5C for value in key)
    return sha256(outer + sha256(inner + message))


def verify_hmac(key: bytes, message: bytes, tag: bytes) -> bool:
    """Compare a complete tag using the standard library comparator."""
    return isinstance(tag, bytes) and compare_digest(hmac_sha256(key, message), tag)
