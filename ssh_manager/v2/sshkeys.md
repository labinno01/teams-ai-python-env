# SSH Key Manager v2.5

Un utilitaire en ligne de commande pour gérer de manière fluide les clés SSH, de leur création à leur configuration pour des services comme GitHub ou GitLab.

## Fonctionnalités

- **Cycle de vie complet :** Crée, charge, supprime et configure les clés SSH.
- **Gestion de `~/.ssh/config` :** Ajoute et supprime automatiquement les configurations d'hôtes lorsque vous gérez vos clés.
- **Mode double :** Entièrement interactif pour un usage manuel et scriptable avec des options pour l'automatisation.
- **Sécurisé :** Demande toujours confirmation avant d'écraser une clé et archive les anciennes clés par sécurité.
- **Introspection :** Commandes `status`, `list`, et `debug` pour inspecter l'état de l'agent et des fichiers.

## Prérequis

Ce script interagit avec l'agent SSH de votre système. Assurez-vous qu'il est bien en cours d'exécution dans votre session de terminal. Si ce n'est pas le cas, démarrez-le avec :

```bash
eval $(ssh-agent -s)
```

## Installation

1.  Placez le script `sshkeys.sh` dans un dossier de votre `PATH` (ex: `~/.local/bin`).
    ```bash
    mkdir -p ~/.local/bin
    cp sshkeys.sh ~/.local/bin/sshkeys
    chmod +x ~/.local/bin/sshkeys
    ```
2.  Vous pouvez maintenant l'appeler de n'importe où avec la commande `sshkeys`.

## Commandes

### `create`

Crée une nouvelle clé SSH, la charge dans l'agent et met à jour votre fichier `~/.ssh/config`. L'empreinte de la clé est affichée après sa création pour vérification.

**Syntaxe**
```bash
sshkeys create <nom_de_la_clé> [options]
```

**Options**
- `--host <nom_hôte>`: Spécifie le nom d'hôte à utiliser dans `~/.ssh/config` (ex: `github.com-work`). Si omis, il est déduit du nom de la clé ou de l'email.
- `--email <adresse_email>`: Spécifie l'email à utiliser comme commentaire pour la clé. En mode interactif, le script vous le demandera si omis.
- `--passphrase`, `-P`: Demande une phrase secrète pour la clé. Si omis, la clé sera créée sans phrase secrète.
- `--force`, `-f`: Force l'écrasement d'une clé existante sans demander confirmation. À utiliser avec prudence.

**Exemples**
```bash
# Mode interactif : le script vous guide
sshkeys create github-perso

# Mode script : pour l'automatisation
sshkeys create deploy-key --host gitlab.com --email "deploy@monprojet.com" --force
```

#### Restrictions sur les noms de clés

Lors de la création d'une clé, le `<nom_de_la_clé>` doit respecter les règles suivantes :

-   Il doit contenir uniquement des caractères alphanumériques (a-z, A-Z, 0-9), des tirets (`-`) ou des underscores (`_`).
-   Les noms `config` et `known_hosts` (insensible à la casse) sont réservés et ne peuvent pas être utilisés pour éviter les conflits avec les fichiers de configuration SSH.

### `delete`

Supprime une clé SSH, en tentant d'abord de la décharger de l'agent SSH si elle y est chargée, puis supprime ses fichiers et nettoie l'entrée correspondante dans `~/.ssh/config`.

**Syntaxe**
```bash
sshkeys delete <nom_de_la_clé>
```

### `init` & `reload`

Charge une ou plusieurs clés dans l'agent SSH. `reload` décharge d'abord toutes les clés existantes.

**Syntaxe**
```bash
sshkeys init <clé_1> [clé_2...]
sshkeys reload <clé_1> [clé_2...]
```

### `status`

Affiche les clés actuellement chargées dans l'agent SSH, avec leur empreinte et leur commentaire.

### `list`

Liste tous les fichiers de clés privées trouvées dans votre dossier `~/.ssh/`, affichant également leur empreinte.

## Configuration Personnalisée

Le comportement de `sshkeys` peut être personnalisé via un fichier de configuration. Le script recherche automatiquement ce fichier au démarrage et charge les variables qu'il contient.

- **Emplacement du fichier :** `~/.config/sshkeys.conf`

**Variables configurables :**

Vous pouvez définir les variables suivantes dans `~/.config/sshkeys.conf` pour remplacer les valeurs par défaut du script :

-   `SSH_DIR`: Répertoire de base pour les clés SSH (par défaut : `~/.ssh`).
    ```bash
    # Exemple : Stocker les clés dans un dossier différent
    SSH_DIR="$HOME/mes_cles_ssh"
    ```
-   `SSHKEYS_LOG_FILE`: Chemin complet du fichier de log (par défaut : `$(dirname "${BASH_SOURCE[0]}")/load_ssh_keys.log`).
-   `LOG_MAX_SIZE`: Taille maximale du fichier de log en octets avant rotation (par défaut : 1 Mo).
-   `LOG_ARCHIVE_DAYS`: Nombre de jours de conservation des archives de logs (par défaut : 7 jours).

**Exemple de `~/.config/sshkeys.conf` :**

```bash
# Mon fichier de configuration sshkeys
SSH_DIR="$HOME/mon_dossier_ssh"
SSHKEYS_LOG_FILE="/var/log/sshkeys/mon_log.log"
LOG_MAX_SIZE=$((2 * 1024 * 1024)) # 2 Mo
LOG_ARCHIVE_DAYS=30
```

## Notes



---
*Script par Frédéric & Copilot - Août 2025*