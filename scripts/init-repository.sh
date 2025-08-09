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

# Fonction pour sélectionner le chemin du dépôt
select_repository_path() {
    local DEFAULT_BASE_DIR="/mnt/d/projets-python"
    local PROJECT_NAME=""
    local REPO_PATH=""

    # Demander le nom du projet pour le chemin par défaut
    local VALID_PROJECT_NAME=false
    while [ "$VALID_PROJECT_NAME" = false ]; do
        read -p "Entrez le nom du projet (ex: mon-super-projet, sans espaces ni caractères spéciaux): " PROJECT_NAME
        if [ -z "$PROJECT_NAME" ]; then
            echo "${ICON_ERROR} Le nom du projet ne peut pas être vide. Veuillez réessayer."
        elif [[ "$PROJECT_NAME" =~ [[:space:]] ]] || [[ "$PROJECT_NAME" =~ [^a-zA-Z0-9_-] ]]; then
            echo "${ICON_ERROR} Le nom du projet ne doit pas contenir d'espaces ni de caractères spéciaux (seuls les lettres, chiffres, tirets et underscores sont autorisés). Veuillez réessayer."
        else
            VALID_PROJECT_NAME=true
        fi
    done

    # Construire le chemin par défaut
    local DEFAULT_REPO_PATH="${DEFAULT_BASE_DIR}/${PROJECT_NAME}"

    local VALID_PATH=false
    while [ "$VALID_PATH" = false ]; do
        read -p "Entrez le chemin du dépôt local [${DEFAULT_REPO_PATH}]: " REPO_PATH_INPUT
        if [ -z "$REPO_PATH_INPUT" ]; then
            REPO_PATH="${DEFAULT_REPO_PATH}"
        else
            REPO_PATH="${REPO_PATH_INPUT}"
        fi

        # Vérifier si le chemin est absolu
        if [[ ! "$REPO_PATH" = /* ]]; then
            echo "${ICON_ERROR} Le chemin doit être un chemin absolu. Veuillez réessayer."
        else
            VALID_PATH=true
        fi
    done

    # Assigner le chemin final à une variable globale ou le retourner
    # Pour l'instant, nous allons l'assigner à une variable globale pour la suite du script
    SELECTED_REPO_PATH="$REPO_PATH"
}

# Appeler la fonction de sélection de chemin
select_repository_path

echo "${ICON_INFO} Chemin du dépôt sélectionné : ${SELECTED_REPO_PATH}"

# Naviguer vers le répertoire sélectionné ou le créer
if [ ! -d "$SELECTED_REPO_PATH" ]; then
    echo "${ICON_INFO} Création du répertoire ${SELECTED_REPO_PATH}..."
    mkdir -p "$SELECTED_REPO_PATH"
    if [ $? -ne 0 ]; then
        echo "${ICON_ERROR} Impossible de créer le répertoire ${SELECTED_REPO_PATH}."
        exit 1
    fi
fi

# Se déplacer dans le répertoire pour les opérations Git
cd "$SELECTED_REPO_PATH" || exit 1

# Vérifier si le répertoire n'est pas vide avant l'initialisation Git
if [ -n "$(ls -A)" ]; then
    echo "${ICON_WARN} Le répertoire '${SELECTED_REPO_PATH}' n'est pas vide."
    echo "${ICON_INFO} Que souhaitez-vous faire ?"
    echo "  1) Supprimer tout le contenu existant et initialiser un nouveau dépôt."
    echo "  2) Initialiser le dépôt Git ici et inclure les fichiers existants (fusion)."
    echo "  3) Annuler l'opération."
    read -p "Votre choix (1-3) [3]: " CHOICE
    CHOICE=${CHOICE:-3} # Défaut à '3' (Annuler) si vide

    case $CHOICE in
        1)
            read -p "Êtes-vous sûr de vouloir SUPPRIMER TOUT le contenu de '${SELECTED_REPO_PATH}' ? (oui/NON): " CONFIRM_DELETE
            CONFIRM_DELETE=${CONFIRM_DELETE:-non} # Défaut à 'non' si vide
            if [ "$CONFIRM_DELETE" = "oui" ]; then
                echo "${ICON_INFO} Suppression du contenu existant..."
                find . -mindepth 1 -delete
                if [ $? -ne 0 ]; then
                    echo "${ICON_ERROR} Échec de la suppression du contenu existant."
                    exit 1
                fi
                echo "${ICON_SUCCESS} Contenu existant supprimé."
            else
                echo "${ICON_INFO} Opération annulée."
                exit 0
            fi
            ;;
        2)
            echo "${ICON_INFO} Initialisation du dépôt Git avec les fichiers existants."
            ;;
        3)
            echo "${ICON_INFO} Opération annulée."
            exit 0
            ;;
        *)
            echo "${ICON_ERROR} Choix invalide. Opération annulée."
            exit 1
            ;;
    esac
fi

# 1. Vérifier si le dépôt est déjà initialisé
if [ -d ".git" ]; then
    echo "${ICON_INFO} Ce dossier est déjà un dépôt Git."
    echo "${ICON_INFO} Informations sur le dépôt existant :"
    echo "  - Branche actuelle : $(git branch --show-current 2>/dev/null || echo 'N/A')"
    echo "  - URL du remote 'origin' : $(git remote get-url origin 2>/dev/null || echo 'N/A')"
    echo "  - Premier commit : $(git log --reverse --pretty=format:"%s (%ad)" --date=short 2>/dev/null | head -1 || echo 'N/A')"
    echo "  - Dernier commit : $(git log -1 --pretty=format:"%s (%ad)" --date=short 2>/dev/null || echo 'N/A')"
    echo "  - Statut du répertoire de travail :"
    git status --short 2>/dev/null || echo '    N/A'

    read -p "Voulez-vous continuer avec ce dépôt existant ? (OUI/non): " CONFIRM_EXISTING_REPO
    CONFIRM_EXISTING_REPO=${CONFIRM_EXISTING_REPO:-oui} # Défaut à 'oui' si vide

    if [ "$CONFIRM_EXISTING_REPO" != "oui" ]; then
        echo "${ICON_INFO} Opération annulée."
        exit 0
    fi
    # Si l'utilisateur choisit de continuer, le script continuera à partir d'ici.
    # Cela signifie qu'il passera à l'étape 2 (Initialisation), mais comme .git existe,
    # l'initialisation sera ignorée ou gérée par Git lui-même (pas de réinitialisation forcée).
    # Le script continuera ensuite avec la vérification de la configuration Git, etc.
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
    read -p "Voulez-vous continuer et lier votre projet local à ce dépôt ? (oui/NON): " CONFIRM_LINK
    CONFIRM_LINK=${CONFIRM_LINK:-non} # Défaut à 'non' si vide
    if [ "$CONFIRM_LINK" != "oui" ]; then
        echo "${ICON_INFO} Opération annulée. Vous devriez peut-être utiliser 'git clone' à la place."
        # Nettoyage du git init pour laisser le dossier propre
        rm -rf .git
        echo "${ICON_INFO} Le dépôt local qui venait d'être créé a été supprimé."
        exit 0
    fi
fi

# 6. Ajouter le remote
if git remote get-url origin &> /dev/null; then
    echo "${ICON_INFO} Le remote 'origin' existe déjà. URL actuelle : $(git remote get-url origin)"
    read -p "Voulez-vous le mettre à jour avec la nouvelle URL '$REMOTE_URL' ? (oui/NON): " UPDATE_REMOTE
    UPDATE_REMOTE=${UPDATE_REMOTE:-non} # Défaut à 'non' si vide
    if [ "$UPDATE_REMOTE" = "oui" ]; then
        git remote set-url origin "$REMOTE_URL"
        if [ $? -ne 0 ]; then
            echo "${ICON_ERROR} Échec de la mise à jour du remote 'origin'. Vérifiez l'URL."
            exit 1
        fi
        echo "${ICON_SUCCESS} Remote 'origin' mis à jour."
    else
        echo "${ICON_INFO} Le remote 'origin' existant a été conservé."
    fi
else
    git remote add origin "$REMOTE_URL"
    if [ $? -ne 0 ]; then
        echo "${ICON_ERROR} Échec de l'ajout du remote. Vérifiez l'URL."
        exit 1
    fi
    echo "${ICON_SUCCESS} Dépôt distant ajouté sous le nom 'origin'."
fi

# 7. Créer ou mettre à jour un README initial
echo "# $(basename "$PWD")" > README.md
echo "<!-- Initialisation du dépôt : $(date) -->" >> README.md
echo "${ICON_SUCCESS} Fichier README.md créé ou mis à jour."

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
read -p "Voulez-vous envoyer votre projet sur le serveur distant (GitHub) maintenant ? (oui/NON): " PUSH_NOW
PUSH_NOW=${PUSH_NOW:-non} # Défaut à 'non' si vide
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
