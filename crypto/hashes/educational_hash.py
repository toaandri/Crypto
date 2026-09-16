"""A deliberately weak 32-bit hash used to demonstrate collisions."""


def educational_hash(data: bytes) -> int:
    """Return a tiny FNV-inspired hash. This is not cryptographically secure."""
    state = 0x811C9DC5
    for byte in data:
        state ^= byte
        state = (state * 0x01000193) & 0xFFFFFFFF
        state ^= state >> 13
    return state

