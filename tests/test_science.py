from crypto.math import is_prime
from experiments.science.run import factorization_study, modes_study, primality_study


def test_factorization_workloads():
    rows = factorization_study(1)
    assert len(rows) == 6
    assert [r["bits"] for r in rows] == sorted(r["bits"] for r in rows)
    for row in rows:
        p, q = row["factors"]
        assert p * q == row["number"]
        assert is_prime(p) and is_prime(q)


def test_primality_comparison_and_bounds():
    result = primality_study(1)
    assert all(row["is_prime"] for row in result["small_numbers"])
    assert [row["composite_false_positive_bound"] for row in result["probabilistic_rounds"]] == [
        4.0**-rounds for rounds in (1, 4, 8, 16, 40)]


def test_repeated_matrix():
    result = modes_study()
    assert len(result["plaintext"]) == 256
    assert len(set(result["plaintext"])) == len(set(result["ecb"])) == 2
    assert len(set(result["cbc"])) == 256
