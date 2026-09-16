"""Primality tests and cryptographically strong candidate generation.

Miller–Rabin is deterministic below 2**64 with the fixed bases used here. For
larger values, random bases make it probabilistic.
"""

import secrets

from .modular import mod_pow

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_DETERMINISTIC_64_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def is_prime(number: int) -> bool:
    """Deterministic trial-division test, intended for small integers."""
    if number < 2:
        return False
    if number in _SMALL_PRIMES:
        return True
    if any(number % prime == 0 for prime in _SMALL_PRIMES):
        return False
    divisor = 41
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def is_probable_prime(number: int, rounds: int = 40) -> bool:
    """Test primality with Miller–Rabin.

    For values at least 2**64, ``rounds`` independent random witnesses are
    tested, giving a false-positive probability no greater than 4**-rounds.
    """
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    if number < 2:
        return False
    if number in _SMALL_PRIMES:
        return True
    if number % 2 == 0 or any(number % prime == 0 for prime in _SMALL_PRIMES[1:]):
        return False

    odd_part = number - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        powers_of_two += 1
        odd_part //= 2

    if number < 2**64:
        bases = (base % number for base in _DETERMINISTIC_64_BASES)
    else:
        bases = (secrets.randbelow(number - 3) + 2 for _ in range(rounds))

    for base in bases:
        if base in (0, 1):
            continue
        value = mod_pow(base, odd_part, number)
        if value in (1, number - 1):
            continue
        for _ in range(powers_of_two - 1):
            value = (value * value) % number
            if value == number - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int, rounds: int = 40) -> int:
    """Generate an odd probable prime with exactly *bits* bits."""
    if bits < 2:
        raise ValueError("bits must be at least 2")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate, rounds):
            return candidate
