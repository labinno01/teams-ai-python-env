**Cahier des Charges : Commande `sshkeys create`**

**Objectif :** Implémenter la commande `create` pour générer une nouvelle clé SSH, l'ajouter à l'agent, et optionnellement la configurer dans `~/.ssh/config`.

**1. Nom de la Commande :**
   `create` (sera une sous-commande du groupe principal `cli`)

**2. Description CLI (pour l'aide `sshkeys create --help`) :**
   ```
   Crée une nouvelle clé SSH, la charge dans l'agent et met à jour votre fichier ~/.ssh/config.
   L'empreinte de la clé est affichée après sa création pour vérification.
   ```

**3. Syntaxe CLI :**
   `sshkeys create <nom_de_la_clé> [OPTIONS]`

**4. Arguments :**

   *   `<nom_de_la_clé>`
        *   **Type Click :** `click.Argument("key_name")`
        *   **Description :** Nom de base du fichier de la clé SSH (ex: `github-perso`). Ce nom sera utilisé pour les fichiers `~/.ssh/<nom_de_la_clé>` et `~/.ssh/<nom_de_la_clé>.pub`.
        *   **Obligatoire :** Oui.

**5. Options :**

   *   `--host <nom_hôte>`
        *   **Type Click :** `click.Option("--host", type=str, help="Spécifie le nom d'hôte à utiliser dans ~/.ssh/config (ex: github.com-work). Si omis, la clé n'est pas ajoutée à config.")`
        *   **Description :** Spécifie le nom d'hôte à utiliser dans `~/.ssh/config`.
        *   **Comportement :** Si cette option est fournie, la clé sera également ajoutée à `~/.ssh/config` en utilisant ce `nom_hôte` comme `alias` et `real_host` dans l'objet `HostConfig` passé à `add_to_ssh_config`.
        *   **Valeur par défaut :** Aucune (optionnel).

   *   `--email <adresse_email>`
        *   **Type Click :** `click.Option("--email", type=str, help="Spécifie l'email à utiliser comme commentaire pour la clé.")`
        *   **Description :** Spécifie l'email à utiliser comme commentaire pour la clé (ex: `votre@email.com`).
        *   **Comportement :** La valeur de cette option sera passée comme partie du commentaire (`-C`) à `ssh-keygen`. Si omis, le commentaire sera généré sans email spécifique.
        *   **Valeur par défaut :** Aucune (optionnel).

   *   `--passphrase`, `-P`
        *   **Type Click :** `click.Option("--passphrase", "-P", is_flag=True, help="Demande une phrase secrète pour la clé.")`
        *   **Description :** Demande une phrase secrète pour la clé.
        *   **Comportement :** Si ce flag est présent, la fonction `generate_ssh_key` doit être appelée de manière à ce que `ssh-keygen` demande interactivement la phrase secrète. Si omis, `generate_ssh_key` doit être appelée avec `-N ""` pour créer une clé sans phrase secrète.
        *   **Valeur par défaut :** `False` (flag).

   *   `--force`, `-f`
        *   **Type Click :** `click.Option("--force", "-f", is_flag=True, help="Force l'écrasement d'une clé existante sans demander confirmation.")`
        *   **Description :** Force l'écrasement d'une clé existante.
        *   **Comportement :** La valeur de ce flag sera passée comme argument `overwrite` à la fonction `generate_ssh_key`.
        *   **Valeur par défaut :** `False` (flag).

**6. Comportement / Logique Interne (Implémentation dans `sshkeys/cli.py`) :**

   *   **Décorateur Click :** `@cli.command()`
   *   **Signature de la Fonction :** `def create(key_name: str, host: Optional[str], email: Optional[str], passphrase: bool, force: bool):`
        *   Assurez-vous d'importer `Optional` depuis `typing`.
   *   **Validation du Nom de la Clé (`key_name`) :**
        *   **Règles :**
            *   Doit contenir uniquement des caractères alphanumériques (a-z, A-Z, 0-9), des tirets (`-`) ou des underscores (`_`).
            *   Ne peut pas être `config` ou `known_hosts` (insensible à la casse).
        *   **Action en cas d'erreur :** Lever une `click.BadParameter(message, param_name="key_name")` ou `click.UsageError(message)`.
   *   **Construction de l'Objet `HostConfig` pour `generate_ssh_key` :**
        *   Créez une instance de `HostConfig` (importez-la depuis `sshkeys.core.models`).
        *   `host_type`: Définir à `"server"` par défaut. (Pour ce prototype, `"server"` est suffisant. L'intégration avec `detect_host` pour les URLs GitHub/GitLab peut être une amélioration future).
        *   `alias`: `key_name`
        *   `real_host`: `host` si spécifié, sinon `key_name`.
        *   `user`: `git` (valeur par défaut simple pour le prototype).
        *   `key_path`: `Path.home() / ".ssh" / key_name`
        *   `key_type`: `ed25519` (valeur par défaut simple pour le prototype).
        *   `identity_file`: `None` (pour le prototype).
        *   `port`: `22` (par défaut).
   *   **Gestion de la Passphrase et Interactivité :**
        *   Si l'option `--passphrase` est utilisée, la fonction `generate_ssh_key` doit appeler `ssh-keygen` de manière à ce qu'il demande interactivement la phrase secrète à l'utilisateur.
        *   Si l'option `--passphrase` n'est *pas* utilisée, la fonction `generate_ssh_key` doit appeler `ssh-keygen` avec l'option `-N ""` pour créer une clé sans phrase secrète et éviter toute interaction.
        *   Pour toutes les autres options (`--host`, `--email`, `--force`), la commande `create` fonctionnera de manière non-interactive, en utilisant les valeurs fournies ou leurs valeurs par défaut. Elle ne demandera pas d'informations supplémentaires à l'utilisateur.
   *   **Appel à `generate_ssh_key` :**
        *   `generate_ssh_key(host_config_instance, overwrite=force)`
        *   Assurez-vous que `generate_ssh_key` gère correctement l'absence de `-N ""` pour la passphrase.
   *   **Ajout à `~/.ssh/config` (si `--host` est spécifié) :**
        *   Si l'option `host` est fournie :
            *   Construire un objet `HostConfig` approprié pour `add_to_ssh_config`.
            *   Appeler `add_to_ssh_config(host_config_for_config)`.
   *   **Affichage de l'Empreinte :**
        *   Après la création réussie, afficher un message de succès.
        *   Pour afficher l'empreinte, vous pouvez utiliser `subprocess.run(["ssh-keygen", "-lf", str(key_path)])` et capturer sa sortie.
   *   **Gestion des Erreurs :**
        *   Utiliser un bloc `try...except Exception as e:` pour capturer les erreurs (ex: `FileExistsError` de `generate_ssh_key`, `click.BadParameter`).
        *   Afficher les messages d'erreur clairs via `click.echo(f"❌ Erreur : {e}", err=True)`.

**7. Fichiers Impactés :**
   *   `sshkeys/cli.py` (ajout de la commande `create`)
   *   Potentiellement `sshkeys/core/ssh.py` (si `generate_ssh_key` doit être ajustée pour la gestion de la phrase secrète).