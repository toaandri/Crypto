# Limites de sécurité

Ce dépôt privilégie la lisibilité et les expériences reproductibles.

- les opérations sur grands entiers ne sont pas à temps constant ;
- RSA ne possède aucun padding OAEP et ses blocs sont déterministes ;
- les clés RSA de démonstration sont trop petites ;
- Diffie–Hellman n'authentifie pas les pairs et ne remplace pas une KDF ;
- le réseau de Feistel est une invention pédagogique non auditée ;
- ECB/CBC/CTR seuls ne garantissent pas l'intégrité ;
- les secrets restent dans la mémoire gérée de Python sans effacement garanti.

Pour de vraies données, employer une bibliothèque reconnue qui expose des
constructions modernes et authentifiées. Les phases suivantes du projet
expliqueront HMAC et les signatures, mais ne transformeront pas cette base en
bibliothèque de production.

