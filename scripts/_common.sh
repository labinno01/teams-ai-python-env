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

# --- Fonction pour vérifier l'authentification SSH à GitHub ---
check_ssh_auth() {
    echo "${ICON_INFO} Vérification de l'authentification SSH à GitHub..."
    # Tente une connexion SSH silencieuse à GitHub
    ssh -T git@github.com &> /dev/null
    local ssh_status=$?

    if [ $ssh_status -eq 1 ]; then
        # Code 1 signifie authentification réussie mais pas d'accès shell (comportement normal de ssh -T)
        echo "${ICON_SUCCESS} Authentification SSH à GitHub réussie."
        return 0
    elif [ $ssh_status -eq 255 ]; then
        # Code 255 signifie échec de connexion (Permission denied, Host key verification failed, etc.)
        echo "${ICON_ERROR} Échec de l'authentification SSH à GitHub."
        echo "${ICON_INFO} Voici les étapes pour résoudre le problème :"
        echo "1. Assurez-vous que votre agent SSH est démarré :"
        # echo "   eval \"$(ssh-agent -s)\"" # Commented out for debugging
        echo "2. Ajoutez votre clé SSH à l'agent (remplacez 'votre_cle' par le nom de votre clé, ex: id_rsa, github-monprojet) :"
        echo "   ssh-add ~/.ssh/votre_cle"
        echo "   (Si votre clé a un mot de passe, il vous sera demandé.)"
        echo "3. Vérifiez que votre clé publique est bien ajoutée à votre compte GitHub :"
        echo "   Allez sur GitHub -> Settings -> SSH and GPG keys."
        echo "4. Acceptez la clé d'hôte de GitHub \(si ce n'est pas déjà fait\) en exécutant :"
        echo "   ssh -T git@github.com"
        echo "   (Tapez 'yes' si on vous le demande pour accepter l'empreinte digitale.)"
        exit 1
    else
        # Autre code de retour (ex: 0 si pas de clé, ou autre erreur)
        echo "${ICON_WARN} Un problème inattendu est survenu lors de la vérification SSH (code: $ssh_status)."
        echo "${ICON_INFO} Veuillez vérifier votre configuration SSH manuellement."
        exit 1
    fi
}
