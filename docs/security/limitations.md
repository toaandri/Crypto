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
constructions modernes et authentifiées. Les phases 4 et 5 ajoutent HMAC, des
signatures et un protocole, sans transformer cette base en bibliothèque de
production.

- la signature RSA sur un condensat brut ne fournit pas le codage RSA-PSS ;
- le canal utilise un groupe DH fixe de seulement 11 bits, cassable localement ;
- l'authentification suppose une clé prépartagée distribuée par un moyen fiable ;
- les rôles Alice/Bob représentent une seule paire, sans PKI ni certificats ;
- Feistel possède des blocs de 64 bits, inadaptés aux volumes importants ;
- aucune garantie de confidentialité persistante n'est revendiquée ;
- AES/GCM sont implémentés pour l'étude, sans audit ni protection contre les
  accès mémoire ou branches dépendant de secrets ;
- l'API GCM ne conserve pas les nonces déjà utilisés et ne gère pas les quotas
  d'utilisation par clé ; les nonces des vecteurs ne doivent pas être réemployés
  comme modèle pour des messages réels ;
- le canal reste en mémoire, sans transport, persistance des compteurs,
  renégociation, concurrence ni gestion des pertes de paquets.

Les nonces de session, clés directionnelles et compteurs protègent les scénarios
testés de rejeu et de réflexion, mais ne constituent pas une preuve de sécurité.
