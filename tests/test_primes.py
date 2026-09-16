import pytest

from crypto.math.primes import generate_prime, is_prime, is_probable_prime


@pytest.mark.parametrize("value", [2, 3, 5, 97, 997])
def test_known_primes(value):
    assert is_prime(value)
    assert is_probable_prime(value)


@pytest.mark.parametrize("value", [-7, 0, 1, 4, 21, 561, 1105, 3215031751])
def test_composites_and_carmichael_numbers(value):
    assert not is_probable_prime(value)


def test_generate_prime_has_requested_size():
    prime = generate_prime(64)
    assert prime.bit_length() == 64
    assert is_probable_prime(prime)


def test_invalid_round_count():
    with pytest.raises(ValueError):
        is_probable_prime(17, rounds=0)

