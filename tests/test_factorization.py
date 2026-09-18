import math

import pytest

from crypto.math import factorize, is_prime


@pytest.mark.parametrize("number", [1, 2, 3, 16, 27, 3233, 65537, 10403])
def test_prime_factorization(number):
    factors = factorize(number)
    assert math.prod(factors) == number
    assert factors == sorted(factors)
    assert all(is_prime(factor) for factor in factors)


@pytest.mark.parametrize("number", [0, -1, 1.5, True])
def test_invalid_inputs(number):
    with pytest.raises(ValueError):
        factorize(number)
