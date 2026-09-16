# RSA brut et messages par blocs

## Principe

Deux premiers distincts `p` et `q` donnent `n = pq` et
`φ(n) = (p-1)(q-1)`. On choisit `e` premier avec `φ(n)`, puis
`d = e⁻¹ mod φ(n)`. La clé publique est `(n,e)` et la clé privée `(n,d)`.

- chiffrement : `c = mᵉ mod n` ;
- déchiffrement : `m = cᵈ mod n`.

Le module `encoding` convertit des octets en entiers plus petits que `n`, garde
la longueur d'origine et restaure donc aussi les zéros initiaux. Les clés sont
sérialisables en JSON pour l'expérimentation.

## Limites essentielles

RSA brut est déterministe : un même message produit toujours le même chiffré.
Il est malléable et vulnérable aux attaques par messages choisis. Le découpage
en blocs de ce projet résout seulement la représentation, **pas la sécurité**.
Un système réel emploie RSA-OAEP pour chiffrer une petite clé aléatoire, puis un
chiffrement authentifié tel qu'AES-GCM ou ChaCha20-Poly1305 pour les données.
Les tailles de 128 ou 256 bits dans les exemples accélèrent uniquement les
tests ; elles sont trivialement factorisables.

