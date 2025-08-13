# Gestionnaire de Clés SSH v3

Ceci est la documentation pour le nouveau gestionnaire de clés SSH basé sur Python.

## Commandes

Voici une liste des commandes disponibles :

*   `assist` : Configure automatiquement l'accès SSH pour un hôte à partir d'une URL.
*   `backup` : Sauvegarde le fichier `~/.ssh/config`.
*   `config-list` : Liste les hôtes configurés dans `~/.ssh/config`.
*   `create` : Crée une nouvelle clé SSH.
*   `debug` : Affiche les informations de débogage sur l'agent SSH.
*   `delete` : Supprime une clé SSH.
*   `init` : Charge une ou plusieurs clés dans l'agent SSH.
*   `known` : Gère le fichier `known_hosts`.
*   `list` : Liste les fichiers de clés privées dans le répertoire `~/.ssh`.
*   `reload` : Décharge toutes les clés de l'agent, puis charge les clés spécifiées.
*   `status` : Affiche les clés actuellement chargées dans l'agent SSH.