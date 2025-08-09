#!/bin/bash

# ==============================================================================
# Script générique de gestion de dépôt Git
#
# Ce script fournit une interface en ligne de commande pour effectuer
# les opérations Git de base de manière non-interactive.
# ==============================================================================

# --- Fonction d'aide ---
usage() {
    echo "Usage: $0 <commande> [arguments...]"
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
        echo "⚠️  L'identité Git (nom et email) n'est pas configurée pour ce dépôt."
        read -p "Entrez votre nom d'utilisateur Git : " git_user
        read -p "Entrez votre email Git : " git_email
        git config user.name "$git_user"
        git config user.email "$git_email"
        echo "✅ Identité Git configurée localement pour ce projet."
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
            echo "✅ Dépôt Git trouvé."
            exit 0
        else
            echo "❌ Aucun dépôt Git initialisé dans ce dossier."
            exit 1
        fi
        ;;

    init)
        if [ -d ".git" ]; then
            echo "ℹ️  Un dépôt Git existe déjà."
            exit 0
        fi
        git init
        echo "✅ Dépôt Git initialisé."
        ;;

    add-remote)
        if [ "$#" -ne 2 ]; then echo "Erreur: La commande 'add-remote' nécessite un <nom> et une <url>."; usage; fi
        git remote add "$1" "$2"
        echo "✅ Remote '$1' ajoutée avec l'URL : $2"
        ;;

    initial-commit)
        if [ "$#" -ne 1 ]; then echo "Erreur: La commande 'initial-commit' nécessite un <message>."; usage; fi
        check_git_config
        git add .
        # Vérifie s'il y a quelque chose à commiter pour éviter une erreur
        if git diff-index --quiet HEAD --; then
            echo "ℹ️  Aucun changement à commiter."
            exit 0
        fi
        git commit -m "$1"
        echo "✅ Commit initial créé avec le message : '$1'"
        ;;

    push)
        if [ "$#" -ne 2 ]; then echo "Erreur: La commande 'push' nécessite un <nom_remote> et une <nom_branche>."; usage; fi
        echo "🚀 Poussée de la branche '$2' vers la remote '$1'..."
        # L'option -u établit le suivi pour les futurs 'git pull'
        git push -u "$1" "$2"
        if [ $? -eq 0 ]; then
            echo "✅ Push réussi."
        else
            echo "❌ Le push a échoué. Vérifiez l'URL de la remote et vos permissions."
            exit 1
        fi
        ;;

    *)
        echo "Erreur: Commande '$COMMAND' inconnue."
        usage
        ;;
esac

exit 0
