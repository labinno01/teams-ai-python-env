#!/bin/bash

# ==============================================================================
# Script de synchronisation avec le dépôt distant
# GIT-REQ-004
#
# Ce script aide l'utilisateur à synchroniser son dépôt local avec les
# changements du dépôt distant.
# ==============================================================================

# Inclut les variables et fonctions communes
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_GIT} Assistant de synchronisation avec le distant"
echo "-----------------------------------------------------"

# 1. Vérifier si le dossier est un dépôt Git
if [ ! -d ".git" ]; then
    echo "${ICON_ERROR} Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser."
    exit 1
fi

# 2. Récupérer les informations du remote
REMOTE_NAME=$(git remote)
if [ -z "$REMOTE_NAME" ]; then
    echo "${ICON_WARN} Aucun remote n'est configuré. Impossible de synchroniser."
    exit 0
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# 3. Mettre à jour les informations du remote
echo "${ICON_INFO} Récupération des dernières informations du dépôt distant (${REMOTE_NAME})..."
git fetch ${REMOTE_NAME}
if [ $? -ne 0 ]; then
    echo "${ICON_ERROR} La récupération depuis le distant a échoué. Vérifiez votre connexion et les droits d'accès au dépôt."
    exit 1
fi

# 4. Vérifier le statut par rapport à la branche distante
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse ${REMOTE_NAME}/${CURRENT_BRANCH})

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo "${ICON_SUCCESS} Votre branche locale '${CURRENT_BRANCH}' est déjà à jour avec '${REMOTE_NAME}/${CURRENT_BRANCH}'."
    exit 0
fi

# Vérifier si on est en avance (commits locaux à pousser)
if git log ..${REMOTE_NAME}/${CURRENT_BRANCH} --oneline | read; then
    echo "${ICON_INFO} Votre branche locale est en avance sur la branche distante. Vous devriez pousser vos changements."
    # On pourrait proposer de pousser ici, mais le script se concentre sur la synchro entrante
fi

# Vérifier si on est en retard (commits distants à tirer)
if git log ${REMOTE_NAME}/${CURRENT_BRANCH}.. --oneline | read; then
    echo "${ICON_WARN} La branche distante contient des changements qui ne sont pas dans votre branche locale."
    echo "Changements distants :"
    git log --oneline --graph --decorate ${REMOTE_NAME}/${CURRENT_BRANCH}..HEAD

    read -p "Voulez-vous intégrer (pull) ces changements maintenant ? (oui/non): " CONFIRM_PULL
    if [ "$CONFIRM_PULL" = "oui" ]; then
        echo "${ICON_INFO} Intégration des changements depuis ${REMOTE_NAME}/${CURRENT_BRANCH}..."
        git pull --ff-only
        if [ $? -ne 0 ]; then
            echo "${ICON_ERROR} Le pull en fast-forward a échoué. Votre branche locale a probablement des commits divergents."
            echo "${ICON_INFO} Un rebase ou un merge manuel est nécessaire pour résoudre les conflits."
            exit 1
        fi
        echo "${ICON_SUCCESS} Votre branche a été mise à jour avec succès."
    else
        echo "${ICON_INFO} Opération annulée."
    fi
else
    echo "${ICON_INFO} Votre branche locale et la branche distante ont divergé. Un rebase ou un merge est nécessaire."
fi

echo "${ICON_SUCCESS} Opération de synchronisation terminée."
exit 0
