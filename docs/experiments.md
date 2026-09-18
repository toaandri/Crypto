# Expériences A–F : protocole, observations et limites

Rapport généré depuis [science.json](results/science.json), sous Python
3.14.2 sur `Windows-11-10.0.26200-SP0`, avec 3 répétitions.
Les données et figures sont conservées ; les durées changeront à la réexécution.
Les clés jouets et les exposants fixes ne sont destinés qu'à l'étude.

Pour reproduire : `python -m experiments.science.run`, puis
`python -m scripts.build_docs`. Les calculs utilisent le code du dépôt.

![Mesures A, B, C et F](assets/science.png)

## A — Influence de la taille des clés RSA

**Hypothèse.** La génération devient plus coûteuse quand la taille augmente.

**Protocole et données.** Générer des clés de 512, 1024 et 2048 bits, une chauffe
puis plusieurs mesures. La recherche de nombres premiers reste aléatoire.
Le benchmark inclut aussi chiffrement/déchiffrement pour 16, 256 et 1024 octets.
Le pic d'allocations Python est obtenu dans une exécution séparée.

**Résultats.** Médianes de génération :

| Bits demandés | Médiane (s) | Pic Python (octets) |
|---|---|---|
| 512 | 0.027823 | 1276 |
| 1024 | 0.122878 | 1836 |
| 2048 | 1.540980 | 2792 |

**Interprétation et conclusion.** Cette exécution montre un coût croissant.
Les petits échantillons et le nombre variable de candidats premiers interdisent
d'en déduire une loi exacte ou une recommandation de sécurité.

## B — Factorisation selon la taille de l'entier

**Hypothèse.** La division d'essai devient rapidement plus lente.

**Protocole et données.** Choisir deux premiers proches par une recherche
déterministe, multiplier, puis factoriser avec la même fonction à chaque taille.
Les paramètres exacts figurent dans le JSON ; aucune cible externe n'est utilisée.

**Résultats.**

| Bits réels | n | Facteurs | Médiane (ms) |
|---|---|---|---|
| 12 | 3551 | 53 × 67 | 0.0028 |
| 15 | 24287 | 149 × 163 | 0.0089 |
| 19 | 301337 | 541 × 557 | 0.0325 |
| 23 | 4305589 | 2069 × 2081 | 0.0790 |
| 27 | 67486189 | 8209 × 8221 | 0.5675 |
| 31 | 1075511989 | 32789 × 32801 | 3.0865 |

**Interprétation et conclusion.** Les facteurs étant proches de la racine,
le nombre de divisions augmente fortement. Il s'agit uniquement de la division
d'essai, pas du crible général des corps de nombres ni d'une estimation du coût
des meilleures attaques RSA modernes.

## C — Effet avalanche de SHA-256

**Hypothèse.** Changer un bit d'entrée modifie environ la moitié du condensat.

**Protocole et données.** Messages : `Bonjour`, les octets 0 à 31 et
`Un seul bit change tout.`. Inverser chaque bit séparément et calculer la distance
de Hamming entre les condensats. Aucun tirage aléatoire n'est nécessaire.

**Résultats.** L'écart-type indiqué est celui de la population d'essais mesurée.

| Message | Essais | Moyenne / 256 | Écart-type | Min–max |
|---|---|---|---|---|
| 1 | 56 | 127.196 | 8.288 | 108–147 |
| 2 | 256 | 127.566 | 8.002 | 104–151 |
| 3 | 192 | 128.495 | 8.018 | 106–151 |

**Interprétation et conclusion.** Les moyennes proches de 128 illustrent une
bonne diffusion. Cette observation ne prouve ni la résistance aux collisions
ni la résistance à la préimage. Les messages ont des nombres d'essais différents,
donc les hauteurs brutes des histogrammes ne sont pas directement comparables.

## D — Motifs répétés en ECB et CBC

**Hypothèse.** ECB conserve l'égalité des blocs ; CBC masque ce motif.

**Protocole et données.** Construire une matrice 16 × 16 de blocs de 8 octets,
alternant les valeurs `AAAAAAAA` et `BBBBBBBB`. Chiffrer avec Feistel et une clé
fixe. L'IV CBC nul est réservé à cette expérience reproductible. Exclure le
padding des comptages et attribuer une couleur à chaque valeur distincte.

![Matrice avant et après chiffrement](assets/ecb-cbc.png)

**Résultats.** 2 blocs distincts en clair, 2 en ECB, 256 en CBC pour ces entrées.

**Interprétation et conclusion.** La matrice révèle les motifs laissés par ECB.
L'absence de répétitions en CBC n'authentifie rien et ne valide pas le Feistel.
Un IV fixe ne doit pas être reproduit pour des messages réels.

## E — Interception d'un Diffie–Hellman non authentifié

**Hypothèse.** Un échange DH seul n'assure pas l'identité du pair.

**Protocole et données.** Dans le groupe jouet p=23, g=5, Alice et Bob utilisent
les exposants 6 et 15. Mallory remplace leurs valeurs publiques par celles de
ses exposants 3 et 7. Comparer les secrets de chaque extrémité.

