"""Textbook integer RSA operations."""

from crypto.math.modular import gcd, mod_inverse, mod_pow
from crypto.math.primes import generate_prime

from .keys import PrivateKey, PublicKey


def generate_keypair(bits: int = 1024, public_exponent: int = 65537) -> tuple[PublicKey, PrivateKey]:
    """Generate an educational RSA key pair with a modulus of about *bits* bits."""
    if bits < 16:
        raise ValueError("bits must be at least 16")
    if public_exponent <= 1 or public_exponent % 2 == 0:
        raise ValueError("public exponent must be an odd integer greater than 1")
    p_bits = bits // 2
    q_bits = bits - p_bits
    while True:
        p = generate_prime(p_bits)
        q = generate_prime(q_bits)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if gcd(public_exponent, phi) == 1:
            break
    n = p * q
    d = mod_inverse(public_exponent, phi)
    return PublicKey(n, public_exponent), PrivateKey(n, d, p, q)


def encrypt_int(message: int, key: PublicKey) -> int:
    """Apply raw textbook RSA to one integer smaller than the modulus."""
    if not 0 <= message < key.n:
        raise ValueError("message integer must satisfy 0 <= message < n")
    return mod_pow(message, key.e, key.n)


def decrypt_int(ciphertext: int, key: PrivateKey) -> int:
    """Invert raw textbook RSA for one integer."""
    if not 0 <= ciphertext < key.n:
        raise ValueError("ciphertext integer must satisfy 0 <= ciphertext < n")
    return mod_pow(ciphertext, key.d, key.n)

