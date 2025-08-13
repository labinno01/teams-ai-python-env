import subprocess
from pathlib import Path
import os
import requests # Import requests

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
