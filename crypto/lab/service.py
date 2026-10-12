"""Bounded experiments using the repository's own implementations.

All requests are independent. Keys, messages and results are never persisted.
The deliberately small input limits keep the local workbench responsive.
"""

from dataclasses import replace
import secrets

from crypto.authentication import hmac_sha256, verify_hmac
from crypto.diffie_hellman import Party
from crypto.hashes import educational_hash, sha256
from crypto.math import extended_gcd, factorize, is_probable_prime, mod_inverse, mod_pow
from crypto.protocols import establish_channels
from crypto.rsa import decrypt_bytes, encrypt_bytes, generate_keypair
from crypto.signatures import sign, verify
from crypto.symmetric import cbc_encrypt, ecb_encrypt, gcm_decrypt, gcm_encrypt
from experiments.avalanche.run import bit_difference, flip_bit


def _text(data, name, default="", limit=2048):
    value = data.get(name, default)
    if not isinstance(value, str) or len(value.encode("utf-8")) > limit:
        raise ValueError(f"{name}: text required, at most {limit} UTF-8 bytes.")
    return value


def _integer(data, name, default, low, high):
    value = data.get(name, default)
    if type(value) is int:
        number = value
    elif isinstance(value, str) and len(value) <= 20:
        try:
            number = int(value)
        except ValueError:
            raise ValueError(f"{name}: enter an integer.") from None
    else:
        raise ValueError(f"{name}: enter an integer.")
    if not low <= number <= high:
        raise ValueError(f"{name}: enter a value between {low} and {high}.")
    return number


def _hex(data, name, default="", sizes=None, limit=2048):
    value = _text(data, name, default, limit=limit * 2 + 256)
    try:
        result = bytes.fromhex(value)
    except ValueError:
        raise ValueError(f"{name}: use hexadecimal byte pairs (00 to ff).") from None
    if len(result) > limit or (sizes is not None and len(result) not in sizes):
        expected = ", ".join(map(str, sizes)) if sizes else f"at most {limit}"
        raise ValueError(f"{name}: expected {expected} bytes.")
    return result


def _hash(data):
    message = _text(data, "message", "Hello", limit=512).encode("utf-8")
    mode = _text(data, "mode", "bit")
    if mode == "bit":
        if not message:
            raise ValueError("Enter a message before flipping a bit.")
        index = _integer(data, "bit", 0, 0, len(message) * 8 - 1)
        changed = flip_bit(message, index)
    elif mode == "text":
        changed = _text(data, "comparison", "hello", limit=512).encode("utf-8")
        index = None
    else:
        raise ValueError("Choose a bit flip or a text comparison.")
    left, right = sha256(message), sha256(changed)
    return {"original": message.hex(), "changed": changed.hex(), "bit": index,
            "digest": left.hex(), "changed_digest": right.hex(),
            "difference": bit_difference(left, right), "total_bits": 256,
            "weak_digest": f"{educational_hash(message):08x}",
            "weak_changed_digest": f"{educational_hash(changed):08x}"}


def _math(data):
    a = _integer(data, "a", 240, -10**12, 10**12)
    b = _integer(data, "b", 46, -10**12, 10**12)
    modulus = _integer(data, "modulus", 497, 2, 10**12)
    exponent = _integer(data, "exponent", 13, 0, 100000)
    n = _integer(data, "n", 3233, 1, 10**9)
    g, x, y = extended_gcd(a, b)
    trace, left, right = [], abs(a), abs(b)
    while right:
        quotient, remainder = divmod(left, right)
        trace.append({"a": left, "b": right, "quotient": quotient, "remainder": remainder})
        left, right = right, remainder
    try:
        inverse = mod_inverse(a, modulus)
    except ValueError:
        inverse = None
    return {"gcd": g, "x": x, "y": y, "a": a, "b": b, "trace": trace,
            "inverse": inverse, "modulus": modulus, "exponent": exponent,
            "power": mod_pow(a, exponent, modulus), "n": n,
            "prime": is_probable_prime(n), "factors": factorize(n)}


def _rsa(data):
    bits = _integer(data, "bits", 256, 256, 1024)
    if bits not in (256, 512, 1024):
        raise ValueError("Choose a 256-, 512- or 1024-bit RSA key.")
    message = _text(data, "message", "Hello, RSA!").encode("utf-8")
    public, private = generate_keypair(bits)
    encrypted = encrypt_bytes(message, public)
    recovered = decrypt_bytes(encrypted, private)
    return {"p": str(private.p), "q": str(private.q), "n": str(public.n),
            "phi": str((private.p - 1) * (private.q - 1)), "e": public.e,
            "d": str(private.d), "bits": public.n.bit_length(),
            "blocks": [str(block) for block in encrypted.blocks],
            "length": encrypted.length, "recovered": recovered.decode("utf-8"),
            "verified": recovered == message, "public_key": public.to_json()}


def _dh(data):
    prime = _integer(data, "prime", 23, 5, 65521)
    generator = _integer(data, "generator", 5, 2, prime - 2)
    a = _integer(data, "alice", 6, 2, prime - 2)
    b = _integer(data, "bob", 15, 2, prime - 2)
    alice, bob = Party(prime, generator, a), Party(prime, generator, b)
    return {"prime": prime, "generator": generator, "alice": a, "bob": b,
            "alice_public": alice.public, "bob_public": bob.public,
            "alice_secret": alice.shared_secret(bob.public),
            "bob_secret": bob.shared_secret(alice.public)}


