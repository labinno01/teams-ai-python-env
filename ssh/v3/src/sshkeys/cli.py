import click
from pathlib import Path
import subprocess
import re
import os
from typing import Optional, Tuple # Added Tuple

from .core.detect import detect_host
from .core.config import add_to_ssh_config, list_ssh_configs, backup_ssh_config, remove_from_ssh_config # Added remove_from_ssh_config
from .core.ssh import generate_ssh_key, test_ssh_connection, unload_key_from_agent, load_key_to_agent, unload_all_keys_from_agent, get_agent_status # Added load_key_to_agent, unload_all_keys_from_agent, get_agent_status
from .core.known_hosts import (
    parse_known_hosts,
    add_host_to_known,
    remove_host_from_known,
    verify_known_hosts_consistency
)
from .core.known_hosts_migration import migrate_known_hosts
from .core.models import HostConfig

@click.group()
@click.help_option("-h", "--help", help="Affiche ce message d'aide et quitte.")
def cli():
    """Outil de gestion des clés SSH pour GitHub et serveurs."""
    pass

@cli.command()
def status():
    """Affiche les clés actuellement chargées dans l'agent."""
    status = get_agent_status()
    click.echo(status)

@cli.command(name="list")
def list_keys():
    """Liste les fichiers de clés privées trouvées dans ~/.ssh."""
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.is_dir():
        click.echo(f"Le dossier {ssh_dir} n'existe pas.")
        return

    click.echo("Clés privées trouvées dans ~/.ssh :")
    for f in ssh_dir.iterdir():
        if f.is_file() and not f.name.endswith(".pub") and f.name not in ["known_hosts", "config"]:
            click.echo(f.name)

@cli.command()
def debug():
    """Affiche des informations de débogage sur l'agent."""
    click.echo("🔍 Debug SSH Agent")
    agent_pid = os.environ.get("SSH_AGENT_PID")
    auth_sock = os.environ.get("SSH_AUTH_SOCK")
    click.echo(f"Agent PID: {agent_pid}")
    click.echo(f"Auth Sock: {auth_sock}")
    status = get_agent_status()
    click.echo(status)
    click.echo("Contenu de ~/.ssh :")
    ssh_dir = Path.home() / ".ssh"
    for f in ssh_dir.iterdir():
        click.echo(f.name)


@cli.command()
@click.argument("url")
@click.option("--default-user", default="git", help="Utilisateur par défaut (ex: git)")
@click.option("--overwrite", is_flag=True, help="Écrase la clé existante")
def assist(url: str, default_user: str, overwrite: bool):
    """Configure automatiquement l'accès SSH à un hôte."""
    try:
        host = detect_host(url, default_user)
        click.echo(f"🔍 Hôte détecté : {host.alias} ({host.host_type})")

        # Génère la clé SSH
        key_path = generate_ssh_key(host, overwrite)
        click.echo(f"🔑 Clé générée : {key_path}")

        # Ajoute à ~/.ssh/config
        add_to_ssh_config(host)
        click.echo(f"📝 Configuration ajoutée à {host.alias}")

        # Teste la connexion
        if test_ssh_connection(host):
            click.echo("✅ Connexion SSH réussie !")
        else:
            click.echo("⚠️  Échec de la connexion. Vérifiez les permissions.")

    except Exception as e:
        click.echo(f"❌ Erreur : {e}", err=True)

