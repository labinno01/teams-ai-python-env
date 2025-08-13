import subprocess
from pathlib import Path
import os
import requests # Import requests
import sys # Added

from .models import HostConfig

def generate_ssh_key(host: HostConfig, overwrite: bool = False) -> Path:
    """Génère une clé SSH pour un hôte."""
    key_path = Path(os.path.expanduser(host.key_path))
    if key_path.exists() and not overwrite:
        raise FileExistsError(f"Clé existante : {key_path}")

    # Génère la clé
    command = [
        "ssh-keygen", "-t", host.key_type,
        "-f", str(key_path),
        "-C", host.comment if host.comment else f"{host.user}@{host.alias}" # Use host.comment if available
    ]

    # Add -N "" if no passphrase is required
    if not host.passphrase_flag: # Use host.passphrase_flag
        command.extend(["-N", ""])

    subprocess.run(command, check=True) # THIS LINE WAS MISSING!

    # Ajoute la clé à ssh-agent
    subprocess.run(["ssh-add", str(key_path)], check=True)
    return key_path

def test_ssh_connection(host: HostConfig) -> bool:
    """Teste la connexion SSH à un hôte."""
    try:
        subprocess.run([
            "ssh", "-T",
            f"{host.user}@{host.alias}",
            "-p", str(host.port),
            "-i", os.path.expanduser(host.key_path)
        ], check=True, timeout=10)
        return True
    except subprocess.CalledProcessError:
        return False

def add_key_to_host(host: HostConfig) -> None:
    """Ajoute la clé SSH à l'hôte distant."""
    if host.host_type == "github":
        # Read public key content
        public_key_path = Path(os.path.expanduser(host.key_path + ".pub"))
        if not public_key_path.exists():
            raise FileNotFoundError(f"Clé publique non trouvée : {public_key_path}")

        with open(public_key_path, "r") as f:
            public_key_content = f.read().strip()

        # GitHub API endpoint
        github_api_url = "https://api.github.com/user/keys"
        headers = {
            "Authorization": f"token {os.environ.get('GITHUB_PAT')}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": f"sshkeys-agent-{host.alias}", # A descriptive title for the key
            "key": public_key_content
        }

        response = requests.post(github_api_url, headers=headers, json=data)

        if response.status_code == 201:
            print(f"Clé ajoutée avec succès à GitHub pour {host.alias}.")
        else:
            print(f"Erreur lors de l'ajout de la clé à GitHub: {response.status_code} - {response.json()}")
            response.raise_for_status() # Raise an exception for HTTP errors
    elif host.host_type == "server":
        # For generic servers, typically use ssh-copy-id or manual addition
        # This part is more complex and might require user interaction or specific credentials
        print(f"L'ajout de clé pour les serveurs génériques n'est pas encore implémenté pour {host.alias}.")
        print("Veuillez utiliser ssh-copy-id ou ajouter manuellement la clé publique à ~/.ssh/authorized_keys sur le serveur.")
    else:
        raise ValueError(f"Type d'hôte non supporté pour l'ajout de clé: {host.host_type}")

def unload_key_from_agent(key_path: Path) -> bool:
    """Tente de décharger une clé SSH spécifique de l'agent SSH."""
    try:
        # ssh-add -d <key_path>
        subprocess.run(["ssh-add", "-d", str(key_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        # If key is not loaded, ssh-add -d will return non-zero exit code.
        # We can check stderr for specific messages if needed.
        print(f"Erreur lors du déchargement de la clé {key_path}: {e}", file=sys.stderr) # Need to import sys
        return False
    except FileNotFoundError:
        print("ssh-add non trouvé. Assurez-vous que ssh-agent est installé et dans votre PATH.", file=sys.stderr)
        return False

def load_key_to_agent(key_path: Path) -> bool:
    """Tente de charger une clé SSH spécifique dans l'agent SSH."""
    try:
        # ssh-add <key_path>
        subprocess.run(["ssh-add", str(key_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du chargement de la clé {key_path}: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ssh-add non trouvé. Assurez-vous que ssh-agent est installé et dans votre PATH.", file=sys.stderr)
        return False

def unload_all_keys_from_agent() -> bool:
    """Décharge toutes les clés de l'agent SSH."""
    try:
        # ssh-add -D (delete all)
        subprocess.run(["ssh-add", "-D"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du déchargement de toutes les clés: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ssh-add non trouvé. Assurez-vous que ssh-agent est installé et dans votre PATH.", file=sys.stderr)
        return False

def get_agent_status() -> str:
    """Récupère le statut de l'agent SSH (clés chargées)."""
    try:
        result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if "The agent has no identities." in e.stderr: # Specific error for no identities
            return "Agent SSH démarré, mais aucune clé chargée."
        else:
            return f"Erreur lors de la récupération du statut de l'agent: {e.stderr.strip()}"
    except FileNotFoundError:
        return "ssh-add non trouvé. Assurez-vous que ssh-agent est installé et dans votre PATH."
