<!-- Documentation for Git Scripts Version 1.x.x (Bash) -->
<!-- For Python CLI Version 2.0.0+, refer to the main documentation. -->

# Documentation des Scripts Utilitaires Git

Ce document décrit le fonctionnement et l'utilisation des scripts `manage_git.sh` et `restore_generic.sh`. Ces outils ont pour but de standardiser et de simplifier la gestion des dépôts Git au sein de nos projets.

---

## 1. `manage_git.sh` - Le Couteau Suisse Git

Ce script est un outil en ligne de commande pour effectuer les opérations Git les plus courantes de manière contrôlée et reproductible.

### Fonctionnalités

-   Vérification de l'existence d'un dépôt Git.
-   Initialisation d'un nouveau dépôt.
-   Ajout de dépôts distants (remotes).
-   Création d'un commit initial.
-   Envoi des modifications (push) vers une remote.
-   Gestion des environnements où les emojis ne sont pas supportés.

### Utilisation

Le script s'utilise avec une commande suivie de ses propres arguments.

```bash
./manage_git.sh [--no-emoji] <commande> [arguments...]
```

#### Option Globale

-   `--no-emoji` : (Optionnel) Force la désactivation des emojis dans les messages de sortie. Le script tente de détecter automatiquement les terminaux non-UTF-8, mais cette option permet de forcer ce comportement.

#### Commandes

-   **`check`**
    -   **Description :** Vérifie si le dossier courant est un dépôt Git.
    -   **Usage :** `./manage_git.sh check`
    -   **Retourne :** Un message de succès ou d'erreur et un code de sortie (`0` si OK, `1` si non).

-   **`init`**
    -   **Description :** Initialise un nouveau dépôt Git (`git init`) si aucun n'existe.
    -   **Usage :** `./manage_git.sh init`

-   **`add-remote <nom> <url>`**
    -   **Description :** Ajoute un nouveau dépôt distant.
    -   **Usage :** `./manage_git.sh add-remote origin git@github.com:user/repo.git`
    -   **Arguments :**
        -   `<nom>` : Le nom de la remote (ex: `origin`, `local_backup`).
        -   `<url>` : L'URL SSH ou HTTPS du dépôt distant.

-   **`initial-commit <message>`**
    -   **Description :** Ajoute tous les fichiers du projet (`git add .`) et crée le premier commit. Si l'identité Git (nom/email) n'est pas configurée, le script la demandera.
    -   **Usage :** `./manage_git.sh initial-commit "Premier commit du projet"`
    -   **Argument :**
        -   `<message>` : Le message du commit, entre guillemets.

-   **`push <nom_remote> <nom_branche>`**
    -   **Description :** Pousse une branche vers une remote spécifiée.
    -   **Usage :** `./manage_git.sh push origin main`
    -   **Arguments :**
        -   `<nom_remote>` : Le nom de la remote de destination.
        -   `<nom_branche>` : Le nom de la branche à pousser.

---

## 2. `restore_generic.sh` - Restauration de Projet

Ce script facilite le clonage d'un projet depuis GitHub en s'assurant que l'authentification par clé SSH est correctement configurée sur la machine de l'utilisateur.

### Fonctionnalités

-   Vérifie la présence d'une clé SSH existante (`~/.ssh/id_rsa`).
-   Si aucune clé n'est trouvée, il guide l'utilisateur pour en créer une.
-   Affiche la clé publique et des instructions claires pour l'ajouter à GitHub.
-   Clone le dépôt spécifié une fois que l'utilisateur a confirmé la configuration.

### Utilisation

Le script prend deux arguments obligatoires.

```bash
./restore_generic.sh <utilisateur_github/nom_repo> <dossier_destination>
```

#### Arguments

-   **`<utilisateur_github/nom_repo>`**
    -   **Description :** L'identifiant complet du dépôt sur GitHub.
    -   **Exemple :** `labinno01/teams-ai-python-env`

-   **`<dossier_destination>`**
    -   **Description :** Le nom du dossier qui sera créé localement pour contenir le projet cloné.
    -   **Exemple :** `mon-projet-restaure`

### Processus pour l'utilisateur

1.  Lancer le script avec les bons arguments.
2.  Si aucune clé SSH n'est présente, suivre les instructions pour en créer une.
3.  Copier la clé publique affichée par le script.
4.  Aller sur [github.com/settings/keys](https://github.com/settings/keys) et ajouter la clé.
5.  Revenir au terminal et appuyer sur "Entrée" pour que le script procède au clonage.
