# Installation du Patrimoine de Scripts Git

Ce document explique comment installer l'ensemble des scripts utilitaires Git dans un nouveau projet à l'aide du script d'installation `install.sh`.

L'objectif est de vous permettre de déployer rapidement votre environnement de travail Git standardisé sur n'importe quel nouveau projet.

---

## 1. Commande d'Installation Rapide

Pour installer les scripts, placez-vous à la racine de votre nouveau projet et exécutez la commande suivante dans votre terminal :

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/labinno01/teams-ai-python-env/main/install.sh)"
```

Cette commande télécharge et exécute le script d'installation de manière sécurisée.

---

## 2. Que Fait le Script d'Installation ?

Le script est conçu pour être transparent et didactique. Voici les étapes qu'il réalise :

1.  **Vérification de `curl` :** Il s'assure que l'outil `curl` est disponible sur votre système.
2.  **Création du Dossier :** Il crée un dossier `.git-scripts/` à la racine de votre projet pour y stocker tous les scripts utilitaires.
3.  **Téléchargement des Scripts :** Il télécharge la dernière version de chaque script (`setup-ssh.sh`, `init-repository.sh`, etc.) depuis le dépôt GitHub de référence.
4.  **Téléchargement de `version.json` :** Il récupère le fichier `version.json` pour que les scripts connaissent leur version actuelle.
5.  **Permissions :** Il rend automatiquement les scripts téléchargés exécutables (`chmod +x`).
6.  **Mise à jour du `.gitignore` :** Il vous propose d'ajouter le dossier `.git-scripts/` à votre fichier `.gitignore` pour éviter de commiter les outils eux-mêmes dans votre nouveau projet.
7.  **Message de Fin :** Il affiche un message de succès avec des instructions pour commencer à utiliser les scripts.

---

## 3. Personnalisation (Utilisation avec un Dépôt Privé)

Si vous avez "forké" le projet `teams-ai-python-env` ou si vous souhaitez maintenir votre propre version des scripts dans un **dépôt privé**, vous pouvez facilement adapter le script.

1.  **Téléchargez le script `install.sh`** localement au lieu de l'exécuter directement via `curl`.
2.  **Modifiez la variable `REPO_URL`** au début du script pour pointer vers votre dépôt.

    ```bash
    # Remplacez l'URL par l'URL de votre dépôt
    REPO_URL="https://raw.githubusercontent.com/VOTRE_NOM/VOTRE_DEPOT/main"
    ```

3.  Si votre dépôt est privé, assurez-vous d'avoir configuré votre [accès SSH](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh) et utilisez l'URL SSH de votre dépôt pour que l'authentification se fasse de manière transparente.
