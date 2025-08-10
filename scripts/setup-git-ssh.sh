#!/bin/bash

# ==============================================================================
# Script d'assistance à la configuration SSH pour Git (GitHub)
#
# Ce script guide l'utilisateur à travers les étapes de vérification et de
# configuration de l'authentification SSH pour GitHub, en automatisant les
# parties possibles et en fournissant des instructions claires pour les
# étapes manuelles.
# ==============================================================================

# Inclut les variables et fonctions communes (icônes, etc.)
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_KEY} Assistant de configuration SSH pour Git (GitHub)"
echo "-------------------------------------------------"

# NOTE: Scenario 1 (SSH Agent Not Running) is currently non-testable due to automatic ssh-agent restarts on the user's system.
# The script's interactive prompt for starting the agent is in place, but cannot be fully automated for testing.

# 1. Vérifier et démarrer l'agent SSH
echo "${ICON_INFO} Étape 1: Vérification et démarrage de l'agent SSH."
if [ -z "$SSH_AGENT_PID" ] || ! ps -p $SSH_AGENT_PID > /dev/null; then
    echo "${ICON_WARN} L'agent SSH ne semble pas être en cours d'exécution ou ses variables d'environnement ne sont pas chargées."
    echo "${ICON_INFO} Veuillez exécuter la commande suivante dans votre terminal pour démarrer l'agent et charger ses variables :"
    echo "   eval \"$(ssh-agent -s)\""
    read -p "Avez-vous exécuté la commande ci-dessus et l'agent SSH a-t-il démarré avec succès ? (oui/non): " AGENT_STARTED
    if [ "$AGENT_STARTED" = "oui" ]; then
        echo "${ICON_SUCCESS} Agent SSH démarré et variables chargées (confirmé par l'utilisateur)."
    else
        echo "${ICON_ERROR} L'agent SSH n'a pas été démarré ou confirmé. Impossible de continuer sans un agent SSH fonctionnel."
        echo "${ICON_INFO} Pistes de résolution :"
        echo "   - Assurez-vous que 'ssh-agent' est installé sur votre système."
        echo "   - Redémarrez votre terminal et réessayez."
        echo "   - Vérifiez les messages d'erreur lors de l'exécution de 'eval \"$(ssh-agent -s)\'."
        exit 1
    fi
else
    echo "${ICON_SUCCESS} L'agent SSH est déjà en cours d'exécution et ses variables sont chargées."
fi


# 2. Ajouter la clé SSH à l'agent
echo ""
echo "${ICON_INFO} Étape 2: Ajout de votre clé SSH à l'agent."
echo "   Nous allons essayer d'ajouter la clé par défaut ou celle que vous spécifiez."
read -p "Entrez le chemin complet de votre clé privée SSH (laissez vide pour la clé par défaut ~/.ssh/github-teams-ai-python-env): " SSH_KEY_PATH
if [ -z "$SSH_KEY_PATH" ]; then
    SSH_KEY_PATH="$HOME/.ssh/github-teams-ai-python-env"
fi

if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "${ICON_ERROR} Le fichier de clé privée '${SSH_KEY_PATH}' n'existe pas."
    echo "${ICON_INFO} Veuillez vous assurer que la clé existe ou générez-en une nouvelle avec 'setup-git-ssh.sh'."
    exit 1
fi

if ! ssh-add -l | grep -q "$(ssh-keygen -lf "$SSH_KEY_PATH" | awk '{print $2}')"; then
    echo "${ICON_INFO} Ajout de la clé '${SSH_KEY_PATH}' à l'agent SSH..."
    ssh-add "$SSH_KEY_PATH"
    if [ $? -eq 0 ]; then
        echo "${ICON_SUCCESS} Clé ajoutée à l'agent SSH."
    else
        echo "${ICON_ERROR} Échec de l'ajout de la clé à l'agent SSH. Vérifiez votre mot de passe ou les permissions de la clé."
        exit 1
    fi
else
    echo "${ICON_SUCCESS} La clé '${SSH_KEY_PATH}' est déjà chargée dans l'agent SSH."
fi

# 3. Vérifier la clé publique sur GitHub
echo ""
echo "${ICON_INFO} Étape 3: Vérification de votre clé publique sur GitHub."
echo "   Ceci est une étape MANUELLE. Vous devez vous assurer que la clé publique"
echo "   correspondante à votre clé privée est bien ajoutée à votre compte GitHub."
echo "   Votre clé publique est généralement située à '${SSH_KEY_PATH}.pub'."
echo ""
echo "   Pour vérifier :"
echo "   1. Copiez le contenu de votre clé publique :"
echo "      cat '${SSH_KEY_PATH}.pub'"
echo "   2. Allez sur GitHub.com -> Settings -> SSH and GPG keys."
echo "   3. Assurez-vous que la clé copiée est présente dans la liste."
read -p "Avez-vous vérifié que votre clé publique est sur GitHub ? (oui/non): " CONFIRM_GITHUB_KEY
if [ "$CONFIRM_GITHUB_KEY" != "oui" ]; then
    echo "${ICON_WARN} Veuillez ajouter votre clé publique à GitHub pour que l'authentification fonctionne."
    exit 0
fi

# 4. Accepter la clé d'hôte de GitHub
echo ""
echo "${ICON_INFO} Étape 4: Acceptation de la clé d'hôte de GitHub."
echo "   Nous allons tenter une connexion test à GitHub pour ajouter leur clé d'hôte à vos 'known_hosts'."
echo "   Si vous êtes invité à confirmer, tapez 'yes'."
ssh -T git@github.com
SSH_TEST_STATUS=$?

if [ $SSH_TEST_STATUS -eq 1 ]; then
    echo "${ICON_SUCCESS} Authentification SSH à GitHub réussie (code 1 est normal pour ssh -T)."
elif [ $SSH_TEST_STATUS -eq 255 ]; then
    echo "${ICON_ERROR} Échec de la connexion SSH à GitHub (code 255). Cela peut indiquer un problème de réseau ou de pare-feu."
    exit 1
else
    echo "${ICON_WARN} La connexion SSH à GitHub a retourné un code inattendu ($SSH_TEST_STATUS)."
    echo "${ICON_INFO} Veuillez vérifier votre configuration SSH manuellement."
    exit 1
fi

echo ""
echo "${ICON_SUCCESS} Configuration SSH pour Git terminée. Vous devriez maintenant pouvoir pousser vos changements."
exit 0
