# Git Workflow Tool - Interface en Ligne de Commande

## Table des matières
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Utilisation de base](#utilisation-de-base)
4. [Options globales](#options-globales)
5. [Commandes disponibles](#commandes-disponibles)
   - [commit](#commit)
   - [release](#release)
   - [sync](#sync)
   - [tag](#tag)
6. [Mode interactif](#mode-interactif)
7. [Exemples d'utilisation](#exemples-dutilisation)
8. [Variables d'environnement](#variables-denvironnement)
9. [Intégration CI/CD](#intégration-cicd)
10. [Développement et extension](#développement-et-extension)

---

## Introduction
`git_tools/cli.py` est le **point d'entrée principal** de Git Workflow Tool. Il offre :
- Une **interface en ligne de commande** complète
- Un **menu interactif** pour les utilisateurs débutants
- Un **mode non-interactif** pour les scripts et CI/CD
- Une **architecture modulaire** facile à étendre

---

## Installation
### Via pip (recommandé)
```bash
pip install git-tools
```
### En développement
```bash
git clone https://github.com/votre-repo/git-tools.git
cd git-tools
pip install -e .
```

## Utilisation de base
```bash
# Lancer le menu interactif
git-tools

# Exécuter une commande spécifique
git-tools commit -m "Mon message de commit"

# Afficher l'aide
git-tools --help

# Afficher la version
git-tools --version
```

## Options globales

| Option | Description |
|---|---|
| `--version` | Affiche la version et quitte |
| `--non-interactive` | Désactive les prompts interactifs (pour les scripts/CI) |
| `--debug` | Active les messages de debug |
| `--force-color` | Force l'affichage des couleurs même si stdout n'est pas un TTY |
| `--help` | Affiche l'aide et quitte |

**Exemple :**
```bash
git-tools --non-interactive --debug commit -m "Fix bug"
```

## Commandes disponibles

### commit
Effectue un commit et push vers le dépôt distant.

**Usage :**
```bash
git-tools commit [OPTIONS]
```

**Options :**

| Option | Description |
|---|---|
| `-m`, `--message` | Message de commit (désactive le prompt) |
| `--amend` | Modifie le dernier commit au lieu d'en créer un nouveau |

**Exemples :**
```bash
# Mode interactif
git-tools commit

# Mode non-interactif avec message
git-tools --non-interactive commit -m "Fix critical bug"
```

### release
Crée une nouvelle release (tag + push).

**Usage :**
```bash
git-tools release [OPTIONS]
```

**Options :**

| Option | Description |
|---|---|
| `--type` | Type de release (major/minor/patch) |
| `--dry-run` | Simule la création sans appliquer les changements |

**Exemples :**
```bash
# Créer une release patch
git-tools release --type patch

# Simulation
git-tools release --type minor --dry-run
```

### sync
Synchronise le dépôt local avec le dépôt distant.

**Usage :**
```bash
git-tools sync
```

**Exemple :**
```bash
git-tools --non-interactive sync
```

### tag
Gère les tags Git (liste, création, suppression).

**Usage :**
```bash
git-tools tag ACTION [OPTIONS]
```

**Actions disponibles :**

| Action | Description |
|---|---|
| `list` | Liste tous les tags |
| `create` | Crée un nouveau tag |
| `delete` | Supprime un tag existant |

**Options :**

| Option | Description |
|---|---|
| `--name` | Nom du tag (pour create/delete) |
| `--message` | Message du tag (pour create) |

**Exemples :**
```bash
# Lister les tags
git-tools tag list

# Créer un tag
git-tools tag create --name v1.0.0 --message "Version 1.0.0"

# Supprimer un tag
git-tools tag delete --name v1.0.0
```

## Mode interactif
Si aucune commande n'est spécifiée, l'outil lance un menu interactif :
```
🐙 Git Workflow Tool - Menu Principal
==================================================
1. Commit & Push
2. Créer une Release
3. Synchroniser avec le dépôt distant
4. Gérer les Tags
5. Quitter
```

**Navigation :**
- Utilisez les numéros pour sélectionner une option
- Suivez les instructions à l'écran

**Exemple :**
```bash
git-tools  # Lance le menu interactif
```

## Exemples d'utilisation

### 1. Workflow de commit complet
```bash
# Mode interactif
git-tools commit

# Mode non-interactif (pour CI)
git-tools --non-interactive commit -m "Update README [skip ci]"
```

### 2. Création d'une release
```bash
# Avec confirmation interactive
git-tools release --type minor

# Sans interaction (pour scripts)
git-tools --non-interactive release --type patch
```

### 3. Synchronisation
```bash
# Mode interactif
git-tools sync

# Mode silencieux
git-tools --non-interactive sync
```

### 4. Gestion des tags
```bash
# Lister les tags
git-tools tag list

# Créer un tag annoté
git-tools tag create --name v2.0.0 --message "Version 2.0.0"

# Supprimer un tag
git-tools --non-interactive tag delete --name v2.0.0
```

## Variables d'environnement

| Variable | Description | Valeurs possibles |
|---|---|---|
| `DEBUG` | Active les messages de debug | `1`, `true`, `yes` |
| `FORCE_COLOR` | Force l'affichage des couleurs | `1`, `true`, `yes` |
| `NO_COLOR` | Désactive complètement les couleurs | Toute valeur |
| `GIT_TOOLS_NON_INTERACTIVE` | Désactive le mode interactif (alternative à `--non-interactive`) | Toute valeur |

**Exemple :**
```bash
DEBUG=1 git-tools commit
```

## Intégration CI/CD
Pour utiliser Git Workflow Tool dans vos pipelines CI/CD :

### GitHub Actions
```yaml
- name: Commit changes
  run: |
    git-tools --non-interactive commit -m "Auto-commit from CI [skip ci]"
    git-tools --non-interactive sync
```

### GitLab CI
```yaml
script:
  - git-tools --non-interactive release --type patch
```

### Jenkins
```groovy
sh 'git-tools --non-interactive --debug sync'
```

## Développement et extension

### Ajouter une nouvelle commande
1.  **Créer une fonction workflow** dans `git_tools/workflows.py` :
    ```python
    def ma_nouvelle_commande(logger: Logger, args: argparse.Namespace) -> None:
        logger.info("Exécution de ma nouvelle commande...")
        # ... logique métier
    ```

2.  **Mettre à jour `COMMAND_MAPPING`** dans `cli.py` :
    ```python
    COMMAND_MAPPING = {
        # ... commandes existantes ...
        "ma-commande": ma_nouvelle_commande,
    }
    ```

3.  **Ajouter le parser de commande** dans `parse_args()` :
    ```python
    ma_commande_parser = subparsers.add_parser(
        "ma-commande",
        help="Description de ma commande",
    )
    ma_commande_parser.add_argument(
        "--option",
        help="Description de l'option",
    )
    ```

### Structure du projet
```
git_tools/
├── __init__.py
├── cli.py          # Point d'entrée (ce fichier)
├── logger.py       # Gestion des logs et interactions
├── workflows.py    # Logique métier des commandes
└── utils/          # Fonctions utilitaires
```

### Bonnes pratiques
- **Toujours utiliser le `logger`** pour les interactions utilisateur.
- **Gérer les erreurs proprement**.
- **Documenter les nouvelles commandes** dans le `__doc__` du module.
- **Respecter le typage** pour une meilleure maintenabilité.

## Résolution des problèmes

- **Problème : Commande non trouvée**
  - **Solutions :** Vérifier `COMMAND_MAPPING`, le parser, et la casse.

- **Problème : L'outil plante en mode non-interactif**
  - **Solutions :** Vérifier le flag `--non-interactive`, s'assurer que les `prompt`/`confirm` ont des valeurs par défaut.

- **Problème : Les couleurs ne s'affichent pas**
  - **Solutions :** Forcer avec `--force-color`, vérifier `NO_COLOR`.

- **Problème : Erreur de permission**
  - **Solutions :** Configurer la clé SSH avec `ssh-add`, utiliser le workflow de setup SSH.

## Changelog
- **v1.0.0 (2023-11-20):** Première version stable.
- **v1.1.0 (2023-11-25):** Ajout du support des variables d'environnement.

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
