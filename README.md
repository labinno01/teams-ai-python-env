# Git Workflow Tool (Version 3.0.0)

Bienvenue dans la nouvelle version de Git Workflow Tool ! Cet outil a été entièrement refactorisé pour offrir une expérience en ligne de commande plus robuste, plus simple et sans dépendances externes lourdes.

## Table des matières
- [Philosophie](#philosophie)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis : Gestion des clés SSH](#prérequis--gestion-des-clés-ssh)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Licence](#licence)

## Philosophie

La version 3.0 adopte une approche modulaire et standard :

*   **Zéro dépendance lourde :** L'interface n'utilise plus `typer` mais le module `argparse` natif de Python.
*   **Interactions claires :** Un nouveau module de `logger` gère toutes les sorties et interactions avec l'utilisateur, en supportant les modes interactif et non-interactif.
*   **Séparation des responsabilités :** La gestion des clés SSH est maintenant déléguée à un script `bash` externe, `ssh/sshkeys.sh`, pour plus de clarté et de puissance.

## Fonctionnalités

*   **Menu interactif :** Lancez `python -m git_tools` sans argument pour un menu guidé.
*   **Commandes directes :** Utilisez les commandes `commit`, `release`, `sync`, et `tag` directement depuis votre terminal.
*   **Mode non-interactif :** Toutes les commandes sont scriptables pour une utilisation dans des pipelines CI/CD via le flag `--non-interactive`.

## Prérequis : Gestion des clés SSH

Avant d'utiliser cet outil, votre authentification SSH avec les services Git (GitHub, GitLab, etc.) doit être fonctionnelle.

Nous fournissons un puissant gestionnaire de clés SSH en `bash` pour vous aider. **Veuillez utiliser ce script pour toute configuration de vos clés.**

*   **Script :** `ssh/sshkeys.sh`
*   **Documentation :** `ssh/sshkeys.md`

Consultez sa documentation pour créer, ajouter et gérer vos clés. Une fois que votre connexion SSH est fonctionnelle (`ssh -T git@github.com` réussit), vous pouvez utiliser `git-tools` sans problème.

## Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone git@github.com:labinno01/teams-ai-python-env.git
    cd teams-ai-python-env
    ```

2.  **Créer et activer l'environnement virtuel :**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation

L'outil s'exécute comme un module Python.

**Lancer le menu interactif :**
```bash
python -m git_tools
```

**Exécuter des commandes spécifiques :**
```bash
# Afficher l'aide générale
python -m git_tools --help

# Lancer un commit en mode interactif
python -m git_tools commit

# Lancer un commit en mode non-interactif
python -m git_tools --non-interactive commit --message "Mon commit"

# Créer une nouvelle release "minor"
python -m git_tools release --type minor
```

## Documentation

La documentation détaillée des différents modules (`logger`, `cli`) se trouve dans le dossier `docs/`.

Pour générer et consulter la documentation du projet avec MkDocs :

1.  **Installer MkDocs :**
    ```bash
    pip install mkdocs
    ```
2.  **Générer la documentation :**
    ```bash
    mkdocs build
    ```
3.  **Lancer le serveur de documentation :**
    ```bash
    mkdocs serve
    ```
    Accédez à `http://127.0.0.1:8000` dans votre navigateur.

## Contribution

Les contributions sont les bienvenues ! Veuillez consulter le fichier `CONTRIBUTING.md` (à créer) pour plus de détails.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` (à créer) pour plus de détails.