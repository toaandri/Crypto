"""JSON benchmark report: python -m experiments.benchmarks.run --help."""

import argparse
import json
import platform
from statistics import median
from time import perf_counter
import tracemalloc

from crypto.hashes import sha256
from crypto.rsa import decrypt_bytes, encrypt_bytes, generate_keypair
from crypto.symmetric import cbc_decrypt, cbc_encrypt


def measure(operation, repeats: int) -> dict:
    """Time warmed operations; measure Python allocations in a separate run."""
    if repeats < 1:
        raise ValueError("repeats must be positive")
    operation()
    durations = []
    for _ in range(repeats):
        start = perf_counter()
        operation()
        durations.append(perf_counter() - start)
    tracemalloc.start()
    try:
        operation()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {"median_seconds": median(durations), "min_seconds": min(durations),
            "peak_python_bytes": peak, "repeats": repeats}


def run(key_sizes=(512, 1024, 2048), message_sizes=(16, 256, 1024), repeats=3) -> dict:
    if (repeats < 1 or not key_sizes or not message_sizes
            or any(bits < 16 for bits in key_sizes) or any(size < 0 for size in message_sizes)):
        raise ValueError("invalid benchmark parameters")
    rows = []
    key = b"benchmark-key-educational"
    for bits in key_sizes:
        rows.append({"operation": "rsa_keygen", "key_bits_requested": bits,
                     **measure(lambda: generate_keypair(bits), repeats)})
        public, private = generate_keypair(bits)
        for size in message_sizes:
            message = bytes(index % 256 for index in range(size))
            ciphertext = encrypt_bytes(message, public)
            assert decrypt_bytes(ciphertext, private) == message
            for name, operation in (
                ("rsa_encrypt", lambda: encrypt_bytes(message, public)),
                ("rsa_decrypt", lambda: decrypt_bytes(ciphertext, private)),
            ):
                rows.append({"operation": name, "key_bits_requested": bits,
                             "modulus_bits": public.n.bit_length(), "message_bytes": size,
                             **measure(operation, repeats)})
    for size in message_sizes:
        message = bytes(index % 256 for index in range(size))
        iv, ciphertext = cbc_encrypt(message, key)
        assert cbc_decrypt(ciphertext, key, iv) == message
        for name, operation in (
            ("sha256", lambda: sha256(message)),
            ("feistel_cbc_encrypt", lambda: cbc_encrypt(message, key)),
            ("feistel_cbc_decrypt", lambda: cbc_decrypt(ciphertext, key, iv)),
        ):
            rows.append({"operation": name, "message_bytes": size,
                         **measure(operation, repeats)})
    return {"python": platform.python_version(), "platform": platform.platform(),
            "educational_only": True, "results": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key-sizes", type=int, nargs="+", default=[512, 1024, 2048])
    parser.add_argument("--message-sizes", type=int, nargs="+", default=[16, 256, 1024])
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if (args.repeats < 1 or min(args.key_sizes) < 16 or min(args.message_sizes) < 0):
        parser.error("repeats >= 1, key sizes >= 16 and message sizes >= 0 required")
    print(json.dumps(run(args.key_sizes, args.message_sizes, args.repeats), indent=2))


if __name__ == "__main__":
    main()
