
<a id="reference-api"></a>

## Référence des interfaces publiques

Les opérations sur les messages attendent des `bytes`. Pour un texte, utiliser
`.encode("utf-8")` avant et `.decode("utf-8")` après ; RSA possède aussi les
raccourcis `encrypt_text` et `decrypt_text`. Les entiers cryptographiques sont
non signés ; la conversion octets/entiers se fait en ordre big-endian.

### Mathématiques — `crypto.math`

| Interface | Résultat et contrat |
|---|---|
| `gcd(a, b)` | PGCD positif ou nul ; accepte les entiers négatifs |
| `extended_gcd(a, b)` | `(g, x, y)` avec `a*x + b*y == g` |
| `mod_inverse(a, modulus)` | Inverse modulo `modulus > 1` ; `ValueError` si inexistant |
| `mod_pow(base, exponent, modulus)` | Exponentiation rapide, module positif ; exposant négatif via l'inverse |
| `is_prime(n)` | Division d'essai déterministe, destinée aux petits entiers |
| `is_probable_prime(n, rounds=40)` | Sept bases déterministes sous `2**64`, témoins aléatoires au-delà |
| `generate_prime(bits, rounds=40)` | Premier probable impair d'exactement `bits >= 2` bits |
| `factorize(n)` | Facteurs premiers avec multiplicité, `n >= 1` ; `factorize(1) == []` |

Miller–Rabin décompose `n-1 = 2**s * d`. Pour un entier composé fixé et des bases
aléatoires indépendantes, la borne d'acceptation erronée est `4**(-rounds)`.
Ce n'est pas une probabilité a posteriori qu'un nombre accepté soit composé.
La génération utilise `secrets`, pas le générateur pseudo-aléatoire de `random`.

### RSA — `crypto.rsa`

| Interface | Résultat et contrat |
|---|---|
| `generate_keypair(bits=1024, public_exponent=65537)` | `(PublicKey, PrivateKey)` ; modulus d'environ `bits` bits |
| `PublicKey(n, e)` / `PrivateKey(n, d, p=None, q=None)` | Objets immuables ; facteurs privés facultatifs |
| `key.to_json()` / `KeyClass.from_json(text)` | Sérialisation JSON ; privée non chiffrée, facteurs exclus par défaut |
| `private.to_json(include_primes=True)` | Inclut les facteurs privés pour l'étude |
| `encrypt_int(m, public)` / `decrypt_int(c, private)` | RSA brut ; exige `0 <= valeur < n` |
| `encrypt_bytes(message, public)` | `EncryptedMessage(blocks, length)` |
| `decrypt_bytes(encrypted, private)` | Reconstitue les octets, y compris les zéros initiaux |
| `encrypt_text(text, public, encoding="utf-8")` | Encode puis chiffre par blocs |
| `decrypt_text(encrypted, private, encoding="utf-8")` | Déchiffre puis décode |

Le bloc clair mesure `(n.bit_length()-1)//8` octets. La longueur totale est
conservée pour reconstruire le dernier bloc. Ce format ne fournit aucun padding
de sécurité, aucun MAC et aucune confidentialité de la longueur. Les clés JSON
privées sont des secrets en clair. Voir [RSA et OAEP](docs/cryptography/rsa.md).

### Diffie–Hellman — `crypto.diffie_hellman`

| Interface | Résultat et contrat |
|---|---|
| `Party(prime, generator, private=None)` | Valide les paramètres ; choisit un exposant secret si absent |
| `party.public` | Valeur publique `g**a mod p` |
| `party.shared_secret(peer_public)` | Entier partagé ; rejette les valeurs publiques triviales |
| `generate_private_key(prime)` | Exposant uniforme dans `[2, p-2]` ; primalité à valider séparément |
| `public_key(private, prime, generator)` | Calcul de valeur publique avec validation |
| `derive_shared_secret(peer_public, private, prime)` | Calcul du secret partagé avec validation |

Le module général n'authentifie pas le pair et ne garantit pas l'ordre du
sous-groupe choisi. Un entier DH n'est pas directement une clé AES ; le canal
ajoute sa propre dérivation et une authentification prépartagée.

### Hash et authentification

