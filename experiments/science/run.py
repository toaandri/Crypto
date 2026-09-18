"""Generate experimental data using deterministic inputs and measured timings."""

import argparse
import json
from pathlib import Path
import platform
from statistics import mean, median, pstdev
from time import perf_counter

from crypto.diffie_hellman import Party
from crypto.math import factorize, is_prime, is_probable_prime
from crypto.symmetric import cbc_encrypt, ecb_encrypt, gcm_encrypt, gcm_decrypt
from experiments.attacks.run import run as attacks
from experiments.avalanche.run import measure as avalanche
from experiments.benchmarks.run import run as benchmarks


def _time(operation, repeats):
    samples = []
    result = operation()  # warmup
    for _ in range(repeats):
        start = perf_counter()
        result = operation()
        samples.append(perf_counter() - start)
    return {"median_seconds": median(samples), "samples_seconds": samples}, result


def _next_prime(number):
    candidate = number | 1
    while not is_probable_prime(candidate):
        candidate += 2
    return candidate


def factorization_study(repeats=3):
    rows = []
    for bits in (12, 16, 20, 24, 28, 32):
        p = _next_prime(2 ** (bits // 2 - 1) + 17)
        q = _next_prime(p + 12)
        number = p * q
        timing, factors = _time(lambda: factorize(number), repeats)
        rows.append({"number": number, "bits": number.bit_length(),
                     "factors": factors, **timing})
    return rows


def primality_study(repeats=3):
    rows = []
    for bits in (12, 16, 20, 24, 28, 32):
        prime = _next_prime(2 ** (bits - 1) + 1)
        for name, test in (("trial_division", is_prime), ("miller_rabin", is_probable_prime)):
            timing, result = _time(lambda: test(prime), repeats)
            rows.append({"algorithm": name, "number": prime, "bits": prime.bit_length(),
                         "is_prime": result, "deterministic": True, **timing})
    probabilistic = []
    for rounds in (1, 4, 8, 16, 40):
        prime = 2**127 - 1  # Known Mersenne prime; beyond the deterministic branch.
        timing, result = _time(lambda: is_probable_prime(prime, rounds), repeats)
        probabilistic.append({"number": prime, "bits": 127, "rounds": rounds,
                              "is_prime": result, "composite_false_positive_bound": 4.0**-rounds,
                              **timing})
    return {"small_numbers": rows, "probabilistic_rounds": probabilistic}


def dh_study(repeats=3):
    rows = []
    for bits in (16, 32, 64, 128):
        # Deterministic candidate sequence. Above 64 bits primality is probabilistic.
        q = _next_prime(2 ** (bits - 2) + 1)
        while not is_probable_prime(2 * q + 1):
            q = _next_prime(q + 2)
        p = 2 * q + 1
        def exchange():
            alice, bob = Party(p, 4, 6), Party(p, 4, 15)
            first, second = alice.shared_secret(bob.public), bob.shared_secret(alice.public)
            assert first == second
            return first
        timing, secret = _time(exchange, repeats)
        rows.append({"prime": p, "subgroup_order": q, "generator": 4,
                     "bits": p.bit_length(), "secret": secret, **timing})
    return rows


def avalanche_study():
    rows = []
    for message in (b"Bonjour", bytes(range(32)), b"Un seul bit change tout."):
        samples = avalanche(message).samples
        rows.append({"message_hex": message.hex(), "samples": list(samples),
                     "mean_bits": mean(samples), "stddev_bits": pstdev(samples),
                     "min_bits": min(samples), "max_bits": max(samples),
                     "mean_ratio": mean(samples) / 256})
    return rows


def modes_study():
    # 16x16 blocks form a repeated checkerboard. Each cell is one entire block.
    blocks = [b"A" * 8 if (x // 4 + y // 4) % 2 else b"B" * 8
              for y in range(16) for x in range(16)]
    plaintext = b"".join(blocks)
    key = b"fixed-modes-demo-key"
    ecb = ecb_encrypt(plaintext, key)
    _, cbc = cbc_encrypt(plaintext, key, bytes(8))
    def split(data):
        return [data[i:i + 8].hex() for i in range(0, len(plaintext), 8)]
    # Padding is excluded from visualization and distinct-block counts.
    return {"width": 16, "height": 16, "plaintext": split(plaintext),
            "ecb": split(ecb), "cbc": split(cbc), "padding_excluded": True}


def run(repeats=3, include_benchmarks=True):
    if repeats < 1:
        raise ValueError("repeats must be positive")
    data = {"python": platform.python_version(), "platform": platform.platform(),
            "repeats": repeats, "factorization": factorization_study(repeats),
            "primality": primality_study(repeats), "dh": dh_study(repeats),
            "avalanche": avalanche_study(), "modes": modes_study(), "attacks": attacks()}
    if include_benchmarks:
        data["benchmarks"] = benchmarks(repeats=repeats)
        aes_rows = []
        for key_size in (16, 24, 32):
            key = bytes(range(key_size))
            for size in (16, 256, 1024):
                message = bytes(index % 256 for index in range(size))
                # Fixed nonce ONLY to repeat the same public benchmark input.
                nonce, ciphertext, tag = gcm_encrypt(message, key, bytes(12), b"benchmark")
                assert gcm_decrypt(ciphertext, key, nonce, tag, b"benchmark") == message
                for name, operation in (
                    ("aes_gcm_encrypt", lambda: gcm_encrypt(message, key, bytes(12), b"benchmark")),
                    ("aes_gcm_decrypt", lambda: gcm_decrypt(ciphertext, key, nonce, tag, b"benchmark")),
                ):
                    from experiments.benchmarks.run import measure
                    aes_rows.append({"operation": name, "key_bits": key_size * 8,
                                     "message_bytes": size, **measure(operation, repeats)})
        data["aes_gcm_benchmarks"] = aes_rows
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/results/science.json"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--quick", action="store_true", help="Skip RSA and AES-GCM benchmarks")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    data = run(args.repeats, not args.quick)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Experimental results written to {args.output}")


if __name__ == "__main__":
    main()
