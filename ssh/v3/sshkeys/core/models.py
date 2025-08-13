from pydantic import BaseModel
from typing import Optional, Literal
from pathlib import Path

class HostConfig(BaseModel):
    """Modèle pour la configuration d'un hôte SSH."""
    host_type: Literal["github", "server", "gitlab"]  # À étendre
    alias: Optional[str] = None                  # Nom dans ~/.ssh/config (ex: "git-python-env")
    real_host: Optional[str] = None              # Hôte réel (ex: "github.com")
    user: Optional[str] = None                   # Utilisateur SSH (ex: "git")
    port: int = 22              # Port SSH
    key_path: Optional[str]     # Chemin vers la clé privée (ex: ~/.ssh/id_ed25519)
    identity_file: Optional[Path] = None
    key_type: str = "ed25519"   # Type de clé (ed25519, rsa, etc.)
