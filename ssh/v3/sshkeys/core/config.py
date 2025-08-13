import os
import shutil # Added
from pathlib import Path
from datetime import datetime # Added
from typing import List, Dict, Optional
import re

from .models import HostConfig

SSH_CONFIG_PATH = Path.home() / ".ssh" / "config"

# --- is_wsl() (from config-py.txt) ---
def is_wsl() -> bool:
    """Détecte si le script s'exécute sous WSL."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False  # Linux/macOS

# --- parse_ssh_config (from output5.txt) ---
def parse_ssh_config(config_path: Path = Path.home() / ".ssh" / "config") -> List[HostConfig]:
    """Parse ~/.ssh/config et retourne une liste d'hôtes configurés."""
    if not config_path.exists():
        return []

    hosts = []
    current_host = None

    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower().startswith("host "):
                if current_host:
                    hosts.append(current_host)
                host_names = line[5:].split()
                current_host = HostConfig(alias=host_names[0], host_type="server")
            elif line.lower().startswith("hostname "):
                if current_host:
                    current_host.real_host = line[9:].strip()
            elif line.lower().startswith("user "):
                if current_host:
                    current_host.user = line[5:].strip()
            elif line.lower().startswith("port "):
                if current_host:
                    current_host.port = int(line[5:].strip())
            elif line.lower().startswith("identityfile "):
                if current_host:
                    current_host.identity_file = Path(line[14:].strip()).expanduser()

        if current_host:
            hosts.append(current_host)

    return hosts

# --- generate_ssh_config (from output2.txt) ---
def generate_ssh_config(host: HostConfig) -> str:
    """Génère une entrée pour ~/.ssh/config."""
    config = [
        f"Host {host.alias}",
        f"    HostName {host.real_host}",
        f"    User {host.user}",
        f"    Port {host.port}",
        f"    IdentityFile {os.path.expanduser(host.key_path)}",
        "    IdentitiesOnly yes",
        "    StrictHostKeyChecking accept-new"
    ]
    return "\n".join(config)

# --- add_to_ssh_config (from output2.txt) ---
def add_to_ssh_config(host: HostConfig) -> None:
    """Ajoute une configuration à ~/.ssh/config."""
    config_entry = generate_ssh_config(host)
    if not SSH_CONFIG_PATH.exists():
        SSH_CONFIG_PATH.parent.mkdir(exist_ok=True)
        SSH_CONFIG_PATH.touch()

    # Évite les doublons
    with open(SSH_CONFIG_PATH, "r+") as f:
        content = f.read()
        if f"Host {host.alias}" not in content:
            f.write(f"\n{config_entry}\n")

# --- list_ssh_configs (from output2.txt) ---
def list_ssh_configs() -> List[HostConfig]:
    """Liste les hôtes configurés dans ~/.ssh/config."""
    if not SSH_CONFIG_PATH.exists():
        return []
    with open(SSH_CONFIG_PATH, "r") as f:
        blocks = f.read().split("\nHost ")
    hosts = []
    for block in blocks[1:]:
        lines = block.split("\n")
        host_name = lines[0].strip()
        config = {line.split()[0]: line.split()[1] for line in lines[1:] if line.strip()}
        hosts.append(HostConfig(
            alias=host_name,
            real_host=config.get("HostName", host_name),
            user=config.get("User", "git"),
            port=int(config.get("Port", 22)),
            key_path=config.get("IdentityFile", f"~/.ssh/{host_name}")
        ))
    return hosts

# --- backup_ssh_config (from config-py.txt) ---
DEFAULT_SSH_CONFIG_PATH = Path.home() / ".ssh" / "config"
BACKUP_DIR = Path.home() / ".ssh" / "backups"

def backup_ssh_config(
    config_path: Optional[Path] = None,
    backup_dir: Optional[Path] = None,
) -> Path:
    """
    Sauvegarde le fichier SSH config (WSL/Linux/macOS uniquement).

    Args:
        config_path: Chemin vers le fichier config. Par défaut: ~/.ssh/config.
        backup_dir: Dossier de destination. Par défaut: ~/.ssh/backups/.

    Returns:
        Path: Chemin vers la sauvegarde.

    Raises:
        RuntimeError: Si exécuté sous Windows natif ou Git Bash.
        FileNotFoundError: Si le fichier config n'existe pas.
        PermissionError: Si les permissions sont insuffisantes.
    """
    # 1. Vérification de l'environnement (refus Windows natif et Git Bash)
    if os.name == "nt":
        raise RuntimeError(
            "Ce script ne supporte que WSL, Linux ou macOS. "
            "Solutions pour Windows :\n"
            "  - Utilisez WSL (recommandé)\n"
            "  - Sauvegardez manuellement C:\\Users\\<vous>\\.ssh\\config\n"
            "  - Utilisez PuTTY/Pageant pour gérer vos clés SSH."
        )

    # 2. Résolution des chemins
    config_path = config_path or DEFAULT_SSH_CONFIG_PATH
    backup_dir = backup_dir or BACKUP_DIR

    # 3. Vérifications préalables
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier config introuvable : {config_path}")
    if not config_path.is_file():
        raise ValueError(f"Le chemin spécifié n'est pas un fichier : {config_path}")

    # 4. Création du dossier de backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 5. Génération du nom de backup (timestamp)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"config_backup_{timestamp}"

    # 6. Copie du fichier
    shutil.copy2(config_path, backup_path)

    # 7. Application des permissions (sauf sous WSL où chmod est ignoré)
    if not is_wsl():  # Linux/macOS uniquement
        backup_path.chmod(0o600)

    return backup_path