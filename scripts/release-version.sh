#!/bin/bash

# ==============================================================================
# Script de création de release (version + tag)
# GIT-REQ-005
#
# Ce script automatise le processus de création d'une nouvelle version :
# - Met à jour le fichier version.json
# - Crée un commit pour la version
# - Crée un tag Git annoté
# ==============================================================================

# Inclut les variables et fonctions communes
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_GIT} Assistant de création de Release"
echo "-----------------------------------------"

# 1. Vérifier si le dossier est un dépôt Git
if [ ! -d ".git" ]; then
    echo "${ICON_ERROR} Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser."
    exit 1
fi

# 2. Vérifier si le répertoire de travail est propre
if ! git diff-index --quiet HEAD --; then
    echo "${ICON_ERROR} Votre répertoire de travail n'est pas propre. Veuillez commiter ou ranger vos changements."
    git status
    exit 1
fi

echo "${ICON_SUCCESS} Le répertoire de travail est propre."

# La suite du script sera ajoutée ici

# --- Fonction pour déterminer la prochaine version ---
get_next_version() {
    local current_version=$1
    
    major=$(echo $current_version | cut -d. -f1)
    minor=$(echo $current_version | cut -d. -f2)
    patch=$(echo $current_version | cut -d. -f3)

    echo "${ICON_INFO} Version actuelle : ${current_version}"
    echo "Quel type de version est-ce ?"
    echo "  1) PATCH (correction de bug, ex: ${major}.${minor}.$((patch + 1)))"
    echo "  2) MINOR (ajout de fonctionnalité, ex: ${major}.$((minor + 1)).0)"
    echo "  3) MAJOR (changement majeur, ex: $((major + 1)).0.0)"
    read -p "Votre choix (1, 2, 3) : " version_choice

    case $version_choice in
        1)
            next_version="${major}.${minor}.$((patch + 1))"
            version_type="PATCH"
            ;;
        2)
            next_version="${major}.$((minor + 1)).0"
            version_type="MINOR"
            ;;
        3)
            next_version="$((major + 1)).0.0"
            version_type="MAJOR"
            ;;
        *)
            echo "${ICON_ERROR} Choix invalide."
            exit 1
            ;;
    esac
    # Retourne la version et le type pour la suite
    echo "$next_version $version_type"
}

# 3. Déterminer la prochaine version
read -r NEXT_VERSION VERSION_TYPE <<< $(get_next_version $VERSION)
echo "${ICON_INFO} La nouvelle version sera : ${NEXT_VERSION}"

# --- Fonction pour générer le message du tag ---
get_tag_message() {
    local version_type=$1
    local next_version=$2
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null)

    if [ "$version_type" = "PATCH" ]; then
        echo "${ICON_INFO} Génération automatique du message pour le PATCH..."
        if [ -z "$last_tag" ]; then
            # Cas où il n'y a aucun tag précédent
            log_messages=$(git log --oneline)
        else
            log_messages=$(git log --oneline "${last_tag}..HEAD")
        fi
        
        if [ -z "$log_messages" ]; then
            tag_message="Version ${next_version}\n\nAucun commit depuis le dernier tag."
        else
            tag_message="Version ${next_version}\n\nChangements inclus dans ce patch :\n${log_messages}"
        fi
        echo -e "$tag_message" # -e pour interpréter les \n
    elif [ "$version_type" = "MINOR" ]; then
        echo "${ICON_INFO} Veuillez décrire la nouvelle fonctionnalité :"
        read -p "> " user_message
        echo -e "feat: Version ${next_version}\n\n${user_message}"

    elif [ "$version_type" = "MAJOR" ]; then
        echo "${ICON_WARN} Les versions majeures indiquent des changements non rétrocompatibles."
        echo "${ICON_INFO} Veuillez justifier ce changement majeur :"
        read -p "> " user_message
        echo -e "BREAKING CHANGE: Version ${next_version}\n\n${user_message}"
    fi
}

# 4. Générer le message du tag
TAG_MESSAGE=$(get_tag_message $VERSION_TYPE $NEXT_VERSION)

# 5. Confirmer la release
echo ""
echo "${ICON_WARN} --- Résumé de la Release ---"
echo "  Nouvelle version : ${NEXT_VERSION}"
echo "  Message du tag   :"
echo "${TAG_MESSAGE}"
echo "---------------------------"
read -p "Confirmez-vous la création de cette release ? (oui/non): " CONFIRM_RELEASE

if [ "$CONFIRM_RELEASE" != "oui" ]; then
    echo "${ICON_INFO} Opération annulée."
    exit 0
fi

# 6. Exécuter la release
echo "${ICON_INFO} Mise à jour de version.json..."
# Utilisation de sed pour la compatibilité. Le \" est pour échapper les guillemets.
# Le -i.bak crée une sauvegarde sur macOS, -i sans extension sur Linux.
sed -i.bak "s/\"version\": \"${VERSION}\" / \"version\": \"${NEXT_VERSION}\" /" "$VERSION_FILE"
rm -f "${VERSION_FILE}.bak"

echo "${ICON_INFO} Création du commit pour la version..."
git add "$VERSION_FILE"
git commit -m "chore(release): Bump version to ${NEXT_VERSION}"

echo "${ICON_INFO} Création du tag Git annoté..."
git tag -a "v${NEXT_VERSION}" -m "$(echo -e "$TAG_MESSAGE")"

echo "${ICON_INFO} Poussée du commit et du tag vers le distant..."
git push
git push --tags

echo ""
echo "${ICON_SUCCESS} Release v${NEXT_VERSION} créée et poussée avec succès !"

