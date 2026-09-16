# Hachage et effet avalanche

Une fonction de hachage produit une empreinte de taille fixe. Une fonction
cryptographique vise la résistance à la préimage, à la seconde préimage et aux
collisions. `educational_hash` ne fait que 32 bits : il permet de chercher des
collisions, mais ne fournit aucune de ces garanties à une échelle moderne.

L'implémentation SHA‑256 suit les étapes de FIPS 180-4 : ajout du bit `1`,
padding jusqu'à 448 modulo 512, longueur sur 64 bits, expansion de 16 à 64 mots,
puis 64 tours de compression. Les tests la comparent à `hashlib` sur des
frontières de blocs et au vecteur connu de `abc`.

L'expérience `experiments.avalanche.run` change chacun des bits du message,
recalcule SHA‑256 et compte la distance de Hamming entre empreintes. Une bonne
diffusion fait changer en moyenne près de la moitié des 256 bits. Une empreinte
seule n'authentifie pas un message : cette propriété nécessite notamment HMAC,
prévu en phase 4.