# --- New create command ---
@cli.command()
@click.argument("key_name")
@click.option("--host", type=str, help="Spécifie le nom d'hôte à utiliser dans ~/.ssh/config")
@click.option("--email", type=str, help="Spécifie l'email à utiliser comme commentaire pour la clé")
@click.option("--passphrase", "-P", is_flag=True, help="Demande une phrase secrète pour la clé")
@click.option("--force", "-f", is_flag=True, help="Force l'écrasement d'une clé existante sans demander confirmation")
def create(key_name: str, host: Optional[str], email: Optional[str], passphrase: bool, force: bool):
    """Crée une nouvelle clé SSH, la charge dans l'agent et met à jour votre fichier ~/.ssh/config.
    L'empreinte de la clé est affichée après sa création pour vérification.
    """
    try:
        # Validation du nom de la clé
        if not re.match(r"^[a-zA-Z0-9_-]+$", key_name):
            raise click.BadParameter("Le nom de la clé doit contenir uniquement des caractères alphanumériques, tirets ou underscores", param_name="key_name")

        if key_name.lower() in ['config', 'known_hosts']:
            raise click.BadParameter("Le nom de la clé ne peut pas être 'config' ou 'known_hosts'", param_name="key_name")

        # Création de l'objet HostConfig pour generate_ssh_key
        host_config = HostConfig(
            host_type="server",
            alias=key_name,
            real_host=host if host else key_name,
            user="git",
            key_path=str(Path.home() / ".ssh" / key_name),
            key_type="ed25519",
            identity_file=None,
            port=22,
            comment=email, # Pass email as comment
            passphrase_flag=passphrase # Pass passphrase flag
        )

        # Génération de la clé
        key_path = generate_ssh_key(host_config, overwrite=force)
        click.echo(f"🔑 Clé générée : {key_path}")

        # Ajout à ~/.ssh/config si --host est spécifié
        if host:
            config_host = HostConfig(
                host_type="server",
                alias=host,
                real_host=host_config.real_host,
                user=host_config.user,
                key_path=host_config.key_path,
                key_type=host_config.key_type,
                identity_file=host_config.key_path,
                port=host_config.port
            )
            add_to_ssh_config(config_host)

        # Affichage de l'empreinte
        result = subprocess.run(["ssh-keygen", "-lf", str(key_path)], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ Clé créée avec succès : {key_path}")
            click.echo(f"Empreinte : {result.stdout.strip()}")
        else:
            click.echo(f"✅ Clé créée avec succès : {key_path}")
            click.echo("⚠️ Impossible d'afficher l'empreinte")

        click.echo("✅ Opération terminée avec succès")

    except Exception as e:
        click.echo(f"❌ Erreur : {e}", err=True)

# --- New delete command ---
@cli.command()
@click.argument("key_name")
def delete(key_name: str):
    """Supprime une clé SSH, en tentant d'abord de la décharger de l'agent SSH si elle y est chargée,
    puis supprime ses fichiers et nettoie l'entrée correspondante dans ~/.ssh/config.
    """
    try:
        key_path = Path.home() / ".ssh" / key_name
        public_key_path = Path.home() / ".ssh" / f"{key_name}.pub"

        # 1. Décharger de l'agent SSH
        if key_path.exists():
            click.echo(f"Attempting to unload key {key_name} from agent...")
            if unload_key_from_agent(key_path):
                click.echo(f"✅ Clé {key_name} déchargée de l'agent.")
            else:
                click.echo(f"⚠️ Impossible de décharger la clé {key_name} de l'agent (peut-être pas chargée ou agent non démarré).")
        else:
            click.echo(f"ℹ️ Clé privée {key_name} non trouvée. Skipping agent unload.")

        # 2. Supprimer les fichiers de clé
        click.echo(f"Attempting to delete key files for {key_name}...")
        deleted_files = []
        for p in [key_path, public_key_path]:
            if p.exists():
                p.unlink() # Delete the file
                deleted_files.append(p)
        if deleted_files:
            click.echo(f"✅ Fichiers de clé supprimés : {', '.join(str(f) for f in deleted_files)}")
        else:
            click.echo(f"ℹ️ Aucun fichier de clé trouvé pour {key_name}. Skipping file deletion.")

        # 3. Nettoyer ~/.ssh/config
        click.echo(f"Attempting to remove {key_name} from ~/.ssh/config...")
        if remove_from_ssh_config(key_name):
            click.echo(f"✅ Entrée {key_name} supprimée de ~/.ssh/config.")
        else:
            click.echo(f"ℹ️ Entrée {key_name} non trouvée dans ~/.ssh/config. Skipping config cleanup.")

        click.echo("✅ Opération de suppression terminée avec succès.")

    except Exception as e:
        click.echo(f"❌ Erreur lors de la suppression : {e}", err=True)

# --- New init command ---
@cli.command()
@click.argument("key_names", nargs=-1) # Accepts multiple key names
def init(key_names: Tuple[str, ...]):
    """Charge une ou plusieurs clés dans l'agent SSH."""
    if not key_names:
        click.echo("Veuillez spécifier au moins une clé à charger.", err=True)
        return

    for key_name in key_names:
        key_path = Path.home() / ".ssh" / key_name
        if key_path.exists():
            click.echo(f"Attempting to load key {key_name} to agent...")
            if load_key_to_agent(key_path):
                click.echo(f"✅ Clé {key_name} chargée dans l'agent.")
            else:
                click.echo(f"⚠️ Impossible de charger la clé {key_name} dans l'agent.")
        else:
            click.echo(f"❌ Clé privée {key_name} non trouvée : {key_path}", err=True)

    click.echo("✅ Opération de chargement terminée.")

# --- New reload command ---
@cli.command()
@click.argument("key_names", nargs=-1) # Accepts multiple key names
def reload(key_names: Tuple[str, ...]):
    """Décharge toutes les clés de l'agent SSH, puis charge une ou plusieurs clés spécifiées."""
    click.echo("Attempting to unload all keys from agent...")
    if unload_all_keys_from_agent():
        click.echo("✅ Toutes les clés déchargées de l'agent.")
    else:
        click.echo("⚠️ Impossible de décharger toutes les clés de l'agent (peut-être pas d'agent démarré).")

    if not key_names:
        click.echo("Aucune clé spécifiée pour le rechargement.")
        return

    for key_name in key_names:
        key_path = Path.home() / ".ssh" / key_name
        if key_path.exists():
            click.echo(f"Attempting to load key {key_name} to agent...")
            if load_key_to_agent(key_path):
                click.echo(f"✅ Clé {key_name} chargée dans l'agent.")
            else:
                click.echo(f"⚠️ Impossible de charger la clé {key_name} dans l'agent.")
        else:
            click.echo(f"❌ Clé privée {key_name} non trouvée : {key_path}", err=True)

    click.echo("✅ Opération de rechargement terminée.")


@cli.command()
def config_list():
    """Liste les hôtes configurés dans ~/.ssh/config."""
    hosts = list_ssh_configs()
    if not hosts:
        click.echo("Aucun hôte configuré.")
    else:
        for host in hosts:
            click.echo(f"- {host.alias} ({host.host_type}): {host.user}@{host.real_host}:{host.port}")

@cli.command()
@click.option("--config-path", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="Chemin vers le fichier config SSH à sauvegarder.")
@click.option("--backup-dir", type=click.Path(file_okay=False, path_type=Path), help="Dossier de destination pour la sauvegarde.")
def backup(config_path: Path, backup_dir: Path):
    """Sauvegarde le fichier SSH config.

    Par défaut, sauvegarde ~/.ssh/config dans ~/.ssh/backups/.
    """
    try:
        backup_path = backup_ssh_config(config_path=config_path, backup_dir=backup_dir)
        click.echo(f"✅ Sauvegarde créée : {backup_path}")
    except Exception as e:
        click.echo(f"❌ Erreur lors de la sauvegarde : {e}", err=True)

@cli.group()
def known():
    """Gestion des hôtes connus (~/.ssh/known_hosts)."""
    pass

@known.command(name="list")
@click.argument("host", required=False)
def known_list(host: str):
    """Liste les empreintes des hôtes connus."""
    hosts = parse_known_hosts()

    if host:
        fingerprints = hosts.get(host, [])
        if not fingerprints:
            click.echo(f"Aucune empreinte trouvée pour {host}.")
        else:
            click.echo(f"Empreintes pour {host}:")
            for fp in fingerprints:
                click.echo(f"  - {fp}")
    else:
        for h, fps in hosts.items():
            click.echo(f"{h}:")
            for fp in fps:
                click.echo(f"  - {fp}")

@known.command()
@click.argument("host")
@click.option("--key-type", default="ssh-rsa", help="Type de clé (ex: ecdsa-sha2-nistp256)")
@click.option("--fingerprint", help="Empreinte manuelle (sinon récupérée via ssh-keyscan)")
def add(host: str, key_type: str, fingerprint: str):
    """Ajoute un hôte à known_hosts."""
    try:
        if add_host_to_known(host, key_type, fingerprint):
            click.echo(f"✅ Hôte {host} ajouté à known_hosts.")
        else:
            click.echo(f"ℹ️  {host} déjà présent dans known_hosts.")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}", err=True)

