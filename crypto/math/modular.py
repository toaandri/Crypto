"""Basic modular arithmetic implemented without cryptographic libraries."""


def gcd(a: int, b: int) -> int:
    """Return the non-negative greatest common divisor of *a* and *b*."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return ``(g, x, y)`` such that ``a*x + b*y == g == gcd(a,b)``."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s if a >= 0 else -old_s, old_t if b >= 0 else -old_t


def mod_inverse(a: int, modulus: int) -> int:
    """Return the multiplicative inverse of *a* modulo *modulus*.

    Raises ValueError when the modulus is invalid or the inverse does not exist.
    """
    if modulus <= 1:
        raise ValueError("modulus must be greater than 1")
    divisor, coefficient, _ = extended_gcd(a, modulus)
    if divisor != 1:
        raise ValueError(f"{a} has no inverse modulo {modulus}")
    return coefficient % modulus


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """Compute ``base**exponent mod modulus`` by square-and-multiply."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if exponent < 0:
        base = mod_inverse(base, modulus)
        exponent = -exponent
    result = 1 % modulus
    base %= modulus
    while exponent:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result

