# `setup-git-ssh.sh`

Ce script assiste l'utilisateur dans la configuration et le dépannage de l'authentification SSH pour Git, en particulier pour GitHub. Il automatise les étapes possibles et fournit des instructions claires pour les actions manuelles requises.

## Fonctionnalités

*   **Vérification et démarrage de l'agent SSH :** Le script vérifie si l'agent SSH est en cours d'exécution et propose de le démarrer si ce n'est pas le cas.
*   **Ajout de la clé SSH à l'agent :** Il guide l'utilisateur pour ajouter sa clé privée SSH à l'agent, en proposant un chemin par défaut et en vérifiant si la clé est déjà chargée.
*   **Vérification de la clé publique sur GitHub (manuel) :** Le script fournit des instructions claires pour que l'utilisateur vérifie manuellement que sa clé publique correspondante est bien ajoutée à son compte GitHub.
*   **Acceptation de la clé d'hôte de GitHub :** Il tente une connexion test à GitHub pour s'assurer que la clé d'hôte de GitHub est ajoutée aux `known_hosts` de l'utilisateur, ce qui est crucial pour éviter les avertissements de sécurité lors des premières connexions.

## Utilisation

Pour exécuter le script, naviguez jusqu'au répertoire `scripts/` de votre projet et exécutez :

```bash
bash setup-git-ssh.sh
```

Suivez les instructions et les invites du script. Il vous guidera à travers les différentes étapes et vous fournira des messages de succès ou d'erreur avec des conseils pour résoudre les problèmes.

## Exemples d'utilisation

*   **Démarrer l'agent SSH et ajouter une clé :**
    Le script vous demandera si vous souhaitez démarrer l'agent SSH s'il n'est pas actif. Ensuite, il vous invitera à fournir le chemin de votre clé SSH privée (par exemple, `~/.ssh/id_rsa` ou `~/.ssh/github-monprojet`).

*   **Vérifier l'authentification GitHub :**
    Après avoir configuré votre clé, le script effectuera un test de connexion à GitHub pour confirmer que tout est correctement configuré pour les opérations Git via SSH.

## Dépendances

Ce script dépend du fichier `_common.sh` pour les fonctions utilitaires et les icônes. Assurez-vous que `_common.sh` est présent dans le même répertoire.
