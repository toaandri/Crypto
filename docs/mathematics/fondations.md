# Arithmétique modulaire et nombres premiers

## PGCD et Bézout

L'algorithme d'Euclide remplace répétitivement `(a, b)` par `(b, a mod b)`.
Quand `b` vaut zéro, `a` est le PGCD. Sa version étendue conserve deux
coefficients et produit `g = ax + by`. Si `g = 1`, alors `x mod n` est l'inverse
de `a` modulo `n`. Ainsi `3⁻¹ mod 7 = 5`, car `3 × 5 ≡ 1 (mod 7)`.

L'exponentiation rapide lit les bits de l'exposant et utilise les carrés
successifs. Elle demande `O(log exposant)` multiplications au lieu d'une par
unité d'exposant.

## Primalité

`is_prime` utilise la division d'essai : exact, simple, mais trop lent pour de
grands nombres. `is_probable_prime` décompose `n-1 = 2ˢd`, puis applique
Miller–Rabin. Les sept bases fixes rendent le résultat déterministe pour
`n < 2⁶⁴`. Au-delà, 40 témoins aléatoires donnent une borne de faux positif de
`4⁻⁴⁰`.

`generate_prime(bits)` utilise `secrets.randbits`, force le bit de poids fort et
le bit impair, puis teste les candidats. Le résultat possède exactement le
nombre de bits demandé.

## Factorisation et expériences

`factorize(n)` divise successivement par 2, puis les diviseurs impairs jusqu'à
la racine du reste. Chaque facteur est conservé avec sa multiplicité :
`factorize(72) == [2, 2, 2, 3, 3]`, tandis que `factorize(1) == []`.
Cette méthode simple n'est adaptée qu'aux petits entiers ; elle ne représente
pas les meilleurs algorithmes de factorisation connus.

`experiments.science.run` compare division d'essai et Miller–Rabin sur les mêmes
premiers de 12 à 32 bits, puis 1, 4, 8, 16 et 40 témoins sur `2**127-1`. Sous
`2**64`, le paramètre `rounds` ne change pas les sept bases déterministes.
La borne `4**(-rounds)` concerne un composé fixé et des témoins indépendants ;
ce n'est pas la probabilité a posteriori qu'un entier accepté soit composé.
Les tableaux de mesures et graphiques sont décrits dans [les expériences](../experiments.md).

Ces opérations Python ne sont pas à temps constant : elles révèlent
potentiellement des informations par leur durée et ne conviennent pas à la
production.
