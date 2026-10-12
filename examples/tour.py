"""Executable source for the README demonstrations and their GIFs.

Run all: python -m examples.tour. Run one: python -m examples.tour aes.
"""

import argparse
from contextlib import redirect_stdout
from dataclasses import dataclass
import io
from textwrap import dedent


@dataclass(frozen=True)
class Step:
    title: str
    explanation: str
    code: str


@dataclass(frozen=True)
class Scene:
    slug: str
    title: str
    subtitle: str
    steps: tuple[Step, ...]


SCENES = (
    Scene("math", "01 / Mathematical foundations", "V1–V2 · Compute before encrypting", (
        Step("GCD and Bezout", "Euclid finds the GCD. Bezout explains when an inverse exists.", '''
            from crypto.math import gcd, extended_gcd, mod_inverse, mod_pow
            g, x, y = extended_gcd(240, 46)
            assert 240*x + 46*y == g == 2
            print("GCD(240, 46) =", g)
            print("Bezout coefficients:", x, y)
            print("Inverse of 3 modulo 7:", mod_inverse(3, 7))
            print("4**13 modulo 497:", mod_pow(4, 13, 497))
        '''),
        Step("Primes and factors", "Miller-Rabin tests candidates; trial division recovers small factors.", '''
            from crypto.math import generate_prime, is_probable_prime, factorize
            prime = generate_prime(64)
            assert prime.bit_length() == 64
            print("Generated prime:", prime.bit_length(), "bits")
            print("Miller-Rabin test:", is_probable_prime(prime))
            print("Factors of 3233:", factorize(3233))
        '''),
    )),
    Scene("rsa", "02 / RSA: from integers to messages", "V3–V4 · Keys, encoding and reconstruction", (
        Step("A miniature key", "p and q produce n. The inverse of e modulo phi produces d.", '''
            from crypto.rsa import PublicKey, PrivateKey, encrypt_int, decrypt_int
            from crypto.math import mod_inverse
            p, q, e = 61, 53, 17
            public = PublicKey(p*q, e)
            private = PrivateKey(p*q, mod_inverse(e, (p-1)*(q-1)))
            ciphertext = encrypt_int(42, public)
            assert decrypt_int(ciphertext, private) == 42
            print("n =", public.n, "/ d =", private.d)
            print("42 ->", ciphertext, "->", decrypt_int(ciphertext, private))
        '''),
        Step("Text, blocks and JSON", "Encoding preserves bytes and their length. It does not replace OAEP.", '''
            from crypto.rsa import generate_keypair, encrypt_text, decrypt_text
            public, private = generate_keypair(256)
            encrypted = encrypt_text("Bonjour, RSA !", public)
            assert PublicKey.from_json(public.to_json()) == public
            print("Encrypted blocks:", len(encrypted.blocks))
            print("Recovered message:", decrypt_text(encrypted, private))
            print("Public key JSON: round trip OK")
        '''),
    )),
    Scene("dh", "03 / Establish a shared secret", "V5 · Diffie-Hellman, without sending the secret", (
        Step("The public values", "Alice and Bob keep their exponents and exchange only A and B.", '''
            from crypto.diffie_hellman import Party
            alice = Party(prime=23, generator=5, private=6)
            bob = Party(prime=23, generator=5, private=15)
            print("Alice publishes A =", alice.public)
            print("Bob publishes B =", bob.public)
        '''),
        Step("The same result", "Both calculations produce g^(ab) mod p. The peer still needs authentication.", '''
            secret_a = alice.shared_secret(bob.public)
            secret_b = bob.shared_secret(alice.public)
            assert secret_a == secret_b
            print("Alice secret:", secret_a)
            print("Bob secret:  ", secret_b)
            print("Matching secrets:", secret_a == secret_b)
        '''),
    )),
    Scene("hash", "04 / One bit changes the fingerprint", "V6–V7 · SHA-256 and the avalanche effect", (
        Step("A 256-bit fingerprint", "SHA-256 processes 512-bit blocks and produces 32 bytes.", '''
            from crypto.hashes import sha256, SHA256
            digest = sha256(b"abc")
            incremental = SHA256(b"a")
            incremental.update(b"bc")
            assert incremental.digest() == digest
            print("SHA-256 prefix:", digest.hex()[:16])
            print("Size:", len(digest)*8, "bits")
        '''),
        Step("Measure diffusion", "Each bit of Bonjour is flipped separately; changed digest bits are counted.", '''
            from experiments.avalanche.run import measure
            result = measure(b"Bonjour")
            print("Trials:", len(result.samples))
            print("Average:", round(result.average, 2), "/ 256 bits")
            print("Proportion:", round(100*result.average_ratio, 2), "%")
        '''),
    )),
    Scene("aes", "05 / AES, round by round", "V8 · AES-128, AES-192 and AES-256", (
        Step("Reference key and block", "The AES state holds 16 bytes. Key size determines the number of rounds.", '''
            from crypto.symmetric import AES
            key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
            block = bytes.fromhex("00112233445566778899aabbccddeeff")
            cipher = AES(key)
            print("Block:", cipher.block_size, "bytes")
            print("AES-128 rounds:", cipher.rounds)
            print("AES-192 rounds:", AES(bytes(24)).rounds)
            print("AES-256 rounds:", AES(bytes(32)).rounds)
        '''),
        Step("Known vector and round trip", "SubBytes, ShiftRows, MixColumns and AddRoundKey transform the state.", '''
            encrypted = cipher.encrypt_block(block)
            assert encrypted.hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"
            assert cipher.decrypt_block(encrypted) == block
            print("Ciphertext (hex):")
            print(encrypted.hex())
            print("Decryption: original block recovered")
        '''),
    )),
    Scene("modes", "06 / Choose a mode", "V9 · ECB, CBC, CTR and AES-GCM", (
        Step("ECB repetitions", "The same block produces the same ciphertext. CBC chains blocks with an IV.", '''
            from crypto.symmetric import ecb_encrypt, cbc_encrypt, cbc_decrypt
            key, message = b"educational-key", b"REPETE!!" * 3
            ecb = ecb_encrypt(message, key)
            iv, cbc = cbc_encrypt(message, key)
            assert cbc_decrypt(cbc, key, iv) == message
            print("ECB: equal blocks?", ecb[:8] == ecb[8:16])
            print("CBC: equal blocks?", cbc[:8] == cbc[8:16])
        '''),
        Step("CTR: a reversible stream", "CTR applies XOR with the encrypted stream. Never reuse the nonce.", '''
            from crypto.symmetric import ctr_crypt
            nonce = b"demo"
            ciphertext = ctr_crypt(message, key, nonce)
            assert ctr_crypt(ciphertext, key, nonce) == message
            print("No padding:", len(ciphertext) == len(message))
            print("CTR round trip:", ctr_crypt(ciphertext, key, nonce).decode())
        '''),
        Step("GCM: encrypt and authenticate", "The tag protects ciphertext and AAD. Verification precedes decryption.", '''
            from crypto.symmetric import gcm_encrypt, gcm_decrypt
            aes_key = bytes(range(16))
            nonce, ciphertext, tag = gcm_encrypt(b"Bonjour", aes_key, aad=b"Alice")
            plaintext = gcm_decrypt(ciphertext, aes_key, nonce, tag, aad=b"Alice")
            assert plaintext == b"Bonjour"
            print("Message:", plaintext.decode())
            print("Nonce / tag:", len(nonce), "/", len(tag), "bytes")
        '''),
    )),
    Scene("authentication", "07 / Prove and verify", "V10–V11 · HMAC and educational RSA signatures", (
        Step("A shared key, a MAC", "HMAC detects changes. Anyone holding the shared key can create it.", '''
            from crypto.authentication import hmac_sha256, verify_hmac
            key, message = b"shared-demo-key", b"montant=10"
            tag = hmac_sha256(key, message)
            print("Original message:", verify_hmac(key, message, tag))
            print("Changed amount:  ", verify_hmac(key, b"montant=90", tag))
        '''),
        Step("A private key, a signature", "The public key verifies. This RSA demonstration does not implement PSS.", '''
            from crypto.rsa import generate_keypair
            from crypto.signatures import sign, verify
            public, private = generate_keypair(512)
            signature = sign(message, private)
            print("Valid signature:", verify(message, signature, public))
            print("Changed message: ", verify(message+b"!", signature, public))
        '''),
    )),
    Scene("channel", "08 / Alice talks to Bob", "V12 · Authenticate, encrypt and reject replays", (
        Step("Authenticated exchange", "A pre-shared key authenticates the DH transcript. Each direction has its keys.", '''
            from crypto.protocols import establish_channels
            alice, bob = establish_channels(b"cle-prepartagee-de-demonstration")
            packet = alice.send(b"Bonjour Bob")
            print("Bob receives:", bob.receive(packet).decode())
            print("Alice receives:", alice.receive(bob.send(b"Salut Alice")).decode())
        '''),
        Step("Reject replays", "The counter tracks order. A previously accepted packet cannot be read again.", '''
            try:
                bob.receive(packet)
            except ValueError:
                print("Old packet: REJECTED")
        '''),
        Step("Detect tampering", "The recipient verifies the HMAC before decrypting the content.", '''
            from dataclasses import replace
            next_packet = alice.send(b"Message suivant")
            try:
                bob.receive(replace(next_packet, tag=bytes(32)))
            except ValueError:
                print("Changed tag: REJECTED")
            print("Original accepted:", bob.receive(next_packet).decode())
        '''),
    )),
    Scene("attacks", "09 / Break toy parameters", "V13 · Five bounded local experiments", (
        Step("Low entropy and collisions", "Targets are fixed, tiny and local. No external service is tested.", '''
            from experiments.attacks.run import run
            results = run()
            print("Recovered key:", results["brute_force"]["key"])
            print("Password:", results["dictionary"]["password"])
            print("Collision after", results["collision"]["attempts"], "trials")
        '''),
        Step("MITM and factorization", "Unauthenticated DH allows two secrets; RSA factors recover the private key.", '''
            mitm = results["mitm"]
            print("Alice / Bob secret:", mitm["alice_secret"], "/", mitm["bob_secret"])
            print("Mallory intercepts:", mitm["intercepted"])
            rsa = results["factorization"]
            print("RSA factors:", rsa["p"], rsa["q"])
            print("Recovered message:", rsa["recovered_message"])
        '''),
    )),
    Scene("benchmarks", "10 / Measure before concluding", "V14 · Fixed workloads, time and allocations", (
        Step("A small benchmark", "The median summarizes timings. Python allocations are measured separately.", '''
            from experiments.benchmarks.run import run
            report = run(key_sizes=(128,), message_sizes=(16,), repeats=3)
            print("Python:", report["python"])
            print("Measured operations:", len(report["results"]))
            for row in report["results"][:3]:
                milliseconds = round(row["median_seconds"] * 1000, 3)
                print(row["operation"], ":", milliseconds, "ms")
        '''),
        Step("What the numbers mean", "Results depend on the machine. Small keys remain educational.", '''
            row = report["results"][0]
            print("Repetitions:", row["repeats"])
            print("Pic d'allocations Python:", row["peak_python_bytes"], "bytes")
            print("This peak is not process RAM.")
            print("A benchmark is not proof of security.")
        '''),
    )),
)


def execute_scene(scene):
    """Execute each step in one scene-local namespace and capture real stdout."""
    namespace, results = {}, []
    for step in scene.steps:
        output = io.StringIO()
        with redirect_stdout(output):
            exec(compile(dedent(step.code).strip(), f"tour/{scene.slug}", "exec"), namespace)
        results.append(output.getvalue().rstrip())
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", nargs="?", choices=[scene.slug for scene in SCENES])
    args = parser.parse_args()
    for scene in SCENES:
        if args.scene is None or scene.slug == args.scene:
            print(f"\n{scene.title}")
            for step, output in zip(scene.steps, execute_scene(scene)):
                print(f"\n{step.title}\n{output}")


if __name__ == "__main__":
    main()
