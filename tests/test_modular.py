import pytest

from crypto.math.modular import extended_gcd, gcd, mod_inverse, mod_pow


@pytest.mark.parametrize(("a", "b", "expected"), [(48, 18, 6), (-48, 18, 6), (0, 0, 0), (0, 7, 7)])
def test_gcd(a, b, expected):
    assert gcd(a, b) == expected


def test_extended_gcd_bezout_identity():
    divisor, x, y = extended_gcd(-240, 46)
    assert divisor == 2
    assert -240 * x + 46 * y == divisor


def test_mod_inverse_example():
    assert mod_inverse(3, 7) == 5
    assert mod_inverse(-3, 7) == 2


def test_mod_inverse_rejects_non_coprime_values():
    with pytest.raises(ValueError):
        mod_inverse(6, 9)


def test_mod_pow_matches_python_and_supports_negative_exponents():
    assert mod_pow(7, 560, 561) == pow(7, 560, 561)
    assert mod_pow(3, -1, 7) == 5

