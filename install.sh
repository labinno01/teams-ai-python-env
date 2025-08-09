#!/bin/bash

# ==============================================================================
# Script d'Installation du "Patrimoine de Scripts Git"
#
# Ce script télécharge et installe la dernière version des scripts utilitaires
# Git depuis le dépôt de référence sur GitHub.
#
# Utilisation :
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/labinno01/teams-ai-python-env/main/install.sh)"
# ==============================================================================

# --- Configuration ---
# Modifiez cette variable si vous forkez le projet ou si vous voulez utiliser
# votre propre dépôt privé (assurez-vous d'utiliser l'URL SSH dans ce cas).
REPO_URL="https://raw.githubusercontent.com/labinno01/teams-ai-python-env/main"

# Nom du dossier où les scripts seront installés.
INSTALL_DIR=".git-scripts"

# Liste des scripts à installer.
SCRIPTS_TO_INSTALL=(
    "_common.sh"
    "setup-ssh.sh"
    "init-repository.sh"
    "commit-push.sh"
    "sync-remote.sh"
    "release-version.sh"
)

# --- Fonctions Utilitaires ---
# Affiche un message d'information.
# Renamed from écho_info to echo_info
echo_info() {
    echo "[INFO] $1"
}

# Affiche un message de succès.
# Renamed from écho_success to echo_success
echo_success() {
    echo "✅ [SUCCES] $1"
}

# Affiche un message d'erreur et quitte.
# Renamed from écho_error to echo_error
echo_error() {
    echo "❌ [ERREUR] $1" >&2
    exit 1
}

# --- Début du Script ---
# Renamed from écho_info to echo_info
echo_info "Installation du Patrimoine de Scripts Git..."

# 1. Vérifier si curl est installé
if ! command -v curl &> /dev/null; then
    echo_error "curl n'est pas installé. Veuillez l'installer pour continuer."
fi

# 2. Créer le répertoire d'installation
# Renamed from écho_info to echo_info
echo_info "Création du répertoire d'installation : ${INSTALL_DIR}"
if [ -d "$INSTALL_DIR" ]; then
    echo_info "Le répertoire existe déjà. Il sera mis à jour."
else
    mkdir "$INSTALL_DIR"
    if [ $? -ne 0 ]; then
        echo_error "Impossible de créer le répertoire ${INSTALL_DIR}."
    fi
fi

# 3. Télécharger les scripts
# Renamed from écho_info to echo_info
echo_info "Téléchargement des scripts depuis le dépôt..."
for script in "${SCRIPTS_TO_INSTALL[@]}"; do
    echo "  -> Téléchargement de ${script}..."
    curl -fsSL "${REPO_URL}/scripts/${script}" -o "${INSTALL_DIR}/${script}"
    if [ $? -ne 0 ]; then
        echo_error "Échec du téléchargement de ${script}."
    fi
done

# 4. Télécharger le fichier de version
# Renamed from echo_info to echo_info
echo_info "Téléchargement du fichier de version..."
curl -fsSL "${REPO_URL}/version.json" -o "${INSTALL_DIR}/version.json"
if [ $? -ne 0 ]; then
    echo_error "Échec du téléchargement de version.json."
fi

# 5. Télécharger le workflow CI/CD
# Renamed from echo_info to echo_info
echo_info "Téléchargement du workflow CI/CD..."
mkdir -p ".github/workflows"
curl -fsSL "${REPO_URL}/.github/workflows/lint.yml" -o ".github/workflows/lint.yml"
if [ $? -ne 0 ]; then
    echo_error "Échec du téléchargement de .github/workflows/lint.yml."
fi

# 6. Rendre les scripts exécutables
# Renamed from echo_info to echo_info
echo_info "Attribution des permissions d'exécution..."
for script in "${SCRIPTS_TO_INSTALL[@]}"; do
    # On ne rend pas _common.sh exécutable car il est sourcé
    if [ "$script" != "_common.sh" ]; then
        chmod +x "${INSTALL_DIR}/${script}"
    fi
done

# 7. Ajouter au .gitignore
# Renamed from écho_info to echo_info
echo_info "Mise à jour du .gitignore..."
if [ -f ".gitignore" ]; then
    if ! grep -q "^${INSTALL_DIR}/$" .gitignore; then
        read -p "Voulez-vous ajouter '${INSTALL_DIR}/' à votre .gitignore ? (oui/non): " add_to_gitignore
        if [ "$add_to_gitignore" = "oui" ]; then
            echo "" >> .gitignore
            echo "# Dossier des scripts utilitaires Git" >> .gitignore
            echo "${INSTALL_DIR}/" >> .gitignore
            echo_info "Le dossier a été ajouté au .gitignore."
        fi
    else
        echo_info "Le dossier est déjà dans le .gitignore."
    fi
fi

# --- Fin de l'Installation ---


# Renamed from écho_success to echo_success
echo_success "Installation terminée !"



# Renamed from echo to echo
echo "Comment utiliser les scripts :"
# Renamed from echo to echo
echo "  Les scripts sont installés dans le dossier '${INSTALL_DIR}'."
# Renamed from echo to echo
echo "  Exemple : ./${INSTALL_DIR}/commit-push.sh \"Mon message de commit\""
# Renamed from echo to echo
echo ""
# Renamed from echo to echo
echo "Vous pouvez ajouter ce dossier à votre PATH pour un accès plus facile :"
# Renamed from echo to echo
echo "  export PATH=\"$PATH:$(pwd)/${INSTALL_DIR}\""
# Renamed from echo to echo
echo ""
# Renamed from echo to echo
echo "Le workflow CI/CD a été installé dans .github/workflows/lint.yml."
# Renamed from echo to echo
echo "Pensez à le commiter et le pousser pour l'activer sur GitHub."