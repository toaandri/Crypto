# Chiffrement symétrique et modes

Le chiffrement pédagogique est un réseau de Feistel à 16 tours sur des blocs de
64 bits. Chaque tour transforme une moitié et l'entrelace avec l'autre ; la même
structure devient déchiffrable en parcourant les sous-clés à l'envers. Ce choix
illustre les tours, la confusion et la diffusion. Ce n'est pas AES et il n'a
fait l'objet d'aucune cryptanalyse.

## Modes implémentés

- **ECB** chiffre chaque bloc séparément. Deux blocs clairs égaux donnent deux
  blocs chiffrés égaux : les motifs restent visibles.
- **CBC** combine chaque bloc clair avec le chiffré précédent. Son IV doit être
  imprévisible et unique ; PKCS#7 complète le dernier bloc.
- **CTR** chiffre `nonce || compteur` et combine ce flux avec les données. Il ne
  nécessite aucun padding. Un nonce ne doit jamais être réutilisé avec une clé.

ECB, CBC et CTR n'authentifient pas les données. Un adversaire peut les modifier
sans être détecté. En production, utiliser un mode AEAD audité (AES-GCM ou
ChaCha20-Poly1305). AES lui-même emploie SubBytes, ShiftRows, MixColumns et
AddRoundKey sur des blocs de 128 bits ; son implémentation complète est laissée
à une phase avancée, conformément au cahier des charges.

