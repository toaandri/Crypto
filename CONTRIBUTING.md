# Contribuer

Le projet est un outil d'apprentissage. Préserver la lisibilité, les petits
exemples et la distinction entre démonstration et sécurité réelle.

1. Installer Python 3.10+ et `python -m pip install -e ".[test,docs]"`.
2. Modifier l'algorithme et son explication ; ajouter un test de propriété,
   un cas invalide ou un vecteur indépendant pertinent.
3. Exécuter `python -m pytest`.
4. Si les exemples changent, modifier `examples/tour.py`. Les textes du README
   sont dans `docs/readme_header.md` et `docs/readme_footer.md`.
5. Recréer les ressources avec `python -m scripts.build_docs`, puis lancer
   `python -m scripts.verify_docs`. Ouvrir les images modifiées pour vérifier
   leur lisibilité. Les GIFs sont construits depuis des sorties réellement
   exécutées ; ne pas remplacer ces résultats par des sorties inventées.

Pour renouveler les expériences : `python -m experiments.science.run` avant la
génération documentaire. Garder les JSON afin que les graphiques soient
reproductibles à partir des données. Les temps et les clés aléatoires peuvent
varier : ne pas écrire de test imposant une durée précise.

Le package `crypto` ne doit dépendre que de la bibliothèque standard. Les
bibliothèques de référence appartiennent aux tests et les outils graphiques
aux scripts documentaires. Ne pas ajouter d'attaques réseau ou de cibles réelles
aux simulations locales. Ne pas présenter une suite de tests comme un audit.

La CI vérifie le code et les liens documentaires ; elle ne publie rien et ne
régénère pas les images. Pour une nouvelle version, modifier `pyproject.toml`
et `CHANGELOG.md`. Les fichiers générés `build/`, `dist/`, `.venv/` et caches
sont exclus de Git.
