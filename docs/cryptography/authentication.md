# Phase 4 — Authentification et signatures

## V10 : HMAC et intégrité

Chiffrer masque le contenu. Un hash seul détecte une différence seulement si son
empreinte de référence est fiable : un attaquant peut remplacer message et hash.
Un MAC ajoute une clé secrète et permet aux détenteurs de cette clé de vérifier
l'origine et l'intégrité du message. Il ne chiffre rien.

HMAC-SHA256 calcule `H((K' xor opad) || H((K' xor ipad) || message))`.
Le bloc de SHA-256 mesure 64 octets. Une clé plus longue est d'abord hachée ; elle
est ensuite complétée de zéros jusqu'à 64 octets. Les masques sont `0x36` et
`0x5c`. Le résultat complet mesure 32 octets. La construction imbriquée évite
les problèmes d'une construction naïve `SHA256(clé || message)`.

`crypto.authentication.hmac_sha256` réutilise notre SHA-256, sans déléguer HMAC
à une bibliothèque. `verify_hmac` compare les tags avec `secrets.compare_digest`.
Cela ne rend pas tout le programme Python à temps constant.

```python
from crypto.authentication import hmac_sha256, verify_hmac

key = b"cle-partagee-de-demonstration"
tag = hmac_sha256(key, b"montant=10")
assert verify_hmac(key, b"montant=10", tag)
assert not verify_hmac(key, b"montant=90", tag)
```

Les tests couvrent un vecteur RFC 4231, les clés longues, les entrées vides, les
tags tronqués et la comparaison avec `hmac`/`hashlib` de Python. La clé doit être
secrète et suffisamment aléatoire ; un MAC ne permet pas de distinguer lequel
des détenteurs de la clé a écrit un message. Il ne bloque pas seul les rejeux.

## V11 : signature RSA pédagogique

Une signature utilise une clé privée pour produire une preuve vérifiable avec
la clé publique. Ici `h = entier(SHA256(message))`, `s = h^d mod n`, puis on
vérifie `s^e mod n == h`. Le module refuse les petits moduli qui ne peuvent pas
contenir tous les condensats de 256 bits, plutôt que de réduire le hash modulo n.
Une clé de démonstration de 512 bits suffit à cet exemple, pas à un usage réel.

```python
from crypto.rsa import generate_keypair
from crypto.signatures import sign, verify

public, private = generate_keypair(512)
signature = sign(b"Bonjour", private)
assert verify(b"Bonjour", signature, public)
assert not verify(b"Bonjour!", signature, public)
```

Les tests contrôlent la formule avec `pow` et `hashlib`, une autre clé et un
message altéré. Cette formule ne constitue pas une implémentation de RSA-PSS et
n'est pas interopérable avec une API de signature RSA moderne. Une signature ne
cache pas le message ; la clé publique doit aussi être associée de façon fiable
à son propriétaire.

RSA-PSS ajoute un encodage probabiliste avec sel et masque avant l'opération RSA.
ECDSA repose sur les courbes elliptiques et exige un nonce de signature correct :
sa réutilisation peut révéler la clé privée. EdDSA utilise des courbes d'Edwards
et une dérivation déterministe du nonce. Ces mécanismes sont étudiés ici
conceptuellement, sans nouvelle implémentation. En pratique, utiliser les API
auditées pour signer et séparer les clés de chiffrement et de signature.
