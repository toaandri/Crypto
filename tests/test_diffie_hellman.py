import pytest

from crypto.diffie_hellman import Party


def test_both_parties_derive_the_same_secret():
    alice = Party(prime=23, generator=5, private=6)
    bob = Party(prime=23, generator=5, private=15)
    assert alice.public == 8
    assert bob.public == 19
    assert alice.shared_secret(bob.public) == bob.shared_secret(alice.public) == 2


@pytest.mark.parametrize(("prime", "generator"), [(21, 5), (23, 1), (2, 1)])
def test_invalid_parameters(prime, generator):
    with pytest.raises(ValueError):
        Party(prime, generator)


def test_trivial_peer_public_key_is_rejected():
    with pytest.raises(ValueError):
        Party(23, 5, private=6).shared_secret(1)

