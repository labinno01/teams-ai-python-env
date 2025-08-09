#!/bin/bash

# ==============================================================================
# Script de création de clé SSH dédiée à un projet
# GIT-REQ-001
#
# Ce script guide l'utilisateur pour générer une nouvelle paire de clés SSH
# (ed25519) et affiche la clé publique pour une copie facile.
# ==============================================================================

# Inclut les variables et fonctions communes (icônes, etc.)
# Le chemin est relatif à l'emplacement du script lui-même.
source "$(dirname "$0")/_common.sh"

# Gestion de l'argument --version
if [ "$1" = "--version" ]; then
    echo "$(basename "$0") version $VERSION"
    exit 0
fi

# --- Début du Script ---
echo "${ICON_KEY} Assistant de création de clé SSH pour projet"
echo "-------------------------------------------------"

# 1. Demander le nom de la clé
DEFAULT_KEY_NAME="github-$(basename "$(pwd)")"
read -p "Entrez un nom pour la clé (par défaut: ${DEFAULT_KEY_NAME}): " KEY_NAME
if [ -z "$KEY_NAME" ]; then
    KEY_NAME="$DEFAULT_KEY_NAME"
fi
if [ -z "$KEY_NAME" ]; then
    echo "${ICON_ERROR} Le nom de la clé ne peut pas être vide."
    exit 1
fi

# Chemin complet vers le fichier de la clé privée
KEY_PATH="$HOME/.ssh/$KEY_NAME"

# 2. Vérifier si la clé existe déjà
if [ -f "$KEY_PATH" ]; then
    echo "${ICON_WARN} Le fichier de clé '${KEY_PATH}' existe déjà."
    read -p "Voulez-vous l'écraser ? Cette action est irréversible. (tapez 'oui' pour confirmer): " CONFIRM_OVERWRITE
    if [ "$CONFIRM_OVERWRITE" != "oui" ]; then
        echo "${ICON_INFO} Opération annulée."
        exit 0
    fi
    echo "${ICON_INFO} La clé existante sera écrasée."
fi

# 3. Demander l'email
read -p "Entrez votre adresse email (associée à la clé): " EMAIL
if [ -z "$EMAIL" ]; then
    echo "${ICON_ERROR} L'adresse email ne peut pas être vide."
    exit 1
fi

# 4. Générer la clé
echo "${ICON_INFO} Génération de la clé ed25519..."
# -t ed25519 : algorithme moderne et sécurisé
# -C "$EMAIL" : commentaire (généralement l'email)
# -f "$KEY_PATH" : chemin complet du fichier de la clé
# -N "" : aucune passphrase (pour les clés de déploiement/automatisées)
ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY_PATH" -N ""

# 5. Vérifier le succès et afficher la clé publique
if [ $? -eq 0 ]; then
    echo "${ICON_SUCCESS} Clé générée avec succès dans ${KEY_PATH}"
    echo ""
    echo "-------------------------------------------------"
    echo "${ICON_CLIPBOARD} Voici votre clé publique à copier :"
    echo "-------------------------------------------------"
    cat "${KEY_PATH}.pub"
    echo "-------------------------------------------------"
    echo ""
    echo "${ICON_INFO} Prochaine étape :"
    echo "1. Copiez l'intégralité de la clé ci-dessus (de 'ssh-ed25519' à votre email)."
    echo "2. Allez sur votre plateforme Git (GitHub, GitLab, etc.)."
    echo "3. Collez-la dans la section 'SSH and GPG keys' de vos paramètres ou dans les 'Deploy Keys' de votre dépôt."
else
    echo "${ICON_ERROR} Une erreur est survenue lors de la génération de la clé."
    exit 1
fi

exit 0
