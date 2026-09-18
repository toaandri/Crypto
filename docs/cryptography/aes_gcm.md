# AES et GCM : du bloc à un message authentifié

## Le problème

Un chiffrement par blocs transforme une entrée de taille fixe. Pour des messages
de longueur quelconque, il faut un mode ; pour refuser les modifications, il
faut également une authentification. AES fournit le premier mécanisme, GCM les
deux suivants. Ici ils sont implémentés directement dans `aes.py` et `gcm.py`.

## AES : mathématiques et algorithme

AES travaille sur 16 octets organisés en quatre colonnes de quatre lignes.
Les clés de 16, 24 et 32 octets donnent respectivement 10, 12 et 14 tours. Le
calendrier de clés produit une sous-clé de 16 octets pour chaque tour.

- **SubBytes** : inversion dans `GF(2**8)`, puis transformation affine. La S-box
  est calculée par le code et non recopiée dans une table de constantes.
- **ShiftRows** : décalage circulaire de chaque ligne, suivant son indice.
- **MixColumns** : produit matriciel par colonne dans `GF(2**8)`, avec réduction
  modulo `x**8 + x**4 + x**3 + x + 1` (`0x11b`).
- **AddRoundKey** : XOR entre l'état et la sous-clé.

On applique une addition de clé initiale, les tours complets, puis un dernier
tour sans MixColumns. Le déchiffrement applique les opérations inverses dans
l'ordre approprié. L'expansion emploie RotWord, SubWord et Rcon, avec une
SubWord supplémentaire pour certaines étapes d'AES-256.

`AES(key).encrypt_block(block)` et `decrypt_block(block)` imposent exactement
16 octets de bloc. Ces méthodes ne fournissent ni padding, ni IV, ni MAC.
`python -m examples.tour aes` reproduit le vecteur de démonstration FIPS 197 :
clé `000102030405060708090a0b0c0d0e0f`, bloc
`00112233445566778899aabbccddeeff`, résultat
`69c4e0d86a7b0430d8cdb78070b4c55a`.

## GCM : compteur et GHASH

GCM chiffre avec AES en mode compteur et calcule un tag sur les données
associées (AAD), le chiffré et leurs longueurs. L'authentificateur GHASH travaille
dans `GF(2**128)` modulo `x**128 + x**7 + x**2 + x + 1`. Le code respecte l'ordre
de bits de SP 800-38D, avec la constante de réduction `0xe1 << 120`.

1. Calculer `H = AES_K(0**128)`.
2. Pour un nonce de 96 bits, former `J0 = nonce || 0**31 || 1`. Pour une autre
   longueur non nulle, calculer J0 avec GHASH et la longueur du nonce.
3. Incrémenter les 32 bits de poids faible du compteur, chiffrer le compteur,
   puis combiner avec le clair par XOR. Le dernier bloc peut être partiel.
4. Calculer GHASH sur les AAD complétées, le chiffré complété et leurs longueurs
   en bits sur 64 bits chacune. Combiner avec `AES_K(J0)` pour former le tag.
5. Lors de la réception, vérifier le tag complet avec `compare_digest` avant
   d'appeler le traitement compteur qui restitue le clair.

Les zéros ajoutés à GHASH ne sont pas du padding ajouté au message chiffré.
Le chiffré conserve la longueur du clair. L'API ne prend en charge que les tags
complets de 128 bits, ce qui est un sous-ensemble explicite de SP 800-38D.

```python
from crypto.symmetric import gcm_encrypt, gcm_decrypt

key = bytes(range(32))  # uniquement pour la démonstration
nonce, ciphertext, tag = gcm_encrypt(b"Bonjour", key, aad=b"type=message")
assert gcm_decrypt(ciphertext, key, nonce, tag, b"type=message") == b"Bonjour"
```

## Tests et limites

Les tests utilisent les trois tailles de clé, les vecteurs AES FIPS 197, deux
vecteurs GCM connus (message vide et bloc nul), puis des comparaisons avec
`cryptography` sur des longueurs partielles, plusieurs nonces et des AAD.
Les modifications de la clé, du nonce, du tag, des AAD et du chiffré sont
refusées ; un test vérifie que le déchiffrement n'est pas appelé avant le MAC.

Le nonce doit être unique pour une clé. Sa réutilisation révèle des relations
entre clairs et compromet l'authentification. L'API ne suit pas l'historique des
nonces ; elle génère 12 octets aléatoires si le nonce n'est pas fourni. Aucune
gestion de quotas, de clés ou de persistance n'est proposée.

Python, les branches et les tables ne fournissent pas de protection contre les
canaux auxiliaires. La conformité aux vecteurs n'est pas une certification.
Les modes ECB/CBC/CTR historiques du dépôt utilisent Feistel ; ils ne sont pas
des alias AES. Le canal V12 conserve Feistel-CBC avec HMAC, pour illustrer la
composition encrypt-then-MAC séparément de l'AEAD GCM.

Références : [FIPS 197](https://csrc.nist.gov/pubs/fips/197/final) et
[SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final).
