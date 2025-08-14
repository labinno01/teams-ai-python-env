import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import re

from .models import HostConfig

SSH_CONFIG_PATH = Path.home() / ".ssh" / "config"

# Helper to strip inline comments
def _strip_comment(val: str) -> str:
    return val.split("#")[0].strip()

# --- is_wsl() ---
def is_wsl() -> bool:
    """Détecte si le script s'exécute sous WSL."""
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

# --- parse_ssh_config ---
def parse_ssh_config(config_path: Path = Path.home() / ".ssh" / "config") -> List[HostConfig]:
    """Parse ~/.ssh/config et retourne une liste d'hôtes configurés."""
    if not config_path.exists():
        return []

    hosts = []
    current_host = None

    with open(config_path, "r") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower().startswith("host "):
                if current_host:
                    hosts.append(current_host)
                host_names = _strip_comment(line[5:]).split()
                current_host = HostConfig(alias=host_names[0], host_type="server")
            elif line.lower().startswith("hostname "):
                if current_host:
                    current_host.real_host = _strip_comment(line[9:])
            elif line.lower().startswith("user "):
                if current_host:
                    current_host.user = _strip_comment(line[5:])
            elif line.lower().startswith("port "):
                if current_host:
                    current_host.port = int(_strip_comment(line[5:]))
            elif line.lower().startswith("identityfile "):
                if current_host:
                    # Find the start of the path part after "IdentityFile "
                    path_start_index = raw_line.lower().find("identityfile ") + len("identityfile ")
                    raw_path_part = raw_line[path_start_index:].strip()
                    stripped_path = _strip_comment(raw_path_part)
                    expanded_path = os.path.expanduser(stripped_path)
                    current_host.identity_file = Path(expanded_path)

        if current_host:
            hosts.append(current_host)

    return hosts

# --- generate_ssh_config ---
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

# --- add_to_ssh_config ---
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

# --- list_ssh_configs ---
def list_ssh_configs(config_path: Path = SSH_CONFIG_PATH) -> List[HostConfig]:
    """Liste les hôtes configurés dans ~/.ssh/config."""
    if not config_path.exists():
        return []
    with open(config_path, "r") as f:
        blocks = f.read().split("\nHost ")
    hosts = []
    for block in blocks[1:]:
        lines = block.split("\n")
        host_name = lines[0].strip()
        config = {}
        for line in lines[1:]:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            parts = stripped_line.split(None, 1)
            if len(parts) == 2:
                key = parts[0]
                value = _strip_comment(parts[1])
                config[key] = value

        identity_file_str = config.get("IdentityFile", f"~/.ssh/{host_name}")
        hosts.append(HostConfig(
            host_type="server",
            alias=host_name,
            real_host=_strip_comment(config.get("HostName", host_name)),
            user=_strip_comment(config.get("User", "git")),
            port=int(_strip_comment(config.get("Port", 22))),
            key_path=identity_file_str,
            identity_file=Path(os.path.expanduser(identity_file_str))
        ))
    return hosts

# --- backup_ssh_config ---
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
    if os.name == "nt":
        raise RuntimeError(
            "Ce script ne supporte que WSL, Linux ou macOS. "
            "Solutions pour Windows :\n"
            "  - Utilisez WSL (recommandé)\n"
            "  - Sauvegardez manuellement C:\\Users\\<vous>\\.ssh\\config\n"
            "  - Utilisez PuTTY/Pageant pour gérer vos clés SSH."
        )

    config_path = config_path or DEFAULT_SSH_CONFIG_PATH
    backup_dir = backup_dir or BACKUP_DIR

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier config introuvable : {config_path}")
    if not config_path.is_file():
        raise ValueError(f"Le chemin spécifié n'est pas un fichier : {config_path}")

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"config_backup_{timestamp}"

    shutil.copy2(config_path, backup_path)

    if not is_wsl():
        backup_path.chmod(0o600)

    return backup_path

# --- remove_from_ssh_config ---
def remove_from_ssh_config(alias: str, config_path: Path = Path.home() / ".ssh" / "config") -> bool:
    """
    Remove a host block with the given alias from the SSH config file.

    Args:
        alias: The host alias to remove
        config_path: Path to the SSH config file

    Returns:
        bool: True if the host was found and removed, False otherwise
    """
    try:
        with open(config_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return False

    in_host_block = False
    host_block_start = -1
    host_block_end = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('Host ') and stripped.split()[1] == alias:
            in_host_block = True
            host_block_start = i
        elif in_host_block and stripped and not stripped.startswith(' '):
            host_block_end = i
            break

    if host_block_start == -1:
        return False

    if host_block_end == -1:
        host_block_end = len(lines)

    new_lines = lines[:host_block_start] + lines[host_block_end:]

    try:
        with open(config_path, 'w') as f:
            f.writelines(new_lines)
        return True
    except (IOError, OSError):
        return False