def _aes(data):
    operation = _text(data, "operation", "encrypt")
    aad = _text(data, "aad", "Alice → Bob").encode("utf-8")
    if operation == "encrypt":
        size = _integer(data, "key_bits", 128, 128, 256)
        if size not in (128, 192, 256):
            raise ValueError("AES accepts 128-, 192- or 256-bit keys.")
        key_text = _text(data, "key").strip()
        key = _hex(data, "key", sizes=(16, 24, 32)) if key_text else secrets.token_bytes(size // 8)
        message = _text(data, "message", "A secret between Alice and Bob.").encode("utf-8")
        nonce, ciphertext, tag = gcm_encrypt(message, key, aad=aad)
        recovered = gcm_decrypt(ciphertext, key, nonce, tag, aad=aad)
        return {"key": key.hex(), "key_bits": len(key) * 8, "nonce": nonce.hex(),
                "ciphertext": ciphertext.hex(), "tag": tag.hex(),
                "aad": aad.decode("utf-8"), "recovered": recovered.decode("utf-8"),
                "verified": recovered == message}
    if operation == "decrypt":
        key = _hex(data, "key", sizes=(16, 24, 32))
        nonce = _hex(data, "nonce", sizes=(12,))
        tag = _hex(data, "tag", sizes=(16,))
        ciphertext = _hex(data, "ciphertext")
        try:
            plaintext = gcm_decrypt(ciphertext, key, nonce, tag, aad=aad)
        except ValueError:
            return {"verified": False, "reason": "Authentication rejected: the key, tag, nonce, AAD or ciphertext has changed."}
        return {"verified": True, "recovered_hex": plaintext.hex(),
                "recovered": plaintext.decode("utf-8", errors="replace")}
    raise ValueError("Unknown AES operation.")


def _authentication(data):
    message = _text(data, "message", "amount=10").encode("utf-8")
    changed = _text(data, "comparison", "amount=90").encode("utf-8")
    key = _text(data, "key", "shared-demo-key", limit=256).encode("utf-8")
    if not key:
        raise ValueError("Enter a shared HMAC key.")
    tag = hmac_sha256(key, message)
    public, private = generate_keypair(512)
    signature = sign(message, private)
    return {"tag": tag.hex(), "hmac_valid": verify_hmac(key, message, tag),
            "hmac_changed": verify_hmac(key, changed, tag), "signature": str(signature),
            "signature_valid": verify(message, signature, public),
            "signature_changed": verify(changed, signature, public), "public_key": public.to_json()}


def _channel(data):
    message = _text(data, "message", "Hello Bob").encode("utf-8")
    key = _text(data, "key", "shared-demo-authentication-key", limit=256).encode("utf-8")
    if len(key) < 16:
        raise ValueError("The pre-shared key must contain at least 16 UTF-8 bytes.")
    alice, bob = establish_channels(key)
    packet = alice.send(message)
    # Tamper before delivering the original: rejection must not advance the counter.
    altered = replace(packet, tag=bytes([packet.tag[0] ^ 1]) + packet.tag[1:])
    try:
        bob.receive(altered)
        tamper_rejected = False
    except ValueError:
        tamper_rejected = True
    recovered = bob.receive(packet)
    try:
        bob.receive(packet)
        replay_rejected = False
    except ValueError:
        replay_rejected = True
    return {"sequence": packet.sequence, "iv": packet.iv.hex(),
            "ciphertext": packet.ciphertext.hex(), "tag": packet.tag.hex(),
            "recovered": recovered.decode("utf-8"), "tamper_rejected": tamper_rejected,
            "replay_rejected": replay_rejected, "verified": recovered == message}


def _experiments(data):
    kind = _text(data, "kind", "modes")
    if kind == "attacks":
        from experiments.attacks.run import run
        return {"kind": kind, "results": run()}
    if kind == "benchmark":
        from experiments.benchmarks.run import run
        return {"kind": kind, **run(key_sizes=(256,), message_sizes=(16, 256), repeats=3)}
    if kind == "modes":
        message = b"REPEAT!!" * 8
        key = secrets.token_bytes(16)
        ecb = ecb_encrypt(message, key)
        iv, cbc = cbc_encrypt(message, key)
        blocks = lambda value: [value[i:i + 8].hex() for i in range(0, len(value), 8)]
        return {"kind": kind, "plaintext": blocks(message), "ecb": blocks(ecb),
                "cbc": blocks(cbc), "iv": iv.hex(), "block_bytes": 8}
    raise ValueError("Unknown experiment.")


_ACTIONS = {"hash": _hash, "math": _math, "rsa": _rsa, "dh": _dh,
            "aes": _aes, "authentication": _authentication,
            "channel": _channel, "experiments": _experiments}


def run_experiment(request):
    """Validate and execute one JSON-compatible request."""
    if not isinstance(request, dict):
        raise ValueError("The request must be a JSON object.")
    action = request.get("action")
    if not isinstance(action, str) or action not in _ACTIONS:
        raise ValueError("Choose an available experiment.")
    data = request.get("data", {})
    if not isinstance(data, dict):
        raise ValueError("Parameters must be a JSON object.")
    return {"action": action, "result": _ACTIONS[action](data)}
