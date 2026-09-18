# Couverture du cahier des charges

Cette matrice couvre [le texte original](../maharavo.txt), y compris AES avancé,
GCM pratique et les expériences A–F. « Réalisé » décrit un projet éducatif
testable, pas une garantie de sécurité en production.

| Exigence | Implémentation / livrable | Vérification |
|---|---|---|
| V1 · PGCD, Bézout, inverse, puissance | [math](../crypto/math/modular.py) | [tests](../tests/test_modular.py) |
| V2 · Essai, Miller–Rabin, génération | [primes](../crypto/math/primes.py) | [tests](../tests/test_primes.py), étude de primalité |
| Fondations · Factorisation | [factorization](../crypto/math/factorization.py) | [tests](../tests/test_factorization.py), expérience B |
| V3 · Clés, RSA, JSON | [rsa](../crypto/rsa/core.py), [keys](../crypto/rsa/keys.py) | [tests](../tests/test_rsa.py) |
| V4 · Texte, octets, blocs, reconstruction | [encoding](../crypto/rsa/encoding.py) | Unicode, zéros initiaux et blocs invalides |
| V5 · DH et tailles de paramètres | [exchange](../crypto/diffie_hellman/exchange.py) | [tests](../tests/test_diffie_hellman.py), groupes 16/32/64/128 bits |
| V6 · Hash pédagogique et SHA-256 | [hashes](../crypto/hashes/sha256.py) | [tests](../tests/test_hashes.py), hashlib |
| V7 · Avalanche et statistiques | [avalanche](../experiments/avalanche/run.py) | [tests](../tests/test_avalanche.py), expérience C |
| V8 · Symétrique pédagogique | [feistel](../crypto/symmetric/feistel.py) | [tests](../tests/test_symmetric.py) |
| V8 avancé · AES complet | [AES](../crypto/symmetric/aes.py) | [AES-128/192/256](../tests/test_aes_gcm.py), vecteurs et référence |
| V9 · ECB/CBC/CTR, padding | [modes](../crypto/symmetric/modes.py) | [tests](../tests/test_symmetric.py), matrice de blocs |
| V9 · GCM conceptuel et pratique | [GCM](../crypto/symmetric/gcm.py), [explication](cryptography/aes_gcm.md) | [tests](../tests/test_aes_gcm.py), AAD et rejets |
| V10 · HMAC et intégrité | [HMAC](../crypto/authentication/hmac.py) | [tests](../tests/test_authentication.py), RFC 4231 et hmac |
| V11 · Signature RSA éducative | [signature](../crypto/signatures/rsa.py) | [tests](../tests/test_signatures.py) |
| V11 · RSA-PSS, ECDSA, EdDSA conceptuels | [étude](cryptography/authentication.md) | Comparaison des mécanismes et limites documentées |
| V12 · Communication simulée | [canal](../crypto/protocols/secure_channel.py) | [tests](../tests/test_secure_channel.py), exemples Alice/Bob |
| V13 · Cinq attaques locales | [attaques](../experiments/attacks/run.py) | [tests](../tests/test_phase5_experiments.py) |
| V14 · Temps, tailles et mémoire | [benchmarks](../experiments/benchmarks/run.py), [science](../experiments/science/run.py) | Mesures séparées, paramètres et JSON conservés |
| Expériences A–F | [rapport](experiments.md), [données](results/science.json) | [tests des études](../tests/test_science.py), figures reproductibles |
| Documentation et exemples | [README](../README.md), [parcours](../examples/tour.py) | [vérification](../scripts/verify_docs.py), GIFs et alternatives fixes |
| Installation et collaboration | [pyproject](../pyproject.toml), [contribution](../CONTRIBUTING.md) | [workflow CI](../.github/workflows/tests.yml) |

## Périmètre explicite

La demande conceptuelle pour RSA-PSS, ECDSA et EdDSA est remplie par l'étude
documentaire ; le projet ne prétend pas implémenter ces trois schémas.
RSA-OAEP est expliqué pour montrer les limites du RSA brut, conformément à la
demande initiale. Les visualisations de modes utilisent une matrice répétitive,
l'une des deux formes proposées dans le cahier des charges.

La communication est une simulation en mémoire ; le transport réseau et une
infrastructure de certificats ne font pas partie du livrable demandé. Les
exemples couvrent maintenant chaque famille au travers du parcours exécutable,
sans imposer exactement l'arborescence indicative du cahier des charges.

La CI est ajoutée au dépôt et s'exécutera lors d'un push sur GitHub. Son ajout
ne signifie pas qu'une exécution distante a déjà eu lieu.
