import subprocess
from pathlib import Path
from typing import List, Dict, Optional

KNOWN_HOSTS_PATH = Path.home() / ".ssh" / "known_hosts"

def parse_known_hosts() -> Dict[str, List[str]]:
    """Parse ~/.ssh/known_hosts et retourne un dict {host: [fingerprints]}."""
    if not KNOWN_HOSTS_PATH.exists():
        return {}

    hosts = {}
    with open(KNOWN_HOSTS_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Format standard: [host] [key_type] [key_fingerprint]
            parts = line.split()
            if len(parts) < 3:
                continue

            host = parts[0]
            key_type = parts[1]
            fingerprint = " ".join(parts[2:])

            if host not in hosts:
                hosts[host] = []
            hosts[host].append(f"{key_type} {fingerprint}")

    return hosts

def get_host_fingerprints(host: str) -> List[str]:
    """Récupère les empreintes d'un hôte spécifique."""
    hosts = parse_known_hosts()
    return hosts.get(host, [])

def add_host_to_known(host: str, key_type: str = "ssh-rsa", fingerprint: Optional[str] = None) -> bool:
    """
    Ajoute un hôte à known_hosts.
    Si fingerprint=none, récupère la clé via ssh-keyscan.
    """
    if fingerprint is None:
        try:
            # Récupère la clé publique de l'hôte
            result = subprocess.run(
                ["ssh-keyscan", "-t", key_type, host],
                capture_output=True, text=True, check=True
            )
            fingerprint_line = result.stdout.strip().split()[1:]
            fingerprint = " ".join(fingerprint_line)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Échec de ssh-keyscan pour {host}: {e.stderr}")

    # Ajoute à known_hosts (sans doublon)
    with open(KNOWN_HOSTS_PATH, "a+") as f:
        f.seek(0)
        content = f.read()
        new_entry = f"{host} {key_type} {fingerprint}\n"

        if new_entry not in content:
            f.write(new_entry)
            return True
        return False

def remove_host_from_known(host: str) -> bool:
    """Supprime un hôte de known_hosts."""
    if not KNOWN_HOSTS_PATH.exists():
        return False

    with open(KNOWN_HOSTS_PATH, "r") as f:
        lines = [line for line in f if not line.strip().startswith(host)]

    with open(KNOWN_HOSTS_PATH, "w") as f:
        f.writelines(lines)

    return True

def verify_known_hosts_consistency() -> Dict[str, List[str]]:
    """
    Vérifie la cohérence entre known_hosts et config.
    Retourne les hôtes dans known_hosts mais pas dans config.
    """
    from .config import list_ssh_configs # Import here to avoid circular dependency
    known_hosts = set(parse_known_hosts().keys())
    config_hosts = {h.alias for h in list_ssh_configs()}
    return {"orphans": list(known_hosts - config_hosts)}

def generate_fingerprint(key: str) -> str:
    """Génère un fingerprint lisible (MD5 ou SHA256) à partir d'une clé publique."""
    # Exemple: "SHA256:2Fzu4... user@host"
    try:
        result = subprocess.run(
            ["ssh-keygen", "-lf", "-"],
            input=key.encode(),
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split()[1]
    except subprocess.CalledProcessError:
        return "INVALIDE"
