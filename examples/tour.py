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
    Scene("math", "01 / Les fondations mathématiques", "V1–V2 · Calculer avant de chiffrer", (
        Step("PGCD et Bézout", "Euclide trouve le PGCD. Bézout explique quand un inverse existe.", '''
            from crypto.math import gcd, extended_gcd, mod_inverse, mod_pow
            g, x, y = extended_gcd(240, 46)
            assert 240*x + 46*y == g == 2
            print("PGCD(240, 46) =", g)
            print("Coefficients de Bezout :", x, y)
            print("Inverse de 3 modulo 7 :", mod_inverse(3, 7))
            print("4**13 modulo 497 :", mod_pow(4, 13, 497))
        '''),
        Step("Premiers et facteurs", "Miller–Rabin teste les candidats ; la division retrouve les petits facteurs.", '''
            from crypto.math import generate_prime, is_probable_prime, factorize
            prime = generate_prime(64)
            assert prime.bit_length() == 64
            print("Premier genere :", prime.bit_length(), "bits")
            print("Test Miller-Rabin :", is_probable_prime(prime))
            print("Facteurs de 3233 :", factorize(3233))
        '''),
    )),
    Scene("rsa", "02 / RSA : du nombre au message", "V3–V4 · Clés, encodage et reconstruction", (
        Step("Une clé miniature", "p et q donnent n. L'inverse de e modulo phi donne d.", '''
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
        Step("Texte, blocs et JSON", "L'encodage préserve les octets et leur longueur. Il ne remplace pas OAEP.", '''
            from crypto.rsa import generate_keypair, encrypt_text, decrypt_text
            public, private = generate_keypair(256)
            encrypted = encrypt_text("Bonjour, RSA !", public)
            assert PublicKey.from_json(public.to_json()) == public
            print("Blocs chiffres :", len(encrypted.blocks))
            print("Message retrouve :", decrypt_text(encrypted, private))
            print("Cle publique JSON : aller-retour OK")
        '''),
    )),
    Scene("dh", "03 / Établir un secret commun", "V5 · Diffie–Hellman, sans envoyer le secret", (
        Step("Les valeurs publiques", "Alice et Bob conservent leurs exposants et échangent seulement A et B.", '''
            from crypto.diffie_hellman import Party
            alice = Party(prime=23, generator=5, private=6)
            bob = Party(prime=23, generator=5, private=15)
            print("Alice publie A =", alice.public)
            print("Bob publie B =", bob.public)
        '''),
        Step("Le même résultat", "Les deux calculs donnent g^(ab) mod p. L'identité du pair reste à vérifier.", '''
            secret_a = alice.shared_secret(bob.public)
            secret_b = bob.shared_secret(alice.public)
            assert secret_a == secret_b
            print("Secret Alice :", secret_a)
            print("Secret Bob   :", secret_b)
            print("Secrets identiques :", secret_a == secret_b)
        '''),
    )),
    Scene("hash", "04 / Un bit change l'empreinte", "V6–V7 · SHA-256 et effet avalanche", (
        Step("Une empreinte de 256 bits", "SHA-256 traite des blocs de 512 bits et produit 32 octets.", '''
            from crypto.hashes import sha256, SHA256
            digest = sha256(b"abc")
            incremental = SHA256(b"a")
            incremental.update(b"bc")
            assert incremental.digest() == digest
            print("Debut du SHA-256 :", digest.hex()[:16])
            print("Taille :", len(digest)*8, "bits")
        '''),
        Step("Mesurer la diffusion", "Chaque bit de Bonjour est modifié séparément ; on compte les bits différents.", '''
            from experiments.avalanche.run import measure
            result = measure(b"Bonjour")
            print("Essais :", len(result.samples))
            print("Moyenne :", round(result.average, 2), "/ 256 bits")
            print("Proportion :", round(100*result.average_ratio, 2), "%")
        '''),
    )),
    Scene("aes", "05 / AES, tour après tour", "V8 · AES-128, AES-192 et AES-256", (
        Step("Clé et bloc de référence", "L'état AES contient 16 octets. La taille de clé détermine le nombre de tours.", '''
            from crypto.symmetric import AES
            key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
            block = bytes.fromhex("00112233445566778899aabbccddeeff")
            cipher = AES(key)
            print("Bloc :", cipher.block_size, "octets")
            print("Tours AES-128 :", cipher.rounds)
            print("Tours AES-192 :", AES(bytes(24)).rounds)
            print("Tours AES-256 :", AES(bytes(32)).rounds)
        '''),
        Step("Vecteur connu et retour", "SubBytes, ShiftRows, MixColumns et AddRoundKey transforment l'état.", '''
            encrypted = cipher.encrypt_block(block)
            assert encrypted.hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"
            assert cipher.decrypt_block(encrypted) == block
            print("Chiffre (hex) :")
            print(encrypted.hex())
            print("Dechiffrement : bloc initial retrouve")
        '''),
    )),
    Scene("modes", "06 / Choisir un mode", "V9 · ECB, CBC, CTR et AES-GCM", (
        Step("Les répétitions d'ECB", "Le même bloc donne le même chiffré. CBC chaîne les blocs avec un IV.", '''
            from crypto.symmetric import ecb_encrypt, cbc_encrypt, cbc_decrypt
            key, message = b"educational-key", b"REPETE!!" * 3
            ecb = ecb_encrypt(message, key)
            iv, cbc = cbc_encrypt(message, key)
            assert cbc_decrypt(cbc, key, iv) == message
            print("ECB : blocs egaux ?", ecb[:8] == ecb[8:16])
            print("CBC : blocs egaux ?", cbc[:8] == cbc[8:16])
        '''),
        Step("CTR : un flux réversible", "CTR applique un XOR avec le flux chiffré. Ne jamais réutiliser le nonce.", '''
            from crypto.symmetric import ctr_crypt
            nonce = b"demo"
            ciphertext = ctr_crypt(message, key, nonce)
            assert ctr_crypt(ciphertext, key, nonce) == message
            print("Sans padding :", len(ciphertext) == len(message))
            print("Retour CTR :", ctr_crypt(ciphertext, key, nonce).decode())
        '''),
        Step("GCM : chiffrer et authentifier", "Le tag protège le chiffré et l'en-tête AAD. Il est vérifié avant déchiffrement.", '''
            from crypto.symmetric import gcm_encrypt, gcm_decrypt
            aes_key = bytes(range(16))
            nonce, ciphertext, tag = gcm_encrypt(b"Bonjour", aes_key, aad=b"Alice")
            plaintext = gcm_decrypt(ciphertext, aes_key, nonce, tag, aad=b"Alice")
            assert plaintext == b"Bonjour"
            print("Message :", plaintext.decode())
            print("Nonce / tag :", len(nonce), "/", len(tag), "octets")
        '''),
    )),
    Scene("authentication", "07 / Prouver et vérifier", "V10–V11 · HMAC et signature RSA pédagogique", (
        Step("Une clé partagée, un MAC", "HMAC détecte un changement. Tous les détenteurs de la clé peuvent le produire.", '''
            from crypto.authentication import hmac_sha256, verify_hmac
            key, message = b"shared-demo-key", b"montant=10"
            tag = hmac_sha256(key, message)
            print("Message original :", verify_hmac(key, message, tag))
            print("Montant modifie  :", verify_hmac(key, b"montant=90", tag))
        '''),
        Step("Une clé privée, une signature", "La clé publique vérifie. Cette démonstration RSA n'implémente pas PSS.", '''
            from crypto.rsa import generate_keypair
            from crypto.signatures import sign, verify
            public, private = generate_keypair(512)
            signature = sign(message, private)
            print("Signature valide :", verify(message, signature, public))
            print("Message modifie   :", verify(message+b"!", signature, public))
        '''),
    )),
    Scene("channel", "08 / Alice parle à Bob", "V12 · Authentifier, chiffrer, contrôler le rejeu", (
        Step("Échange authentifié", "Une clé prépartagée authentifie le transcript DH. Chaque direction a ses clés.", '''
            from crypto.protocols import establish_channels
            alice, bob = establish_channels(b"cle-prepartagee-de-demonstration")
            packet = alice.send(b"Bonjour Bob")
            print("Bob recoit :", bob.receive(packet).decode())
            print("Alice recoit :", alice.receive(bob.send(b"Salut Alice")).decode())
        '''),
        Step("Rejeter le rejeu", "Le compteur mémorise l'ordre. Un paquet déjà accepté ne peut pas être relu.", '''
            try:
                bob.receive(packet)
            except ValueError:
                print("Ancien paquet : REJETE")
        '''),
        Step("Détecter l'altération", "Le destinataire vérifie le HMAC avant de déchiffrer le contenu.", '''
            from dataclasses import replace
            next_packet = alice.send(b"Message suivant")
            try:
                bob.receive(replace(next_packet, tag=bytes(32)))
            except ValueError:
                print("Tag modifie : REJETE")
            print("Original accepte :", bob.receive(next_packet).decode())
        '''),
    )),
    Scene("attacks", "09 / Casser des paramètres jouets", "V13 · Cinq expériences locales et bornées", (
        Step("Faible entropie et collisions", "Les cibles sont fixes, minuscules et locales. Aucun service externe n'est testé.", '''
            from experiments.attacks.run import run
            results = run()
            print("Cle retrouvee :", results["brute_force"]["key"])
            print("Mot de passe :", results["dictionary"]["password"])
            print("Collision apres", results["collision"]["attempts"], "essais")
        '''),
        Step("MITM et factorisation", "Un DH sans identité permet deux secrets ; les facteurs RSA redonnent la clé.", '''
            mitm = results["mitm"]
            print("Secret Alice / Bob :", mitm["alice_secret"], "/", mitm["bob_secret"])
            print("Mallory intercepte :", mitm["intercepted"])
            rsa = results["factorization"]
            print("Facteurs RSA :", rsa["p"], rsa["q"])
            print("Message retrouve :", rsa["recovered_message"])
        '''),
    )),
    Scene("benchmarks", "10 / Mesurer avant de conclure", "V14 · Charges fixes, temps et allocations", (
        Step("Un petit benchmark", "La médiane résume les durées. La mémoire Python est mesurée séparément.", '''
            from experiments.benchmarks.run import run
            report = run(key_sizes=(128,), message_sizes=(16,), repeats=3)
            print("Python :", report["python"])
            print("Operations mesurees :", len(report["results"]))
            for row in report["results"][:3]:
                milliseconds = round(row["median_seconds"] * 1000, 3)
                print(row["operation"], ":", milliseconds, "ms")
        '''),
        Step("Ce que les chiffres signifient", "Les résultats dépendent de la machine. Les petites clés restent pédagogiques.", '''
            row = report["results"][0]
            print("Repetitions :", row["repeats"])
            print("Pic d'allocations Python :", row["peak_python_bytes"], "octets")
            print("Ce pic n'est pas la RAM du processus.")
            print("Un benchmark n'est pas une preuve de securite.")
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
