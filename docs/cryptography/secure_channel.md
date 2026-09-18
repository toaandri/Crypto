# Phase 5 — V12 : mini protocole

Le protocole simule deux participants en mémoire. Il combine établissement de
secret, authentification, confidentialité et intégrité. Une clé prépartagée
authentifie l'échange : elle doit déjà être connue d'Alice et Bob. Les signatures
de V11 restent un exemple distinct et ne sont pas nécessaires à cette variante.

1. Chacun produit un exposant DH frais, une valeur publique et un nonce de 32 octets.
2. Les deux construisent le même transcript canonique : version, paramètres,
   rôles, valeurs publiques et nonces, toujours dans l'ordre Alice puis Bob.
3. Chaque preuve HMAC couvre ce transcript et le rôle de son émetteur. Une preuve
   incorrecte empêche la création du canal ; une valeur DH altérée est détectée.
4. Le secret DH, le transcript et la clé prépartagée alimentent une dérivation
   HMAC pédagogique. Des étiquettes séparent les clés de chiffrement et de MAC,
   ainsi que les deux directions. Ce schéma n'est pas une API HKDF standard.
5. Chaque message utilise un IV CBC aléatoire et un compteur par direction.
   Le HMAC couvre session, direction, compteur, IV, longueur et texte chiffré.
6. Le destinataire vérifie la structure, le compteur et le HMAC **avant** de
   déchiffrer. Il avance son compteur seulement après acceptation du message.

Le groupe fixe est `p=2039`, `q=1019`, `g=4` ; `p=2q+1` et `g` appartient au
sous-groupe d'ordre premier q. Les valeurs publiques doivent appartenir à ce
sous-groupe et différer des valeurs triviales. Cette taille rend les calculs
observables mais permet de retrouver facilement les exposants.

```python
from crypto.protocols import Handshake

key = b"cle-prepartagee-pour-la-demo"
alice, bob = Handshake("alice", key), Handshake("bob", key)
proof_a, proof_b = alice.proof(bob.hello), bob.proof(alice.hello)
channel_a = alice.finish(bob.hello, proof_b)
channel_b = bob.finish(alice.hello, proof_a)
assert channel_b.receive(channel_a.send(b"Bonjour")) == b"Bonjour"
assert channel_a.receive(channel_b.send(b"Salut")) == b"Salut"
```

`establish_channels(key)` réalise cette séquence pour les exemples.
`python -m examples.secure_channel` montre aussi une altération et un rejeu.
Les tests couvrent les deux directions, une mauvaise clé prépartagée, le
transcript modifié, les champs du paquet, la réflexion, le rejeu entre sessions
et le rejet avant déchiffrement. Un paquet rejeté ne consomme pas le compteur.

Ce modèle impose une livraison dans l'ordre : un paquet arrivé trop tôt peut
être présenté à nouveau après les précédents. Il n'implémente ni réseau ni
retransmission. Le handshake est à usage unique ; il authentifie le transcript,
sans acquittement final attestant que le pair a déjà installé le canal.

Les limites sont celles du DH minuscule, du Feistel inventé et du code Python
non audité. Il ne faut pas extrapoler les tests à une preuve cryptographique.
Pour un système réel, utiliser un protocole établi tel que TLS et des primitives
authentifiées standard au travers de bibliothèques reconnues.