@known.command()
@click.argument("host")
def remove(host: str):
    """Supprime un hôte de known_hosts."""
    if remove_host_from_known(host):
        click.echo(f"✅ Hôte {host} supprimé de known_hosts.")
    else:
        click.echo(f"ℹ️  {host} non trouvé dans known_hosts.")

@known.command()
def check():
    """Vérifie la cohérence entre known_hosts et config."""
    consistency = verify_known_hosts_consistency()
    if consistency["orphans"]:
        click.echo("⚠️  Hôtes dans known_hosts mais pas dans config:")
        for host in consistency["orphans"]:
            click.echo(f"  - {host}")
    else:
        click.echo("✅ Aucune incohérence détectée.")

@known.command()
@click.option("--dry-run", is_flag=True, default=True, help="Simule sans modifier.")
def migrate(dry_run: bool):
    """Migre known_hosts vers SHA256 et nettoie les entrées."""
    migrated_hosts = migrate_known_hosts(dry_run=dry_run)
    if dry_run:
        click.echo("\n--- Résultat de la simulation ---")
        if migrated_hosts:
            for host, fps in migrated_hosts.items():
                click.echo(f"  - {host}:")
                for fp in fps:
                    click.echo(f"    - {fp}")
        else:
            click.echo("Aucun hôte à migrer ou aucune modification.")
    else:
        if not migrated_hosts:
            click.echo("❌ Échec de la migration.", err=True)


if __name__ == "__main__":
    cli()
