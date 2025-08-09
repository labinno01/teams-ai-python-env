#!/bin/bash

# ==============================================================================
# Script générique de gestion de dépôt Git (avec gestion des emojis)
#
# Ce script fournit une interface en ligne de commande pour effectuer
# les opérations Git de base de manière non-interactive et portable.
# ==============================================================================

# --- Gestion des icônes (emojis) ---
USE_EMOJI=true # Par défaut, on essaie d'utiliser les emojis

# Vérifier si l'option --no-emoji est passée en premier argument
if [ "$1" = "--no-emoji" ]; then
    USE_EMOJI=false
    shift # On retire l'argument pour ne pas perturber la suite du script
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
    ICON_ROCKET="🚀"
else
    ICON_SUCCESS="[OK]"
    ICON_ERROR="[ERROR]"
    ICON_INFO="[INFO]"
    ICON_WARN="[WARNING]"
    ICON_ROCKET=">>"
fi
# --- Fin de la gestion des icônes ---


# --- Fonction d'aide ---
usage() {
    echo "Usage: $0 [--no-emoji] <commande> [arguments...]"
    echo ""
    echo "Options:"
    echo "  --no-emoji                       Désactive l'affichage des emojis."
    echo ""
    echo "Commandes disponibles:"
    echo "  check                            Vérifie si le dossier courant est un dépôt Git."
    echo "  init                             Initialise un dépôt Git s'il n'en existe pas."
    echo "  add-remote <nom> <url>           Ajoute une remote au dépôt."
    echo "  initial-commit <message>         Crée le commit initial avec tous les fichiers."
    echo "  push <nom_remote> <nom_branche>  Pousse une branche vers une remote."
    echo ""
    exit 1
}

# --- Fonction pour vérifier la configuration Git ---
check_git_config() {
    local_user=$(git config user.name)
    local_email=$(git config user.email)

    if [ -z "$local_user" ] || [ -z "$local_email" ]; then
        echo "${ICON_WARN}  L'identité Git (nom et email) n'est pas configurée pour ce dépôt."
        read -p "Entrez votre nom d'utilisateur Git : " git_user
        read -p "Entrez votre email Git : " git_email
        git config user.name "$git_user"
        git config user.email "$git_email"
        echo "${ICON_SUCCESS} Identité Git configurée localement pour ce projet."
    fi
}

# --- Commande principale ---
COMMAND="$1"
if [ -z "$COMMAND" ]; then
    usage
fi
shift # Décale les arguments pour que $1 soit maintenant le premier paramètre de la commande

# --- Logique des commandes ---
case "$COMMAND" in
    check)
        if [ -d ".git" ]; then
            echo "${ICON_SUCCESS} Dépôt Git trouvé."
            exit 0
        else
            echo "${ICON_ERROR} Aucun dépôt Git initialisé dans ce dossier."
            exit 1
        fi
        ;;

    init)
        if [ -d ".git" ]; then
            echo "${ICON_INFO}  Un dépôt Git existe déjà."
            exit 0
        fi
        git init
        echo "${ICON_SUCCESS} Dépôt Git initialisé."
        ;;

    add-remote)
        if [ "$#" -ne 2 ]; then echo "Erreur: La commande 'add-remote' nécessite un <nom> et une <url>."; usage; fi
        git remote add "$1" "$2"
        echo "${ICON_SUCCESS} Remote '$1' ajoutée avec l'URL : $2"
        ;;

    initial-commit)
        if [ "$#" -ne 1 ]; then echo "Erreur: La commande 'initial-commit' nécessite un <message>."; usage; fi
        check_git_config
        git add .
        # Vérifie s'il y a quelque chose à commiter pour éviter une erreur
        if git diff-index --quiet HEAD --; then
            echo "${ICON_INFO}  Aucun changement à commiter."
            exit 0
        fi
        git commit -m "$1"
        echo "${ICON_SUCCESS} Commit initial créé avec le message : '$1'"
        ;;

    push)
        if [ "$#" -ne 2 ]; then echo "Erreur: La commande 'push' nécessite un <nom_remote> et une <nom_branche>."; usage; fi
        echo "${ICON_ROCKET} Poussée de la branche '$2' vers la remote '$1'..."
        # L'option -u établit le suivi pour les futurs 'git pull'
        git push -u "$1" "$2"
        if [ $? -eq 0 ]; then
            echo "${ICON_SUCCESS} Push réussi."
        else
            echo "${ICON_ERROR} Le push a échoué. Vérifiez l'URL de la remote et vos permissions."
            exit 1
        fi
        ;;

    *)
        echo "Erreur: Commande '$COMMAND' inconnue."
        usage
        ;;
esac

exit 0
