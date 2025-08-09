#!/bin/bash

# ==============================================================================
# Script de restauration du projet Git via SSH
#
# Ce script configure l'environnement pour cloner le dépôt Git en utilisant
# une clé SSH pour l'authentification.
# ==============================================================================

# --- Configuration ---
# L'URL SSH de votre dépôt. Changez-la si nécessaire.
GIT_REPO_URL="git@github.com:labinno01/teams-ai-python-env.git"

# Le nom du dossier où le projet sera cloné.
DESTINATION_FOLDER="teams-ai-python-env-restored"

# Emplacement de la clé SSH par défaut.
SSH_KEY_PATH="$HOME/.ssh/id_rsa"
# --- Fin de la configuration ---


# Étape 1: Vérifier l'existence de la clé SSH.
echo "🔎 Vérification de l'existence d'une clé SSH sur cette machine..."

if [ ! -f "$SSH_KEY_PATH" ]; then
    # Si la clé n'existe pas, on la génère.
    echo "❌ Clé SSH non trouvée. Génération d'une nouvelle clé..."
    
    # Demander l'email de l'utilisateur pour l'associer à la clé.
    read -p "Entrez votre email GitHub pour l'associer à la clé : " user_email

    # Génération de la clé sans phrase de passe pour une utilisation non-interactive.
    # C'est pratique pour les scripts, mais moins sécurisé qu'une clé avec phrase de passe.
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "$user_email"

    if [ $? -ne 0 ]; then
        echo "Erreur lors de la génération de la clé SSH. Le script ne peut pas continuer."
        exit 1
    fi
    echo "✅ Nouvelle clé SSH générée avec succès."
else
    echo "✅ Clé SSH existante trouvée : $SSH_KEY_PATH"
fi

# Étape 2: Afficher la clé publique et les instructions pour l'utilisateur.
echo ""
echo "============================= ACTION REQUISE ============================="
echo "Pour que Git puisse s'authentifier, vous devez ajouter la clé SSH publique"
echo "suivante à votre compte GitHub."
echo ""
echo "1. Allez à l'adresse suivante dans votre navigateur :"
echo "   https://github.com/settings/keys"
echo ""
echo "2. Cliquez sur 'New SSH key'."
echo "3. Donnez-lui un titre (ex: 'Ma Nouvelle Machine')."
echo "4. Copiez l'intégralité du texte ci-dessous (commençant par 'ssh-rsa') et"
echo "   collez-le dans le champ 'Key'."
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
  echo "   Il peut y avoir un délai de quelques instants avant qu'elle ne soit active."
fi