**Résultats.** Alice partage 6 avec Mallory, Bob partage 15 avec Mallory.
Les deux utilisateurs n'ont pas le même secret, mais Mallory connaît les deux.

**Interprétation et conclusion.** Le calcul mathématique est correct et
l'identité est absente. Le canal V12 ajoute des preuves HMAC du transcript et
rejette une substitution sans connaissance de la clé prépartagée ; ses tests
vérifient le transcript modifié et une mauvaise clé d'authentification.

## F — Paramètres, coût et garanties

**Hypothèse.** Augmenter tailles et nombre de témoins a un coût observable ;
choisir un algorithme adapté change également les performances.

**Protocole et données.** Comparer les deux tests sur les mêmes premiers de
12 à 32 bits. Mesurer ensuite Miller–Rabin sur le premier `2**127-1` avec
1, 4, 8, 16 et 40 témoins. Mesurer aussi des échanges DH de 16 à 128 bits et
AES-GCM avec trois tailles de clé et trois tailles de message.

**Résultats de primalité.**

| Bits | Algorithme | Médiane (ms) |
|---|---|---|
| 12 | trial_division | 0.0029 |
| 12 | miller_rabin | 0.0194 |
| 16 | trial_division | 0.0102 |
| 16 | miller_rabin | 0.0239 |
| 20 | trial_division | 0.0504 |
| 20 | miller_rabin | 0.0338 |
| 24 | trial_division | 0.2019 |
| 24 | miller_rabin | 0.0236 |
| 28 | trial_division | 0.5293 |
| 28 | miller_rabin | 0.0513 |
| 32 | trial_division | 2.8386 |
| 32 | miller_rabin | 0.0552 |

**Nombre de témoins sur 127 bits.**

| Témoins | Borne théorique pour un composé fixé | Médiane (ms) |
|---|---|---|
| 1 | 2.500e-01 | 0.0890 |
| 4 | 3.906e-03 | 0.4145 |
| 8 | 1.526e-05 | 0.7372 |
| 16 | 2.328e-10 | 1.8853 |
| 40 | 8.272e-25 | 4.8614 |

**Échanges DH.** Les durées incluent la validation des paramètres et les deux participants.

| Bits | Médiane (ms) |
|---|---|
| 16 | 0.1141 |
| 32 | 0.4365 |
| 64 | 1.2296 |
| 128 | 12.3623 |

**AES-GCM.** Les nonces sont fixes uniquement pour ces données de benchmark publiques.

| Clé (bits) | Message (octets) | Opération | Médiane (ms) | Pic Python (octets) |
|---|---|---|---|---|
| 128 | 16 | aes_gcm_encrypt | 2.1022 | 4061 |
| 128 | 16 | aes_gcm_decrypt | 2.1122 | 3976 |
| 128 | 256 | aes_gcm_encrypt | 13.1292 | 3957 |
| 128 | 256 | aes_gcm_decrypt | 13.0091 | 3864 |
| 128 | 1024 | aes_gcm_encrypt | 48.2334 | 5807 |
| 128 | 1024 | aes_gcm_decrypt | 49.2436 | 4791 |
| 192 | 16 | aes_gcm_encrypt | 2.6607 | 4501 |
| 192 | 16 | aes_gcm_decrypt | 2.5517 | 4456 |
| 192 | 256 | aes_gcm_encrypt | 36.1062 | 4501 |
| 192 | 256 | aes_gcm_decrypt | 15.4816 | 4456 |
| 192 | 1024 | aes_gcm_encrypt | 59.1057 | 6119 |
| 192 | 1024 | aes_gcm_decrypt | 57.2965 | 5059 |
| 256 | 16 | aes_gcm_encrypt | 2.9896 | 5221 |
| 256 | 16 | aes_gcm_decrypt | 3.1600 | 5176 |
| 256 | 256 | aes_gcm_encrypt | 18.6159 | 5221 |
| 256 | 256 | aes_gcm_decrypt | 18.8489 | 5176 |
| 256 | 1024 | aes_gcm_encrypt | 67.0214 | 6543 |
| 256 | 1024 | aes_gcm_decrypt | 68.0639 | 5527 |

**Interprétation.** Sur les très petits nombres, le coût fixe de Miller–Rabin
peut dépasser la division ; il devient avantageux quand la taille augmente.
La borne théorique n'est pas mesurée sur un premier : un premier passe toujours.
Sous 2**64, le paramètre rounds ne remplace pas les sept bases fixes. Les temps
DH avec validation ne mesurent pas seulement une exponentiation modulaire.

**Conclusion.** Les paramètres doivent être étudiés avec leurs hypothèses, pas
seulement leur vitesse. Les expériences ne recommandent aucun paramètre réel et
ne prouvent aucune résistance cryptographique. AES-GCM apporte une authentification
que les modes Feistel seuls ne donnent pas, mais le code Python reste éducatif.

## Reproductibilité et portée

Les valeurs d'entrée, nombres de répétitions et distributions sont conservés
dans le JSON. Les temps dépendent du système, de Python et de la recherche de
premiers. Trois répétitions donnent une illustration, pas un intervalle de
confiance robuste. Les graphiques sont produits à partir des mesures enregistrées,
sans inventer de données ni interpoler des performances non observées.
