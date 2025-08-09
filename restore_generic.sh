#!/bin/bash

# ==============================================================================
# Script de restauration GÉNÉRIQUE de projet Git via SSH
#
# Utilisation:
# ./restore_generic.sh <utilisateur_github/nom_repo> <dossier_destination>
#
# Exemple:
# ./restore_generic.sh labinno01/teams-ai-python-env mon-projet-restaure
# ==============================================================================

# --- Validation des arguments ---
if [ "$#" -ne 2 ]; then
    echo "Erreur : Nombre d'arguments incorrect."
    echo "Usage: $0 <utilisateur_github/nom_repo> <dossier_destination>"
    exit 1
fi

# --- Configuration via les arguments ---
GITHUB_REPO_ID="$1"      # ex: labinno01/teams-ai-python-env
DESTINATION_FOLDER="$2"  # ex: mon-projet-restaure
GIT_REPO_URL="git@github.com:${GITHUB_REPO_ID}.git"

# Emplacement de la clé SSH par défaut (déjà générique).
SSH_KEY_PATH="$HOME/.ssh/id_rsa"
# --- Fin de la configuration ---


# Étape 1: Vérifier l'existence de la clé SSH.
echo "🔎 Vérification de l'existence d'une clé SSH sur cette machine..."

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "❌ Clé SSH non trouvée. Génération d'une nouvelle clé..."
    read -p "Entrez votre email GitHub pour l'associer à la clé : " user_email
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "$user_email"
    if [ $? -ne 0 ]; then
        echo "Erreur lors de la génération de la clé SSH. Le script ne peut pas continuer."
        exit 1
    fi
    echo "✅ Nouvelle clé SSH générée avec succès."
else
    echo "✅ Clé SSH existante trouvée : $SSH_KEY_PATH"
fi

# Étape 2: Afficher la clé publique et les instructions.
echo ""
echo "============================= ACTION REQUISE ============================="
echo "Pour que Git puisse s'authentifier, vous devez ajouter la clé SSH publique"
echo "suivante à votre compte GitHub."
echo ""
echo "1. Allez à l'adresse : https://github.com/settings/keys"
echo "2. Cliquez sur 'New SSH key'."
echo "3. Copiez le texte ci-dessous et collez-le dans le champ 'Key'."
echo "--------------------------------------------------------------------------"
cat "${SSH_KEY_PATH}.pub"
echo "--------------------------------------------------------------------------"
echo ""
read -p "Appuyez sur [Entrée] une fois que la clé a été ajoutée à GitHub..."
echo "=========================================================================="
echo ""


# Étape 3: Cloner le dépôt.
echo "🚀 Tentative de clonage du dépôt : $GIT_REPO_URL..."
git clone "$GIT_REPO_URL" "$DESTINATION_FOLDER"

if [ $? -eq 0 ]; then
  echo "✅ Le dépôt a été cloné avec succès dans le dossier : $DESTINATION_FOLDER"
else
  echo "❌ Une erreur est survenue lors du clonage."
  echo "   Vérifiez que vous avez bien ajouté la clé SSH à votre compte GitHub."
fi
