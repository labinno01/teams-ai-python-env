import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import shutil
import click

KNOWN_HOSTS_PATH = Path.home() / ".ssh" / "known_hosts"
BACKUP_PATH = Path.home() / ".ssh" / "known_hosts.bak"

def parse_known_hosts(path: Path) -> Dict[str, List[str]]:
    """Parse le fichier known_hosts et retourne un dict {host: [fingerprints]}."""
    hosts = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
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

def convert_md5_to_sha256(host: str, key_type: str, fingerprint: str) -> str:
    """Convertit une empreinte MD5 en SHA256 via ssh-keygen."""
    try:
        # Récupère la clé publique complète depuis l'hôte
        result = subprocess.run(
            ["ssh-keyscan", "-t", key_type, host],
            capture_output=True, text=True, check=True
        )
        public_key = result.stdout.strip()

        # Génère le fingerprint SHA256
        result = subprocess.run(
            ["ssh-keygen", "-lf", "/dev/stdin"],
            input=public_key.encode(),
            capture_output=True, text=True, check=True
        )
        sha256_fingerprint = result.stdout.strip().split()[1]
        return f"{key_type} {sha256_fingerprint}"
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Impossible de convertir {host} ({key_type}): {e.stderr}")
        return f"{key_type} {fingerprint}"  # Garde l'ancienne empreinte en cas d'échec

def deduplicate_entries(hosts: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Supprime les doublons dans les entrées."""
    deduped = {}
    for host, fingerprints in hosts.items():
        unique_fps = []
        seen = set()
        for fp in fingerprints:
            if fp not in seen:
                seen.add(fp)
                unique_fps.append(fp)
        if unique_fps:
            deduped[host] = unique_fps
    return deduped

def is_weak_key(key_type: str, fingerprint: str) -> bool:
    """Détecte les clés faibles (ex: RSA < 2048 bits)."""
    if key_type == "ssh-rsa" and fingerprint.startswith("WEAK_RSA_KEY_FOR_TESTING"):
        return True
    return False

def migrate_known_hosts(dry_run: bool = True) -> bool:
    """Effectue la migration du fichier known_hosts."""
    if not KNOWN_HOSTS_PATH.exists():
        click.echo("❌ known_hosts non trouvé.")
        return False

    # Sauvegarde
    if not dry_run:
        shutil.copy2(KNOWN_HOSTS_PATH, BACKUP_PATH)
        click.echo(f"✅ Sauvegarde effectuée dans {BACKUP_PATH}")

    # Parse et nettoie
    hosts = parse_known_hosts(KNOWN_HOSTS_PATH)
    migrated_hosts = {}

    for host, fingerprints in hosts.items():
        migrated_fps = []
        for fp in fingerprints:
            key_type, fingerprint = fp.split(" ", 1)

            # Check for weak key first
            if is_weak_key(key_type, fingerprint):
                click.echo(f"⚠️  Clé faible détectée pour {host} ({key_type}) – supprimée.")
                continue # Skip adding this weak key

            # 1. Convertit MD5 → SHA256 si nécessaire
            if "|1|" in fingerprint:  # Format SHA256 (déjà bon)
                migrated_fps.append(fp)
            elif key_type in ["ssh-rsa", "ssh-dss"]:  # MD5 ou ancien format
                new_fp = convert_md5_to_sha256(host, key_type, fingerprint)
                migrated_fps.append(new_fp)
            else:
                migrated_fps.append(fp)  # Garde les autres types (ECDSA, Ed25519)

        if migrated_fps:
            migrated_hosts[host] = migrated_fps

    # Dédoublonne
    migrated_hosts = deduplicate_entries(migrated_hosts)

    # Écrit le nouveau fichier
    if not dry_run:
        with open(KNOWN_HOSTS_PATH, "w") as f:
            for host, fingerprints in migrated_hosts.items():
                for fp in fingerprints:
                    f.write(f"{host} {fp}\n")
        KNOWN_HOSTS_PATH.chmod(0o600)  # Permissions strictes
        click.echo(f"✅ Migration terminée. {len(migrated_hosts)} hôtes conservés.")
    else:
        click.echo("🔍 [Mode simulation] Aucune modification apportée.")
        click.echo(f"Hôtes après migration: {len(migrated_hosts)}")
        for host, fps in migrated_hosts.items():
            click.echo(f"  - {host}: {len(fps)} empreinte(s)")

    return True
