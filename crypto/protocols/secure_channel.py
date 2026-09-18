"""PSK-authenticated DH + Feistel-CBC + encrypt-then-HMAC simulation.

The fixed small DH group and custom cipher are educational only. No network IO.
"""

from dataclasses import dataclass
import json
import secrets

from crypto.authentication import hmac_sha256, verify_hmac
from crypto.diffie_hellman import Party
from crypto.hashes import sha256
from crypto.symmetric import cbc_decrypt, cbc_encrypt

# Tiny safe prime: p = 2q + 1; generator 4 belongs to the order-q subgroup.
PRIME, ORDER, GENERATOR = 2039, 1019, 4
_DOMAIN = b"crypto-educational-channel-v1\x00"


@dataclass(frozen=True)
class Hello:
    role: str
    public: int
    nonce: bytes


@dataclass(frozen=True)
class Packet:
    sequence: int
    iv: bytes
    ciphertext: bytes
    tag: bytes


class Handshake:
    """One-use handshake, with a pre-shared authentication key per peer pair.

    Exchange ``hello`` values, then ``proof(peer)`` values, then ``finish``.
    Both proofs bind both roles, public values, nonces and fixed parameters.
    """

    def __init__(self, role: str, authentication_key: bytes):
        if role not in ("alice", "bob"):
            raise ValueError("role must be alice or bob")
        if not isinstance(authentication_key, bytes) or len(authentication_key) < 16:
            raise ValueError("authentication key must contain at least 16 bytes")
        self._role = role
        self._psk = authentication_key
        self._party = Party(PRIME, GENERATOR, secrets.randbelow(ORDER - 2) + 2)
        self._hello = Hello(role, self._party.public, secrets.token_bytes(32))
        self._finished = False

    @property
    def hello(self) -> Hello:
        return self._hello

    def _transcript(self, peer: Hello) -> bytes:
        if self._finished:
            raise ValueError("handshake already finished")
        opposite = "bob" if self._role == "alice" else "alice"
        if not isinstance(peer, Hello) or peer.role != opposite:
            raise ValueError("invalid peer role")
        if (type(peer.public) is not int or not 2 <= peer.public <= PRIME - 2
                or pow(peer.public, ORDER, PRIME) != 1):
            raise ValueError("invalid peer DH public value")
        if not isinstance(peer.nonce, bytes) or len(peer.nonce) != 32:
            raise ValueError("invalid peer nonce")
        parties = sorted((self.hello, peer), key=lambda hello: hello.role)
        values = [PRIME, ORDER, GENERATOR,
                  *[(hello.role, hello.public, hello.nonce.hex()) for hello in parties]]
        return _DOMAIN + json.dumps(values, separators=(",", ":")).encode("ascii")

    def proof(self, peer: Hello) -> bytes:
        return hmac_sha256(self._psk, self._transcript(peer) + self._role.encode())

    def finish(self, peer: Hello, peer_proof: bytes) -> "SecureChannel":
        transcript = self._transcript(peer)
        if not verify_hmac(self._psk, transcript + peer.role.encode(), peer_proof):
            raise ValueError("peer authentication failed")
        secret = self._party.shared_secret(peer.public).to_bytes(2, "big")
        # Separate extraction and labelled expansion, including the PSK and transcript.
        master = hmac_sha256(self._psk, _DOMAIN + secret + sha256(transcript))
        session = sha256(transcript)
        outgoing = self._role.encode() + b"->" + peer.role.encode()
        incoming = peer.role.encode() + b"->" + self._role.encode()
        self._finished = True
        return SecureChannel(master, session, outgoing, incoming)


class SecureChannel:
    """Ordered, bidirectional session. Use Handshake to construct endpoints.

    Replays, reflection and out-of-order packets are rejected. Not thread-safe.
    """

    def __init__(self, master: bytes, session: bytes, outgoing: bytes, incoming: bytes):
        self._session = session
        self._outgoing, self._incoming = outgoing, incoming
        self._send_enc = hmac_sha256(master, b"enc:" + outgoing)
        self._send_mac = hmac_sha256(master, b"mac:" + outgoing)
        self._recv_enc = hmac_sha256(master, b"enc:" + incoming)
        self._recv_mac = hmac_sha256(master, b"mac:" + incoming)
        self._sent = self._received = 0

    def _authenticated(self, direction: bytes, sequence: int, iv: bytes, ciphertext: bytes) -> bytes:
        return (_DOMAIN + self._session + direction + sequence.to_bytes(8, "big")
                + iv + len(ciphertext).to_bytes(8, "big") + ciphertext)

    def send(self, message: bytes) -> Packet:
        if not isinstance(message, bytes):
            raise TypeError("message must be bytes")
        if self._sent >= 2**64:
            raise ValueError("sequence counter exhausted")
        iv, ciphertext = cbc_encrypt(message, self._send_enc)
        tag = hmac_sha256(self._send_mac,
                          self._authenticated(self._outgoing, self._sent, iv, ciphertext))
        packet = Packet(self._sent, iv, ciphertext, tag)
        self._sent += 1
        return packet

    def receive(self, packet: Packet) -> bytes:
        if (not isinstance(packet, Packet) or type(packet.sequence) is not int
                or not 0 <= packet.sequence < 2**64 or packet.sequence != self._received
                or not isinstance(packet.iv, bytes) or len(packet.iv) != 8
                or not isinstance(packet.ciphertext, bytes) or not packet.ciphertext
                or len(packet.ciphertext) % 8):
            raise ValueError("invalid packet or unexpected sequence")
        data = self._authenticated(self._incoming, packet.sequence, packet.iv, packet.ciphertext)
        if not verify_hmac(self._recv_mac, data, packet.tag):
            raise ValueError("message authentication failed")
        plaintext = cbc_decrypt(packet.ciphertext, self._recv_enc, packet.iv)
        self._received += 1
        return plaintext


def establish_channels(authentication_key: bytes) -> tuple[SecureChannel, SecureChannel]:
    """Simulate both authenticated endpoints using an already shared key."""
    alice, bob = Handshake("alice", authentication_key), Handshake("bob", authentication_key)
    alice_proof, bob_proof = alice.proof(bob.hello), bob.proof(alice.hello)
    return alice.finish(bob.hello, bob_proof), bob.finish(alice.hello, alice_proof)
