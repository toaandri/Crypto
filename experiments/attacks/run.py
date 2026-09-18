"""Five reproducible local demonstrations; no external targets or inputs."""

import json
from math import isqrt

from crypto.diffie_hellman import Party
from crypto.hashes import educational_hash, sha256
from crypto.math import mod_inverse
from crypto.rsa import PrivateKey, PublicKey, decrypt_int, encrypt_int
from crypto.symmetric.feistel import FeistelCipher


def brute_force_demo() -> dict:
    """Recover a cipher key selected from just 256 possible keys."""
    plaintext = b"DEMO1234"
    ciphertext = FeistelCipher((173).to_bytes(8, "big")).encrypt_block(plaintext)
    for candidate in range(256):
        if FeistelCipher(candidate.to_bytes(8, "big")).encrypt_block(plaintext) == ciphertext:
            return {"key": candidate, "attempts": candidate + 1, "keyspace": 256}
    raise AssertionError("demo key missing")


def dictionary_demo() -> dict:
    """Unsalted fast hashes do not protect a toy dictionary password."""
    target = sha256(b"bonjour123")
    words = ("password", "azerty", "bonjour123", "demo")
    for attempts, word in enumerate(words, 1):
        if sha256(word.encode()) == target:
            return {"password": word, "attempts": attempts}
    raise AssertionError("demo password missing")


def collision_demo() -> dict:
    """Find a collision after deliberately truncating the weak hash to 8 bits."""
    seen = {}
    for number in range(257):  # Pigeonhole principle guarantees termination.
        message = number.to_bytes(2, "big")
        digest = educational_hash(message) & 0xFF
        if digest in seen:
            return {"first": seen[digest].hex(), "second": message.hex(),
                    "digest": digest, "bits": 8, "attempts": number + 1}
        seen[digest] = message
    raise AssertionError("collision must exist")


def mitm_demo() -> dict:
    """Mallory replaces both public values in unauthenticated DH."""
    alice, bob = Party(23, 5, 6), Party(23, 5, 15)
    mallory_alice, mallory_bob = Party(23, 5, 3), Party(23, 5, 7)
    alice_secret = alice.shared_secret(mallory_alice.public)
    bob_secret = bob.shared_secret(mallory_bob.public)
    return {"alice_secret": alice_secret, "bob_secret": bob_secret,
            "mallory_alice_secret": mallory_alice.shared_secret(alice.public),
            "mallory_bob_secret": mallory_bob.shared_secret(bob.public),
            "intercepted": alice_secret != bob_secret}


def factorization_demo() -> dict:
    """Factor the fixed tiny RSA modulus and recover an encrypted integer."""
    public = PublicKey(3233, 17)
    ciphertext = encrypt_int(42, public)
    for attempts, p in enumerate(range(2, isqrt(public.n) + 1), 1):
        if public.n % p == 0:
            q = public.n // p
            private = PrivateKey(public.n, mod_inverse(public.e, (p - 1) * (q - 1)), p, q)
            return {"n": public.n, "p": p, "q": q, "attempts": attempts,
                    "recovered_message": decrypt_int(ciphertext, private)}
    raise AssertionError("toy modulus must factor")


def run() -> dict:
    return {"brute_force": brute_force_demo(), "dictionary": dictionary_demo(),
            "collision": collision_demo(), "mitm": mitm_demo(),
            "factorization": factorization_demo()}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
