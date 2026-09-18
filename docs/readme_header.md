<div align="center">

# Crypto From Scratch

**Comprendre les nombres. Construire les algorithmes. Observer leurs limites.**

Python 3.10+ · Bibliothèque standard à l'exécution · V1–V14 · Licence MIT

[Démarrer](#installation) · [Parcours animé](#parcours-anime) · [API](#reference-api) · [Expériences](#experiences) · [Tests](#validation) · [Documentation](docs/README.md)

</div>

Une bibliothèque cryptographique éducative en Python, des premières identités
modulaires jusqu'à un échange authentifié entre Alice et Bob. Les algorithmes
sont écrits dans le projet : RSA, Diffie–Hellman, SHA-256, HMAC, Feistel,
**AES-128/192/256 et AES-GCM**. Les bibliothèques externes servent à vérifier les
résultats et à fabriquer la documentation, pas à effectuer les opérations du
package `crypto`.

> [!WARNING]
> Projet d'apprentissage, **pas une bibliothèque de production**. Les exemples
> utilisent volontairement de petites clés. RSA est sans OAEP/PSS, le canal
> conserve son Feistel pédagogique et son petit groupe DH. Même l'AES conforme
> aux vecteurs de référence n'est pas une implémentation auditée ou à temps
> constant. Ne pas utiliser ce code pour protéger des données réelles.

## Ce que contient le projet

| Phase | Versions | Réalisation |
|---|---|---|
| 1 · Mathématiques | V1–V2 | Euclide, Bézout, inverse, exponentiation, primalité, génération et factorisation |
| 2 · Asymétrique | V3–V5 | RSA entier et messages par blocs, clés JSON, Diffie–Hellman |
| 3 · Hash et symétrique | V6–V9 | Hash faible, SHA-256, avalanche, Feistel, AES, ECB/CBC/CTR et GCM |
| 4 · Authentification | V10–V11 | HMAC-SHA256, signature RSA pédagogique, étude des signatures modernes |
| 5 · Système complet | V12–V14 | Canal authentifié, cinq attaques locales, benchmarks et expériences A–F |

La [matrice du cahier des charges](docs/completion.md) relie chaque exigence au
code, aux tests et aux résultats. RSA-PSS, ECDSA et EdDSA sont étudiés au niveau
conceptuel demandé ; ils ne sont pas exposés comme des implémentations du dépôt.

<a id="installation"></a>

## Installation

Depuis la racine du dépôt, avec Python 3.10 ou plus récent :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test,docs]"
python -m pytest
```

Sous Linux/macOS, activer l'environnement avec `source .venv/bin/activate`.
L'installation minimale `python -m pip install -e .` n'ajoute aucune dépendance
d'exécution. Le code fonctionne aussi depuis la racine sans installation.

| Option | Contenu | Utilité |
|---|---|---|
| Aucun extra | Bibliothèque standard | Exécuter les algorithmes et les exemples |
| `[test]` | pytest, cryptography | Tests et comparaisons AES/GCM indépendantes |
| `[docs]` | Pillow, Matplotlib | Régénérer les GIFs, images et graphiques |

## Essayer en une minute

```powershell
python -m examples.aes_gcm
python -m examples.secure_channel
python -m experiments.attacks.run
```

Le premier vérifie un bloc AES et chiffre un message avec GCM. Le deuxième
montre Alice et Bob communiquer, puis détecte une altération et un rejeu. Le
troisième casse cinq constructions volontairement faibles, entièrement en local.

<a id="parcours-anime"></a>

## Le projet expliqué en dix animations

Chaque GIF montre du **code exécuté et sa sortie réelle**, avec une explication
de l'étape. Ce sont des animations pédagogiques générées, pas des captures d'un
terminal interactif. Le code et les résultats restent lisibles sous chaque GIF,
et une image fixe est disponible pour éviter l'animation. Une animation dure
environ 15 à 22 secondes et se répète.

Les exemples d'une même démonstration partagent leurs variables. Chaque
démonstration est indépendante des autres. Les clés et IV sont aléatoires sauf
lorsqu'un vecteur connu ou une expérience fixe est explicitement utilisé ; les
durées de benchmark changent d'une machine à l'autre.

| Comprendre | Voir |
|---|---|
| Euclide, nombres premiers, factorisation | [01 · Mathématiques](#demo-math) |
| Construire les clés et encoder un message | [02 · RSA](#demo-rsa) |
| Établir un secret partagé | [03 · Diffie–Hellman](#demo-dh) |
| Empreintes et avalanche | [04 · SHA-256](#demo-hash) |
| Blocs et tours de chiffrement | [05 · AES](#demo-aes) |
| Répétitions, flux et intégrité | [06 · Modes](#demo-modes) |
| Authentifier et signer | [07 · HMAC et signature](#demo-authentication) |
| Communiquer et refuser les altérations | [08 · Canal](#demo-channel) |
| Comprendre les mauvaises constructions | [09 · Attaques](#demo-attacks) |
| Mesurer temps et mémoire | [10 · Benchmarks](#demo-benchmarks) |