| Import | Interface | Résultat |
|---|---|---|
| `crypto.hashes` | `educational_hash(data)` | Petit hash pédagogique de 32 bits, non cryptographique |
| `crypto.hashes` | `sha256(data)` | Empreinte de 32 octets |
| `crypto.hashes` | `SHA256(data=b"")` | `update`, `digest`, `hexdigest`, `copy` ; conserve les données en mémoire |
| `crypto.authentication` | `hmac_sha256(key, message)` | Tag complet de 32 octets |
| `crypto.authentication` | `verify_hmac(key, message, tag)` | Booléen ; comparaison avec `compare_digest` |
| `crypto.signatures` | `sign(message, private)` | Signature RSA brute d'un condensat SHA-256, sous forme d'entier |
| `crypto.signatures` | `verify(message, signature, public)` | Booléen ; rejette une signature hors intervalle |

La signature exige `n > 2**256-1`, pour contenir tous les condensats possibles.
Elle n'implémente pas RSA-PSS. RSA-PSS, ECDSA et EdDSA sont comparés dans
[l'étude des signatures](docs/cryptography/authentication.md).

### Symétrique — `crypto.symmetric`

| Interface | Taille / résultat |
|---|---|
| `FeistelCipher(key)` | Clé d'au moins 8 octets, blocs de 8 octets, 16 tours |
| `AES(key)` | Clé de 16/24/32 octets, blocs de 16 octets, 10/12/14 tours |
| `cipher.encrypt_block(block)` / `decrypt_block(block)` | Un bloc exact, sans padding ni authentification |
| `pkcs7_pad(data, block_size=8)` / `pkcs7_unpad(...)` | Padding PKCS#7 ; tailles de bloc de 1 à 255 |
| `ecb_encrypt(plaintext, key)` / `ecb_decrypt(ciphertext, key)` | **Feistel** ECB avec PKCS#7 |
| `cbc_encrypt(plaintext, key, iv=None)` | **Feistel** CBC ; renvoie `(iv, ciphertext)`, IV de 8 octets |
| `cbc_decrypt(ciphertext, key, iv)` | Déchiffrement CBC puis retrait du padding |
| `ctr_crypt(data, key, nonce)` | **Feistel** CTR ; nonce de 4 octets et compteur de 32 bits, sans padding |
| `gcm_encrypt(plaintext, key, nonce=None, aad=b"")` | **AES-GCM** ; renvoie `(nonce, ciphertext, tag)` |
| `gcm_decrypt(ciphertext, key, nonce, tag, aad=b"")` | Vérifie le tag puis renvoie le clair, sinon `ValueError` |

GCM génère par défaut un nonce aléatoire de 12 octets. Il prend aussi en charge
les autres longueurs non nulles via GHASH ; les tags doivent faire exactement
16 octets. Les AAD sont authentifiées mais **pas chiffrées**. Conserver nonce,
tag et AAD avec le chiffré. La bibliothèque ne mémorise pas les nonces utilisés :
ne jamais réutiliser un nonce avec la même clé. Un nonce fixe dans un vecteur de
test ou un benchmark ne constitue pas une règle d'utilisation.

AES-GCM utilise le compteur sur 32 bits et le produit dans `GF(2**128)` ; il
rejette les données excédant `2**36-32` octets. Il n'expose pas de clair si le tag
échoue. Détails : [AES et GCM](docs/cryptography/aes_gcm.md).

### Canal — `crypto.protocols`

| Interface | Fonction |
|---|---|
| `Handshake(role, authentication_key)` | Rôle `alice` ou `bob`, clé prépartagée d'au moins 16 octets |
| `handshake.hello` | `Hello(role, public, nonce)` à échanger |
| `handshake.proof(peer_hello)` | HMAC du transcript canonique et du rôle émetteur |
| `handshake.finish(peer_hello, peer_proof)` | Vérifie la preuve et crée un `SecureChannel` ; usage unique |
| `establish_channels(key)` | Raccourci de simulation : `(alice_channel, bob_channel)` |
| `channel.send(message)` | `Packet(sequence, iv, ciphertext, tag)` |
| `channel.receive(packet)` | Vérifie ordre et tag, déchiffre, puis avance le compteur |

Le canal utilise DH + **Feistel-CBC + HMAC**, avec des clés séparées par direction
et fonction. AES-GCM est disponible séparément pour comparer les constructions.
Le transcript lie les deux nonces, les valeurs DH, les paramètres et les rôles.
Les tests couvrent altération, réflexion, autre session, rejeu et mauvais ordre.
Les paquets doivent être livrés dans l'ordre. Aucun réseau, certificat,
stockage de session ni accès concurrent n'est implémenté : le cahier des charges
demande une simulation. Voir [le protocole détaillé](docs/cryptography/secure_channel.md).

<a id="experiences"></a>

## Expériences et résultats

![Mesures de factorisation, primalité, avalanche et génération RSA](docs/assets/science.png)

Les [données JSON](docs/results/science.json) contiennent les entrées, paramètres,
mesures et métadonnées de la machine. Les [rapports A–F](docs/experiments.md)
présentent hypothèse, protocole, données, résultats, interprétation et conclusion.
Les durées sont des observations locales ; aucune performance universelle n'est
promise.

| Expérience | Ce qui est mesuré / observé |
|---|---|
| A · Taille RSA | Génération de clés de 512, 1024 et 2048 bits |
| B · Factorisation | Division d'essai sur six semipremiers croissants |
| C · Avalanche | Un bit modifié, trois messages et distribution des distances |
| D · ECB/CBC | Même matrice répétitive, comparaison des blocs chiffrés |
| E · DH et MITM | Deux secrets connus de Mallory dans un échange non authentifié |
| F · Paramètres | Primalité, nombre de témoins, tailles DH, AES-GCM, temps et mémoire |

![Matrice de blocs : motifs du clair conservés en ECB et masqués en CBC](docs/assets/ecb-cbc.png)

Chaque cellule représente **un bloc de 8 octets**, avec une couleur par valeur
distincte ; ce n'est pas une image directement chiffrée pixel par pixel. Le
padding est exclu. Les données fixes donnent 2 blocs distincts en clair et en
ECB, contre 256 pour CBC dans cette expérience. Cela illustre les répétitions,
sans prouver la sécurité de Feistel ni de CBC.

### Toutes les commandes

```powershell
# Parcours complet, ou une demonstration : math, rsa, dh, hash, aes,
# modes, authentication, channel, attacks, benchmarks
python -m examples.tour
python -m examples.tour aes

# Demonstrations autonomes
python -m examples.authentication
python -m examples.aes_gcm
python -m examples.secure_channel
python -m experiments.avalanche.run
python -m experiments.modes.ecb_vs_cbc
python -m experiments.attacks.run

# Benchmarks RSA / SHA-256 / Feistel : sortie JSON
python -m experiments.benchmarks.run --key-sizes 512 1024 2048 --message-sizes 16 256 1024 --repeats 3

# Donnees completes A-F, primalite, DH et AES-GCM
python -m experiments.science.run --repeats 3

# Variante rapide, sans les benchmarks RSA et AES-GCM
python -m experiments.science.run --quick --output docs/results/quick.json

# Reconstruction des GIFs, images, graphiques et README
python -m scripts.build_docs
```

Les benchmarks réalisent une chauffe, puis plusieurs mesures avec
`perf_counter`. Une exécution séparée sous `tracemalloc` mesure les allocations
Python sans perturber les durées. Les pics n'incluent ni toute la RAM du
processus ni toutes les allocations natives. Les messages sont fixes ; les clés
RSA et les témoins probabilistes sont aléatoires. Pour comparer deux machines,
conserver paramètres, répétitions et versions, et lire les médianes avec prudence.

<a id="validation"></a>

## Tests et vérification

```powershell
python -m pytest
python -m scripts.verify_docs
```

| Domaine | Vérifications |
|---|---|
| Mathématiques | Identités, inverses, primalité, composites de Carmichael, facteurs |
| RSA | Entiers, blocs, Unicode, zéros initiaux, clés JSON et données invalides |
| DH | Secrets égaux, paramètres et valeurs publiques invalides |
| SHA-256 / HMAC | Vecteurs connus, frontières de blocs et comparaison à `hashlib` / `hmac` |
| AES | Vecteurs FIPS 197 pour 128/192/256 bits et comparaison indépendante |
| AES-GCM | Vecteurs connus, blocs partiels, AAD, plusieurs tailles de nonce, tags altérés |
| Feistel / modes | Inversion, répétitions ECB, CBC, CTR et padding |
| Signatures | Message altéré, mauvaise clé, signature hors intervalle |
| Protocole | Authentification du transcript, intégrité avant déchiffrement, rejeu, ordre et session |
| Expériences | Facteurs retrouvés, vraie collision tronquée, secrets MITM et rapports |
| Documentation | Exemples exécutés, liens locaux, GIFs multi-images et sorties présentes |

Les comparaisons AES/GCM à `cryptography` sont activées par l'extra `[test]` ;
sans cette dépendance, pytest les marque comme ignorées. Les vecteurs connus
restent exécutés. Le workflow [CI](.github/workflows/tests.yml) installe l'extra
et lance les tests sous Python 3.10, 3.12 et 3.14. Les GIFs sont générés localement
depuis les mêmes exemples que ceux vérifiés dans les tests.

## Organisation et contribution

```text
crypto/
  math/              Euclide, primalité et factorisation
  rsa/               Clés, RSA brut et messages par blocs
  diffie_hellman/     Échange de secret
  hashes/            Hash pédagogique et SHA-256
  symmetric/         Feistel, AES, ECB/CBC/CTR et GCM
  authentication/    HMAC-SHA256
  signatures/        Signature RSA pédagogique
  protocols/         Handshake et canal en mémoire
examples/            Démonstrations et source du parcours animé
experiments/         Avalanche, modes, attaques, benchmarks et études A-F
tests/               Tests unitaires, vecteurs et comparaisons indépendantes
scripts/             Génération et vérification documentaire
docs/
  assets/            GIFs, images fixes et graphiques
  results/           Données expérimentales et sorties des exemples
  cryptography/      Explications des algorithmes
  mathematics/       Fondations mathématiques
  security/          Limites et expériences d'attaques
```

Pour modifier une démonstration, éditer `examples/tour.py`. Le README est généré
à partir de ces exemples et de `docs/readme_header.md` / `docs/readme_footer.md`.
Après modification, lancer les tests puis `python -m scripts.build_docs` et
`python -m scripts.verify_docs`. Les dépendances graphiques restent facultatives
et ne doivent jamais entrer dans `crypto/`. Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Limites et différences avec un système réel

| Ici | Dans une application réelle |
|---|---|
| Petites clés RSA et RSA brut | Primitives auditées et encodage OAEP/PSS approprié |
| DH jouet et clé prépartagée de démonstration | Paramètres reconnus, identités vérifiées et protocole établi |
| Feistel inventé, blocs de 64 bits | Chiffrement authentifié standard via une bibliothèque auditée |
| AES et GCM en Python, tables et branches | Implémentation auditée et protections contre les canaux auxiliaires |
| Clés en mémoire et JSON en clair | Gestion, stockage et rotation des secrets adaptés |
| Compteurs en mémoire, simulation locale | Transport, persistance et gestion des sessions |

Une conformité aux vecteurs de test ne constitue ni un audit, ni une
certification NIST, ni une preuve de résistance aux attaques. La comparaison
du HMAC utilise `compare_digest`, mais le programme entier n'est pas à temps
constant. Les détails sont dans [les limites de sécurité](docs/security/limitations.md).

## Références et licence

- [FIPS 197 — AES](https://csrc.nist.gov/pubs/fips/197/final) : structure, expansion de clé et tours.
- [NIST SP 800-38D — GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final) : compteur, GHASH et authentification.
- [FIPS 180-4 — SHA-256](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) : fonctions de hachage.
- [RFC 2104 — HMAC](https://www.rfc-editor.org/rfc/rfc2104) et [RFC 4231 — vecteurs HMAC](https://www.rfc-editor.org/rfc/rfc4231).
- [RFC 8017 — RSA, OAEP et PSS](https://www.rfc-editor.org/rfc/rfc8017).
- [RFC 8032 — EdDSA](https://www.rfc-editor.org/rfc/rfc8032).
- [Cahier des charges original](maharavo.txt) et [documentation complète](docs/README.md).

Code et ressources générées distribués sous [licence MIT](LICENSE).
