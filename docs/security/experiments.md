# V13 et V14 — Expériences locales

## Simulations d'attaques

Commande : `python -m experiments.attacks.run`. Le JSON contient les résultats,
les secrets jouets récupérés et, lorsque pertinent, le nombre d'essais. Aucun
réseau, fichier de mots de passe ou cible externe n'est utilisé.

| Expérience | Hypothèse et protocole | Interprétation attendue |
|---|---|---|
| Force brute | Tester les 256 clés possibles sur un bloc connu | La clé 173 est retrouvée au 174e essai ; l'entropie compte davantage que le format de stockage sur 8 octets |
| Dictionnaire | Comparer SHA-256 de quatre mots à un hash sans sel | `bonjour123` est retrouvé ; un hash rapide n'est pas une fonction de stockage des mots de passe |
| Collision | Tronquer volontairement le hash pédagogique à 8 bits et essayer des messages distincts | Une collision existe en au plus 257 essais ; ce résultat ne concerne pas SHA-256 ni le hash complet de 32 bits |
| MITM | Remplacer chaque valeur publique DH par celle de Mallory | Mallory partage un secret avec chacun ; Alice et Bob n'ont plus le même secret |
| Factorisation RSA | Diviser n=3233 par les entiers jusqu'à sa racine, retrouver φ(n) puis d | Les facteurs 53 et 61 permettent de déchiffrer le message 42 |

Toutes les données de ces simulations sont fixes et les résultats sont
reproductibles. Le test valide notamment l'égalité des secrets avec Mallory et
la collision réelle des deux messages distincts. Ces démonstrations expliquent
le besoin de paramètres assez grands, d'une dérivation de mot de passe avec sel
et coût adapté, et de l'authentification du DH. Elles ne mesurent pas le coût
d'une attaque contre des paramètres modernes.

Résultats observés : la collision tronquée apparaît au 54e essai entre `0003`
et `0035`, avec une empreinte de 189. Les secrets DH obtenus sont 6 côté Alice
et 15 côté Bob, tous deux connus de Mallory. La factorisation trouve 53 après
52 divisions d'essai. Les autres résultats correspondent au tableau ci-dessus.

## Benchmarks

```powershell
python -m experiments.benchmarks.run --key-sizes 512 1024 2048 --message-sizes 16 256 1024 --repeats 3
```

Hypothèse : la génération et les opérations RSA deviennent plus coûteuses quand
la taille des clés augmente ; le hash et CBC croissent avec le volume des données.
Le rapport JSON indique Python, la plateforme, la taille demandée des clés, la
taille réelle du modulus pour les opérations RSA, la taille des messages, les
durées médiane et minimale et le pic d'allocations Python en octets.

Protocole : une exécution de chauffe, puis N mesures avec `perf_counter` ; une
exécution séparée sous `tracemalloc` évite d'inclure son surcoût dans les durées.
On mesure génération RSA, chiffrement et déchiffrement RSA par blocs, SHA-256,
chiffrement et déchiffrement CBC. Les allers-retours sont vérifiés avant mesure.
Le pic mémoire mesure les allocations Python de l'opération, pas la RAM totale
du processus, les entrées préexistantes ni toutes les allocations natives.

Les messages sont déterministes, les clés et IV sont aléatoires. La génération
des premiers et la charge système font donc varier les mesures. Pour comparer,
conserver machine, version Python, tailles et répétitions identiques ; augmenter
les répétitions et interpréter les médianes, sans transformer un microbenchmark
en garantie de performance ou de sécurité. Le rapport enregistré sur la machine
de travail dans [benchmark_sample.json](benchmark_sample.json) illustre une exécution ; il n'est pas un
seuil de performance à imposer aux tests.

Résultats de cette exécution sous Python 3.14.2 / Windows 11, trois répétitions :

| Taille RSA demandée | Génération, médiane |
|---|---:|
| 512 bits | 0,0330 s |
| 1024 bits | 0,1078 s |
| 2048 bits | 0,6616 s |

Les 30 lignes du rapport couvrent les six opérations et les tailles annoncées.
Cette exécution soutient l'hypothèse d'un coût croissant de génération RSA ; trois
répétitions ne suffisent pas à établir une loi de complexité expérimentale.

Conclusion : les petits paramètres rendent les mécanismes visibles et rapides,
mais leur vitesse ne constitue pas une recommandation d'utilisation réelle.
