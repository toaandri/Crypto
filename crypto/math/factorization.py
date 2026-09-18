"""Trial division for small educational integers."""


def factorize(number: int) -> list[int]:
    """Return prime factors with multiplicity; 1 has no prime factors."""
    if type(number) is not int or number < 1:
        raise ValueError("number must be a positive integer")
    factors = []
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors.append(divisor)
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if number > 1:
        factors.append(number)
    return factors
