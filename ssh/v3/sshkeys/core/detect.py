import re
from typing import Dict, Optional, Tuple
from .models import HostConfig

def detect_host(url: str, default_user: str = "git") -> HostConfig:
    """
    Détecte le type d'hôte (GitHub/serveur) et extrait les métadonnées.
    Exemples :
      - "git@github.com:user/repo.git" → GitHub
      - "user@mon-serveur.com:2222" → Serveur
      - "git@git-python-env:user/repo.git" → GitHub avec alias
    """
    # Cas 1: URL GitHub (standard ou avec alias)
    github_pattern = r"^(?:(git|ssh)@)?(?:([a-zA-Z0-9-]+)@)?([a-zA-Z0-9.-]+)(?::|/)(.+/.+?\.git)?$"
    match = re.match(github_pattern, url)
    if match:
        user, alias, real_host, _ = match.groups()
        if alias and "@" not in url:  # Cas "git@git-python-env:..."
            return HostConfig(
                host_type="github",
                alias=alias,
                real_host="github.com",  # Alias → GitHub
                user=user or default_user,
                key_path=f"~/.ssh/{alias}"
            )
        return HostConfig(  # Cas standard GitHub
            host_type="github",
            alias=real_host,
            real_host=real_host,
            user=user or default_user,
            key_path=f"~/.ssh/{real_host}"
        )

    # Cas 2: Serveur SSH (ex: user@host:port)
    server_pattern = r"^([a-zA-Z0-9-]+)@([a-zA-Z0-9.-]+)(?::(\d+))?$"
    match = re.match(server_pattern, url)
    if match:
        user, host, port = match.groups()
        return HostConfig(
            host_type="server",
            alias=host,
            real_host=host,
            user=user,
            port=int(port) if port else 22,
            key_path=f"~/.ssh/{host}"
        )

    raise ValueError(f"URL non reconnue : {url}")

def get_hosts_from_github_ssh_url(url: str) -> HostConfig:
    """Extrait l'hôte et l'utilisateur d'une URL SSH GitHub."""
    # Exemple: git@github.com:user/repo.git ou git@github.com-user-repo
    pattern = r"^(?:([^@]+)@)?([^:]+)(?::|\/)([^/]+)/([^.]+)\.git$"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"URL SSH GitHub invalide: {url}")

    user, host, _, _ = match.groups()
    return HostConfig(
        real_host=host,
        user=user or "git",  # Par défaut, GitHub utilise 'git'
        host_type="github"
    )
