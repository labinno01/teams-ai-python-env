#!/bin/bash

# ==============================================================================
# Fichier utilitaire commun pour les scripts Git
#
# Ce fichier n'est pas destiné à être exécuté directement. Il doit être
# "sourcé" par d'autres scripts pour fournir des fonctions et des
# variables communes, comme la gestion des icônes.
#
# Exemple d'inclusion :
# source "$(dirname "$0")/_common.sh"
# ==============================================================================

# --- Versioning ---
# Lit la version depuis le fichier version.json à la racine du projet.
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
VERSION_FILE="$GIT_ROOT/.git-scripts/version.json"

if [ -f "$VERSION_FILE" ]; then
    # Utilise sed pour extraire la valeur. C'est plus portable que jq.
    VERSION=$(grep -o '"version": "[^"]*"' "$VERSION_FILE" | sed 's/"version": "//;s/"//')
else
    VERSION="dev"
fi


# --- Gestion des icônes (emojis) ---
USE_EMOJI=true # Par défaut, on essaie d'utiliser les emojis

# Vérifier si l'option --no-emoji est passée en premier argument du script parent
if [ "$1" = "--no-emoji" ]; then
    USE_EMOJI=false
fi

# Si les emojis sont toujours activés, on vérifie le support UTF-8
if [ "$USE_EMOJI" = true ]; then
    # Commande simple pour vérifier si la locale contient "UTF-8" ou "utf8"
    if ! locale | grep -iq "utf-8\|utf8"; then
        USE_EMOJI=false
        echo "[INFO] Terminal non-UTF-8 détecté, les emojis sont désactivés."
    fi
fi

# On définit les icônes en fonction du résultat
if [ "$USE_EMOJI" = true ]; then
    ICON_SUCCESS="✅"
    ICON_ERROR="❌"
    ICON_INFO="ℹ️"
    ICON_WARN="⚠️"
    ICON_CLIPBOARD="📋"
    ICON_KEY="🔑"
    ICON_GIT=""
else
    ICON_SUCCESS="[OK]"
    ICON_ERROR="[ERROR]"
    ICON_INFO="[INFO]"
    ICON_WARN="[WARNING]"
    ICON_CLIPBOARD="[COPY]"
    ICON_KEY="[KEY]"
    ICON_GIT="[GIT]"
fi
# --- Fin de la gestion des icônes ---


# --- Fonction pour vérifier la configuration Git ---
check_git_config() {
    local_user=$(git config user.name)
    local_email=$(git config user.email)

    if [ -z "$local_user" ] || [ -z "$local_email" ]; then
        echo "${ICON_WARN} L'identité Git (nom et email) n'est pas configurée pour ce dépôt."
        read -p "Entrez votre nom d'utilisateur Git : " git_user
        read -p "Entrez votre email Git : " git_email
        git config user.name "$git_user"
        git config user.email "$git_email"
        echo "${ICON_SUCCESS} Identité Git configurée localement pour ce projet."
    fi
}