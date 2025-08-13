# Règles de Développement pour l'Agent Codeur

Ce guide détaille les bonnes pratiques de développement à suivre pour l'agent codeur, afin de limiter les problèmes liés aux opérations de remplacement de code et d'assurer la qualité et la maintenabilité du code produit. Ces règles feront partie du kit de bienvenue pour tout nouvel agent développeur.

## 1. Lecture Préalable

*   **Toujours lire le fichier** avant de tenter un remplacement pour assurer une correspondance exacte du contenu, y compris les espaces, indentations, et caractères spéciaux.

## 2. Stratégie de Remplacement

*   **Éviter les Chaînes Multi-lignes pour les Remplacements Directs :** Préférer les remplacements simples (une seule ligne, sans caractères spéciaux conflictuels pour l'outil `replace`).
*   **Utilisation de la Solution de Secours pour les Changements Complexes :** Pour les changements impliquant :
    *   Des modifications multi-lignes.
    *   Des indentations complexes.
    *   Des caractères spéciaux (`\`, `'`, `"`) qui peuvent poser problème à l'outil `replace`.
    *   Une incertitude sur le contenu exact du fichier cible.
    Utiliser la méthode de secours : **lire le fichier en entier, effectuer les modifications en mémoire (avec les fonctions de manipulation de chaînes de Python ou des expressions régulières), puis écrire le fichier modifié en entier.**

## 3. Précision des Caractères

*   **Copier-coller directement** depuis le contenu du fichier pour construire les chaînes de remplacement (`old_string`, `new_string`). Cela permet de préserver les espaces, indentations et caractères spéciaux exacts.

## 4. Gestion des Fichiers Volumineux

*   **Évaluer la taille du fichier** avant de choisir la méthode de manipulation. Pour les fichiers très volumineux, envisager des méthodes alternatives ou des outils spécialisés (à discuter avec l'utilisateur si nécessaire).

## 5. Encodage Explicite

*   **Spécifier explicitement l'encodage** (par exemple, `UTF-8`) lors de la lecture et de l'écriture de fichiers pour éviter les problèmes de caractères.

## 6. Documentation et Journalisation

*   **Garder une trace des modifications effectuées.** Utiliser le système de gestion de versions (Git) pour des commits fréquents et des messages descriptifs.
*   **Sauvegarder les versions précédentes des fichiers** avant de faire des modifications importantes (par exemple, via des fichiers `.bak` ou des branches Git temporaires).

## 7. Tests et Validation

*   **Toujours tester le code** après des modifications pour s'assurer de son bon fonctionnement.
*   **Utiliser des outils de validation** (linters, formatteurs, frameworks de test) pour vérifier que le code modifié est correct et conforme aux standards du projet.

## 8. Utilisation d'Outils Spécialisés

*   Pour des tâches spécifiques (par exemple, manipulation de JSON ou XML), utiliser des bibliothèques et outils dédiés plutôt que de dépendre uniquement de l'outil de remplacement générique.

## 9. Automatisation des Tâches Répétitives

*   **Écrire des scripts** pour automatiser les modifications répétitives et les tâches complexes, afin de gagner en efficacité et de réduire les erreurs.

## 10. Règles Spécifiques par Langage

Ces règles complètent les principes généraux et s'appliquent aux particularités de chaque langage :

### Python

*   **Indentation :** Toujours conserver l'indentation exacte lors des modifications. Utiliser des outils qui préservent l'indentation (comme les formatteurs de code).
*   **Gestion des Fichiers :** Spécifier explicitement l'encodage `UTF-8` lors de la lecture et de l'écriture de fichiers. Utiliser `pathlib` pour une gestion robuste des chemins.
*   **Environnements Virtuels :** Tester les modifications dans un environnement virtuel pour s'assurer qu'elles ne cassent pas les dépendances et pour isoler le projet.
*   **Outils Recommandés pour Python :**
    *   **Formatage :** Black, Autopep8
    *   **Linting :** Pylint, Flake8, Ruff
    *   **Gestion des Dépendances :** Pipenv, Poetry
    *   **Tests :** Pytest, Unittest
    *   **Environnements Virtuels :** Virtualenv, Conda
    *   **Documentation :** Sphinx, MkDocs
    *   **Gestion de Version :** Git, GitPython
    *   **Construction et Déploiement :** Setuptools, Twine
    *   **Profiling et Performance :** cProfile, Py-Spy
    *   **Gestion des Erreurs et Logging :** Logging, Sentry
    *   **Gestion des Données :** Pandas, SQLAlchemy
    *   **Sécurité :** Bandit, Safety

### Bash

*   **Gestion des Espaces et des Guillemets :** Toujours échapper les espaces dans les chemins de fichiers et les arguments de commande. Utiliser des guillemets pour entourer les variables et les chemins.
*   **Caractères Spéciaux :** Échapper les caractères spéciaux avec des backslashes ou utiliser des guillemets simples ou doubles.
*   **Fin de Ligne :** Utiliser des outils qui préservent les fins de ligne (LF vs CRLF) selon l'environnement cible. Préférer LF (Unix) pour les scripts Bash.

### C/C++

*   **Sensibilité aux Espaces et aux Sauts de Ligne :** Être très attentif aux espaces et aux sauts de ligne, surtout dans les directives de préprocesseur.
*   **Gestion des Fichiers d'En-tête :** Modifier les fichiers d'en-tête avec prudence, car les changements peuvent affecter de nombreux fichiers sources.
*   **Compilation et Liens :** Toujours recompiler et relier le projet après des modifications pour s'assurer qu'il n'y a pas d'erreurs de compilation ou de liens.

### JavaScript

*   **Sensibilité aux Points-virgules :** Inclure explicitement les points-virgules pour éviter les ambiguïtés.
*   **Gestion des Modules et des Dépendances :** Tester les modifications dans un environnement qui reproduit les dépendances du projet.
*   **Environnements d'Exécution :** Tester les modifications dans l'environnement cible (navigateur, Node.js, etc.).

## 11. Règles Générales Complémentaires

*   **Utiliser des Outils de Formatage :** Appliquer des outils comme Black (Python), clang-format (C/C++), ou Prettier (JavaScript) pour maintenir un code bien formaté.
*   **Tests Automatiques :** Mettre en place des tests automatiques (avec Pytest, Google Test, Jest, etc.) après chaque modification.
*   **Gestion des Versions :** Utiliser Git pour suivre les changements, faire des commits fréquents avec des messages descriptifs.

## Prochaines Étapes : Outils à Fournir

Pour faciliter l'adhérence à ces règles, les outils suivants devraient être fournis à l'agent codeur :

*   **Outils de Lecture et Écriture de Fichiers :** Avec options pour gérer les encodages, les fins de ligne, etc.
*   **Bibliothèques de Manipulation de Chaînes :** Pour les expressions régulières, les opérations de chaînes complexes.
*   **Outils de Test et Validation :** Linters, formatteurs, frameworks de test.
*   **Outils de Journalisation et Suivi :** Pour suivre les changements et les sauvegardes.
*   **Outils d'Automatisation :** Pour les tâches répétitives et les modifications complexes.
*   **Outils Spécifiques au Développement Python :**
    *   **Formatage :** Black, Autopep8
    *   **Linting :** Pylint, Flake8, Ruff
    *   **Gestion des Dépendances :** Pipenv, Poetry
    *   **Tests :** Pytest, Unittest
    *   **Environnements Virtuels :** Virtualenv, Conda
    *   **Documentation :** Sphinx, MkDocs
    *   **Gestion de Version :** Git, GitPython
    *   **Construction et Déploiement :** Setuptools, Twine
    *   **Profiling et Performance :** cProfile, Py-Spy
    *   **Gestion des Erreurs et Logging :** Logging, Sentry
    *   **Gestion des Données :** Pandas, SQLAlchemy
    *   **Sécurité :** Bandit, Safety