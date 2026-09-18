from dataclasses import replace

import pytest

from crypto.protocols import Handshake, establish_channels

KEY = b"shared-authentication-demo-key"


@pytest.mark.parametrize("message", [b"", b"hello", bytes(range(256))])
def test_bidirectional_ordered_exchange(message):
    alice, bob = establish_channels(KEY)
    for _ in range(3):
        assert bob.receive(alice.send(message)) == message
        assert alice.receive(bob.send(message[::-1])) == message[::-1]


@pytest.mark.parametrize("field", ["sequence", "iv", "ciphertext", "tag"])
def test_tampering_rejected_without_consuming_sequence(field):
    alice, bob = establish_channels(KEY)
    packet = alice.send(b"hello")
    value = getattr(packet, field)
    altered = value + 1 if field == "sequence" else bytes([value[0] ^ 1]) + value[1:]
    with pytest.raises(ValueError):
        bob.receive(replace(packet, **{field: altered}))
    assert bob.receive(packet) == b"hello"


def test_bad_tag_is_checked_before_decryption(monkeypatch):
    alice, bob = establish_channels(KEY)
    packet = replace(alice.send(b"hello"), tag=b"bad")
    def forbidden(*args):
        pytest.fail("unauthenticated ciphertext reached decryption")
    monkeypatch.setattr("crypto.protocols.secure_channel.cbc_decrypt", forbidden)
    with pytest.raises(ValueError):
        bob.receive(packet)


def test_replay_reflection_order_and_cross_session():
    alice, bob = establish_channels(KEY)
    _, other_bob = establish_channels(KEY)
    first, second = alice.send(b"first"), alice.send(b"second")
    for receiver, packet in ((bob, second), (alice, first), (other_bob, first)):
        with pytest.raises(ValueError):
            receiver.receive(packet)
    assert bob.receive(first) == b"first"
    with pytest.raises(ValueError):
        bob.receive(first)
    assert bob.receive(second) == b"second"


def test_wrong_authentication_key():
    alice = Handshake("alice", KEY)
    bob = Handshake("bob", b"different-authentication-key")
    with pytest.raises(ValueError):
        alice.finish(bob.hello, bob.proof(alice.hello))


def test_transcript_tampering_and_handshake_reuse():
    alice, bob = Handshake("alice", KEY), Handshake("bob", KEY)
    proof = bob.proof(alice.hello)
    for altered in (replace(bob.hello, nonce=b"x" * 32),
                    replace(bob.hello, public=4 if bob.hello.public != 4 else 16)):
        with pytest.raises(ValueError):
            alice.finish(altered, proof)
    alice.finish(bob.hello, proof)
    with pytest.raises(ValueError):
        alice.finish(bob.hello, proof)


@pytest.mark.parametrize("public", [0, 1, 2038, 2039, True])
def test_invalid_dh_values(public):
    alice, bob = Handshake("alice", KEY), Handshake("bob", KEY)
    with pytest.raises(ValueError):
        alice.proof(replace(bob.hello, public=public))


def test_roles_nonce_and_key_validation():
    with pytest.raises(ValueError):
        Handshake("mallory", KEY)
    with pytest.raises(ValueError):
        Handshake("alice", b"short")
    alice, bob = Handshake("alice", KEY), Handshake("bob", KEY)
    for hello in (alice.hello, replace(bob.hello, nonce=b"short")):
        with pytest.raises(ValueError):
            alice.proof(hello)
