import os
from pathlib import Path
from typing import List, Dict, Optional
import re

from .models import HostConfig

SSH_CONFIG_PATH = Path.home() / ".ssh" / "config"

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
