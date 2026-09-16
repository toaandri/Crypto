# Crypto From Scratch

Bibliothèque Python **éducative** qui reconstruit les mécanismes cryptographiques
des phases 1 à 3 du cahier des charges. Elle utilise uniquement la bibliothèque
standard de Python à l'exécution.

> [!WARNING]
> Ce code sert à apprendre. RSA est sans OAEP, Diffie–Hellman n'authentifie pas
> les participants et le chiffrement de Feistel n'est pas un standard audité.
> N'utilisez jamais ce projet pour protéger des données réelles.

## Avancement

| Phase | Version | Contenu | État |
|---|---:|---|---|
| 1 | V1 | PGCD, Bézout, inverse et exponentiation modulaires | ✅ |
| 1 | V2 | division d'essai, Miller–Rabin, génération de premiers | ✅ |
| 2 | V3 | clés RSA, chiffrement entier, sérialisation JSON | ✅ |
| 2 | V4 | conversion bytes/entiers et messages RSA par blocs | ✅ |
| 2 | V5 | échange Diffie–Hellman et validations | ✅ |
| 3 | V6 | hash pédagogique et SHA‑256 from scratch | ✅ |
| 3 | V7 | mesure reproductible de l'effet avalanche | ✅ |
| 3 | V8 | chiffrement symétrique pédagogique de Feistel | ✅ |
| 3 | V9 | modes ECB, CBC et CTR, padding PKCS#7 | ✅ |

## Installation et tests

```powershell
python -m pip install -e .
python -m pip install pytest
python -m pytest
```

Le projet fonctionne aussi directement depuis sa racine, sans installation.

## Démarrage rapide

```python
from crypto.math import mod_inverse
from crypto.rsa import generate_keypair, encrypt_text, decrypt_text
from crypto.hashes import sha256
from crypto.symmetric import cbc_encrypt, cbc_decrypt

assert mod_inverse(3, 7) == 5

public, private = generate_keypair(256)  # minuscule, démonstration uniquement
encrypted = encrypt_text("Bonjour", public)
assert decrypt_text(encrypted, private) == "Bonjour"

assert sha256(b"abc").hex().startswith("ba7816bf")

key = b"cle-pedagogique!"
iv, ciphertext = cbc_encrypt(b"un message", key)
assert cbc_decrypt(ciphertext, key, iv) == b"un message"
```

## Expériences

```powershell
python -m experiments.avalanche.run
python -m experiments.modes.ecb_vs_cbc
```

La première retourne la proportion moyenne des bits de SHA‑256 modifiés après
le changement d'un bit d'entrée. La seconde montre que des blocs identiques
restent visibles avec ECB, mais pas avec CBC.

## Organisation

```text
crypto/
├── math/             # arithmétique modulaire et nombres premiers
├── rsa/              # RSA brut, clés et encodage par blocs
├── diffie_hellman/   # échange de secret
├── hashes/           # hash faible et SHA-256
└── symmetric/        # Feistel et modes ECB/CBC/CTR
experiments/          # avalanche et comparaison de modes
tests/                # tests unitaires et vecteurs de référence
docs/                 # théorie, algorithmes, limites et usage moderne
```

Pour les explications et limites détaillées, voir [la documentation](docs/README.md).

