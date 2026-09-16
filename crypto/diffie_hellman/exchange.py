"""A compact Diffie–Hellman exchange over a caller-provided prime field."""

from dataclasses import dataclass, field
import secrets

from crypto.math.modular import mod_pow
from crypto.math.primes import is_probable_prime


def _validate_parameters(prime: int, generator: int) -> None:
    if prime < 5 or not is_probable_prime(prime):
        raise ValueError("prime must be a prime integer of at least 5")
    if not 2 <= generator <= prime - 2:
        raise ValueError("generator must satisfy 2 <= generator <= prime - 2")


def generate_private_key(prime: int) -> int:
    """Return a private exponent uniformly in ``[2, prime-2]``."""
    if prime < 5:
        raise ValueError("prime must be at least 5")
    return secrets.randbelow(prime - 3) + 2


def public_key(private: int, prime: int, generator: int) -> int:
    _validate_parameters(prime, generator)
    if not 2 <= private <= prime - 2:
        raise ValueError("private key must satisfy 2 <= private <= prime - 2")
    return mod_pow(generator, private, prime)


def derive_shared_secret(peer_public: int, private: int, prime: int) -> int:
    if not is_probable_prime(prime):
        raise ValueError("prime must be prime")
    if not 2 <= private <= prime - 2:
        raise ValueError("private key is out of range")
    # Reject 0, 1 and -1: trivial public values collapse the shared secret.
    if not 2 <= peer_public <= prime - 2:
        raise ValueError("peer public key is invalid")
    return mod_pow(peer_public, private, prime)


@dataclass(frozen=True)
class Party:
    """One participant in a DH exchange.

    ``private`` defaults to a fresh secret. The class does not authenticate the
    peer and is consequently vulnerable to man-in-the-middle attacks.
    """

    prime: int
    generator: int
    private: int | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        _validate_parameters(self.prime, self.generator)
        if self.private is None:
            object.__setattr__(self, "private", generate_private_key(self.prime))
        elif not 2 <= self.private <= self.prime - 2:
            raise ValueError("private key is out of range")

    @property
    def public(self) -> int:
        assert self.private is not None
        return public_key(self.private, self.prime, self.generator)

    def shared_secret(self, peer_public: int) -> int:
        assert self.private is not None
        return derive_shared_secret(peer_public, self.private, self.prime)
