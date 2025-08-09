#!/bin/bash

# ==============================================================================
# Script d'initialisation de dépôt Git
# GIT-REQ-002
#
# Ce script assiste l'utilisateur pour initialiser un dépôt, le lier à un
# remote, et créer le commit initial.
# ==============================================================================

# Inclut les variables et fonctions communes
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_GIT} Assistant d'initialisation de dépôt Git"
echo "-------------------------------------------------"

# 1. Vérifier si le dépôt est déjà initialisé
if [ -d ".git" ]; then
    echo "${ICON_INFO} Ce dossier est déjà un dépôt Git."
    exit 0
fi

# 2. Initialisation
echo "${ICON_INFO} Initialisation d'un nouveau dépôt Git..."
git init -b main
if [ $? -ne 0 ]; then
    echo "${ICON_ERROR} Échec de l'initialisation du dépôt Git."
    exit 1
fi
echo "${ICON_SUCCESS} Dépôt Git initialisé avec la branche 'main'."

# 3. Vérifier la configuration Git (nom/email)
check_git_config

# 4. Demander l'URL du remote
read -p "Entrez l'URL SSH du dépôt distant (ex: git@github.com:user/repo.git): " REMOTE_URL
if [ -z "$REMOTE_URL" ]; then
    echo "${ICON_ERROR} L'URL du dépôt distant ne peut pas être vide."
    # On pourrait vouloir nettoyer le 'git init' ici, mais pour l'instant on arrête
    exit 1
fi

# 5. Vérifier si le dépôt distant existe
echo "${ICON_INFO} Vérification du dépôt distant..."
# Redirige la sortie standard et erreur vers /dev/null pour une exécution silencieuse
if git ls-remote "$REMOTE_URL" &> /dev/null; then
    echo "${ICON_WARN} Le dépôt distant '$REMOTE_URL' semble déjà exister."
    read -p "Voulez-vous continuer et lier votre projet local à ce dépôt ? (oui/non): " CONFIRM_LINK
    if [ "$CONFIRM_LINK" != "oui" ]; then
        echo "${ICON_INFO} Opération annulée. Vous devriez peut-être utiliser 'git clone' à la place."
        # Nettoyage du git init pour laisser le dossier propre
        rm -rf .git
        echo "${ICON_INFO} Le dépôt local qui venait d'être créé a été supprimé."
        exit 0
    fi
fi

# 6. Ajouter le remote
git remote add origin "$REMOTE_URL"
if [ $? -ne 0 ]; then
    echo "${ICON_ERROR} Échec de l'ajout du remote. Vérifiez l'URL."
    exit 1
fi
echo "${ICON_SUCCESS} Dépôt distant ajouté sous le nom 'origin'."

# 7. Créer un README initial
if [ ! -f "README.md" ]; then
    echo "# $(basename "$PWD")" > README.md
    echo "${ICON_SUCCESS} Fichier README.md créé."
fi

# 8. Indexer les fichiers
git add .

# 9. Créer le commit initial
read -p "Entrez le message pour le commit initial [feat: Initial commit]: " COMMIT_MESSAGE
# Utilise le message par défaut si l'utilisateur n'entre rien
: ${COMMIT_MESSAGE:="feat: Initial commit"}

git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
    echo "${ICON_ERROR} Échec de la création du commit initial."
    exit 1
fi
echo "${ICON_SUCCESS} Commit initial créé."

# 10. Pousser vers le distant
read -p "Voulez-vous pousser la branche 'main' vers 'origin' maintenant ? (oui/non): " PUSH_NOW
if [ "$PUSH_NOW" = "oui" ]; then
    echo "${ICON_INFO} Poussée vers origin/main..."
    git push -u origin main
    if [ $? -ne 0 ]; then
        echo "${ICON_ERROR} La poussée a échoué. Le dépôt distant contient peut-être déjà des commits."
        echo "${ICON_INFO} Essayez 'git pull' pour synchroniser avant de pousser à nouveau."
        exit 1
    fi
    echo "${ICON_SUCCESS} Le projet a été poussé avec succès sur le dépôt distant."
fi

echo "${ICON_SUCCESS} Le projet est maintenant configuré."
exit 0
