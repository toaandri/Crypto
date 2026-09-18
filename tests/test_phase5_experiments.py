import pytest

from crypto.hashes import educational_hash
from experiments.attacks.run import run as attacks
from experiments.benchmarks.run import run as benchmarks


def test_local_attack_results():
    result = attacks()
    assert result == attacks()
    assert result["brute_force"]["key"] == 173
    assert result["dictionary"]["password"] == "bonjour123"
    collision = result["collision"]
    first, second = bytes.fromhex(collision["first"]), bytes.fromhex(collision["second"])
    assert first != second
    assert educational_hash(first) & 255 == educational_hash(second) & 255
    mitm = result["mitm"]
    assert mitm["alice_secret"] == mitm["mallory_alice_secret"]
    assert mitm["bob_secret"] == mitm["mallory_bob_secret"]
    assert mitm["intercepted"]
    assert result["factorization"]["p"] * result["factorization"]["q"] == 3233
    assert result["factorization"]["recovered_message"] == 42


def test_small_benchmark_report():
    result = benchmarks((32,), (0, 8), 1)
    assert len(result["results"]) == 11
    assert {row["operation"] for row in result["results"]} == {
        "rsa_keygen", "rsa_encrypt", "rsa_decrypt", "sha256",
        "feistel_cbc_encrypt", "feistel_cbc_decrypt"}
    for row in result["results"]:
        assert row["median_seconds"] >= 0
        assert row["peak_python_bytes"] >= 0  # An empty RSA message may allocate nothing.
    with pytest.raises(ValueError):
        benchmarks(repeats=0)
