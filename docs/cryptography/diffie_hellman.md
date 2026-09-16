# Diffie–Hellman

Dans un groupe modulo un premier `p`, Alice choisit `a` et publie `gᵃ mod p` ;
Bob choisit `b` et publie `gᵇ mod p`. Ils calculent respectivement
`(gᵇ)ᵃ` et `(gᵃ)ᵇ`, tous deux égaux à `gᵃᵇ mod p`. Le secret lui-même ne
traverse jamais le réseau. La difficulté supposée du logarithme discret empêche
de retrouver facilement les exposants privés.

Le module valide la primalité et rejette les valeurs publiques triviales. Il ne
prouve toutefois pas que `g` génère un sous-groupe d'ordre approprié et ne
dérive pas une clé binaire depuis le secret.

Surtout, Diffie–Hellman seul n'authentifie personne : un attaquant peut établir
un secret avec Alice et un autre avec Bob. En pratique, paramètres normalisés,
validation complète, signatures/certificats et fonction de dérivation de clé
sont nécessaires ; X25519 est un choix courant via une bibliothèque auditée.

