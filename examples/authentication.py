"""Run with python -m examples.authentication."""

from crypto.authentication import hmac_sha256, verify_hmac
from crypto.rsa import generate_keypair
from crypto.signatures import sign, verify


def main():
    message = b"Bonjour Bob"
    key = b"shared-demo-authentication-key"
    tag = hmac_sha256(key, message)
    print("HMAC valide :", verify_hmac(key, message, tag))
    print("Message modifie accepte :", verify_hmac(key, message + b"!", tag))
    public, private = generate_keypair(512)
    signature = sign(message, private)
    print("Signature valide :", verify(message, signature, public))
    print("Signature sur message modifie :", verify(message + b"!", signature, public))


if __name__ == "__main__":
    main()
