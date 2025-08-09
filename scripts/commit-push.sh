#!/bin/bash

# ==============================================================================
# Script de commit et push
# GIT-REQ-003
#
# Ce script aide l'utilisateur à créer un commit et à le pousser vers le dépôt
# distant de manière contrôlée.
# ==============================================================================

# Inclut les variables et fonctions communes
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_GIT} Assistant de commit et push"
echo "------------------------------------"

# 1. Vérifier si le dossier est un dépôt Git
if [ ! -d ".git" ]; then
    echo "${ICON_ERROR} Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser."
    exit 1
fi

# 2. Vérifier la configuration Git (nom/email)
check_git_config

# 3. Vérifier s'il y a des changements à commiter
if git diff-index --quiet HEAD --; then
    echo "${ICON_SUCCESS} Aucun changement à commiter. Le dépôt est à jour."
    exit 0
fi

COMMIT_MESSAGE="$1"

# 4. Mode interactif si aucun message de commit n'est passé en argument
if [ -z "$COMMIT_MESSAGE" ]; then
    echo "${ICON_INFO} Statut actuel du dépôt :"
    git status
    
    read -p "Voulez-vous indexer tous les changements et créer un commit ? (oui/non): " CONFIRM_ADD
    if [ "$CONFIRM_ADD" != "oui" ]; then
        echo "${ICON_INFO} Opération annulée."
        exit 0
    fi
    
    git add .
    echo "${ICON_SUCCESS} Tous les changements ont été indexés."
    
    echo "${ICON_INFO} Rédaction du message de commit."
    echo "Astuce : utilisez un préfixe comme 'feat:', 'fix:', 'docs:', 'refactor:'..."
    read -p "Entrez le message de commit : " COMMIT_MESSAGE
    if [ -z "$COMMIT_MESSAGE" ]; then
        echo "${ICON_ERROR} Le message de commit ne peut pas être vide."
        # Annuler l'indexation pour laisser le dépôt dans l'état initial
        git reset > /dev/null
        exit 1
    fi
else
    # Mode non-interactif
    echo "${ICON_INFO} Indexation de tous les changements..."
    git add .
fi

# 5. Créer le commit
echo "${ICON_INFO} Création du commit..."
git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
    echo "${ICON_ERROR} La création du commit a échoué."
    git reset > /dev/null
    exit 1
fi
echo "${ICON_SUCCESS} Commit créé avec le message : \"$COMMIT_MESSAGE\""

# 6. Pousser les changements
# Si on est en mode interactif, on demande confirmation
CONFIRM_PUSH="non"
if [ -z "$1" ]; then # Si $1 est vide, on était en interactif
    read -p "Voulez-vous pousser les changements maintenant ? (oui/non): " CONFIRM_PUSH
else
    # En mode non-interactif, on pousse directement
    CONFIRM_PUSH="oui"
fi

if [ "$CONFIRM_PUSH" = "oui" ]; then
    echo "${ICON_INFO} Poussée vers le dépôt distant..."
    check_ssh_auth # Vérifie l'authentification SSH avant de pousser
    git push
    if [ $? -ne 0 ]; then
        echo "${ICON_ERROR} La poussée a échoué. Votre branche locale n'est peut-être pas synchronisée avec la branche distante."
        echo "${ICON_INFO} Essayez d'utiliser 'sync-remote.sh' pour synchroniser."
        exit 1
    fi
    echo "${ICON_SUCCESS} Les changements ont été poussés avec succès."
fi

echo "${ICON_SUCCESS} Opération terminée."
exit 0
