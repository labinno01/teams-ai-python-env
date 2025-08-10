# Git Workflow CLI (Version 2.0.0 - Python)

Bienvenue dans la CLI Git Workflow ! Cet outil est conçu pour simplifier et automatiser les opérations Git courantes via une interface conviviale basée sur des menus.

## Table des matières
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Licence](#licence)

## Fonctionnalités

La CLI Git Workflow (v2.0.0) offre les fonctionnalités suivantes :

*   **Menu interactif :** Naviguez facilement entre les différents workflows Git.
*   **Configuration SSH guidée :** Un assistant pas à pas pour configurer et dépanner l'authentification SSH avec GitHub.
*   **Commit & Push :** Simplifiez le processus d'indexation, de commit et de push de vos modifications.
*   **Création de Release :** Automatisez la gestion des versions, y compris la mise à jour de `version.json`, la création de commits de version et de tags Git.
*   **Synchronisation avec le distant :** Récupérez les dernières modifications et synchronisez votre branche locale avec le dépôt distant.

## Installation

Pour utiliser la CLI Git Workflow, suivez ces étapes :

1.  **Cloner le dépôt :**
    ```bash
    git clone git@github.com:labinno01/teams-ai-python-env.git
    cd teams-ai-python-env
    ```
    *(Assurez-vous d'avoir configuré votre clé SSH pour GitHub. Si ce n'est pas le cas, utilisez `https://github.com/labinno01/teams-ai-python-env.git` pour le clonage initial, puis exécutez la commande `setup-ssh` du menu pour configurer SSH.)*

2.  **Créer et activer l'environnement virtuel :**
    Il est fortement recommandé d'utiliser un environnement virtuel pour gérer les dépendances.
    ```bash
    python3 -m venv .venv-teams-ai-python-env
    source .venv-teams-ai-python-env/bin/activate
    ```
    *(Si vous préférez un autre emplacement pour votre environnement virtuel, ajustez le chemin en conséquence.)*

3.  **Installer les dépendances :**
    ```bash
    pip install typer
    # D'autres dépendances seront ajoutées au fur et à mesure du développement
    ```

## Utilisation

Une fois installé, vous pouvez lancer la CLI via le menu interactif :

```bash
python -m python_scripts.main menu
```

Le menu vous guidera à travers les options disponibles.

Vous pouvez également exécuter des commandes spécifiques directement :

```bash
python -m python_scripts.main --help
python -m python_scripts.main commit-push --help
python -m python_scripts.main setup-ssh
```

## Documentation

La documentation complète de la CLI Git Workflow est disponible dans le dossier `docs/`.

Pour générer et consulter la documentation localement :

1.  **Installer MkDocs :**
    ```bash
    pip install mkdocs
    ```
2.  **Générer la documentation :**
    ```bash
    mkdocs build
    ```
    Les fichiers HTML générés se trouveront dans le dossier `site/`.

3.  **Lancer le serveur de documentation (pour le développement) :**
    ```bash
    mkdocs serve
    ```
    Accédez à `http://127.0.0.1:8000` dans votre navigateur.

## Contribution

Les contributions sont les bienvenues ! Veuillez consulter le fichier `CONTRIBUTING.md` (à créer) pour plus de détails sur la façon de contribuer.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` (à créer) pour plus de détails.
