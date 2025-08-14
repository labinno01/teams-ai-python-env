import click
from pathlib import Path
import os
import subprocess

from sshkeys.core.config import (
    parse_ssh_config,
    generate_ssh_config,
    add_to_ssh_config,
    list_ssh_configs,
    backup_ssh_config,
    remove_from_ssh_config,
    SSH_CONFIG_PATH
)
from sshkeys.core.known_hosts import verify_known_hosts_consistency
from sshkeys.core.models import HostConfig

@click.group()
def cli():
    """Outil de gestion des clés SSH."""
    pass

@cli.command()
@click.argument('alias')
@click.option('--real-host', default=None, help='Nom d\'hôte réel (ex: github.com).')
@click.option('--user', default='git', help='Utilisateur SSH (ex: git).')
@click.option('--port', type=int, default=22, help='Port SSH.')
@click.option('--key-path', default=None, help='Chemin vers la clé privée (ex: ~/.ssh/id_ed25519).')
@click.option('--key-type', default='ed25519', help='Type de clé (ed25519, rsa, etc.).')
@click.option('--comment', default=None, help='Commentaire pour la clé SSH.')
@click.option('--passphrase', is_flag=True, help='Indique si une passphrase est requise.')
@click.option('--host-type', type=click.Choice(['github', 'server', 'gitlab']), default='server', help='Type d\'hôte.')
def add(alias, real_host, user, port, key_path, key_type, comment, passphrase, host_type):
    """Ajoute une nouvelle configuration d\'hôte SSH."""
    if not key_path:
        key_path = f"~/.ssh/id_{alias}"

    host_config = HostConfig(
        host_type=host_type,
        alias=alias,
        real_host=real_host if real_host else alias,
        user=user,
        port=port,
        key_path=key_path,
        key_type=key_type,
        comment=comment,
        passphrase_flag=passphrase
    )
    add_to_ssh_config(host_config)
    click.echo(f"Hôte '{alias}' ajouté à {SSH_CONFIG_PATH}.")

@cli.command()
def list():
    """Liste les hôtes SSH configurés."""
    hosts = list_ssh_configs()
    if not hosts:
        click.echo("Aucun hôte SSH configuré trouvé.")
        return

    for host in hosts:
        click.echo(f"Alias: {host.alias}")
        click.echo(f"  Type: {host.host_type}")
        click.echo(f"  HostName: {host.real_host}")
        click.echo(f"  User: {host.user}")
        click.echo(f"  Port: {host.port}")
        if host.key_path:
            click.echo(f"  IdentityFile: {host.key_path}")
        if host.identity_file:
            click.echo(f"  IdentityFile (expanded): {host.identity_file}")
        click.echo("-" * 20)

@cli.command()
@click.argument('alias')
def remove(alias):
    """Supprime une configuration d\'hôte SSH."""
    if remove_from_ssh_config(alias):
        click.echo(f"Hôte '{alias}' supprimé de {SSH_CONFIG_PATH}.")
    else:
        click.echo(f"Hôte '{alias}' non trouvé ou impossible à supprimer.")

@cli.command()
@click.argument('alias')
@click.option('--key-path', default=None, help='Chemin vers la clé privée (ex: ~/.ssh/id_ed25519).')
@click.option('--key-type', default='ed25519', help='Type de clé (ed25519, rsa, etc.).')
@click.option('--comment', default=None, help='Commentaire pour la clé SSH.')
@click.option('--passphrase', is_flag=True, help='Indique si une passphrase est requise.')
def generate(alias, key_path, key_type, comment, passphrase):
    """Génère une nouvelle paire de clés SSH."""
    if not key_path:
        key_path = f"~/.ssh/id_{alias}"
    
    key_path_expanded = Path(os.path.expanduser(key_path))
    key_path_expanded.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["ssh-keygen", "-t", key_type, "-f", str(key_path_expanded)]
    if comment:
        cmd.extend(["-C", comment])
    if passphrase:
        click.echo("Veuillez entrer une passphrase pour votre clé SSH:")
        passphrase_val = click.prompt("", hide_input=True, confirmation_prompt=True)
        cmd.extend(["-N", passphrase_val])
    else:
        cmd.extend(["-N", ""])

    try:
        subprocess.run(cmd, check=True)
        click.echo(f"Clé SSH générée: {key_path_expanded}")
        click.echo(f"Clé publique: {key_path_expanded}.pub")
    except subprocess.CalledProcessError as e:
        click.echo(f"Erreur lors de la génération de la clé SSH: {e}")

@cli.command()
@click.argument('action', type=click.Choice(['check', 'fix']), default='check')
def known(action):
    """Vérifie ou corrige la cohérence de known_hosts."""
    if action == 'check':
        click.echo("Vérification de la cohérence de known_hosts...")
        issues = verify_known_hosts_consistency()
        if issues:
            click.echo("Incohérences trouvées:")
            for issue in issues:
                click.echo(f"- {issue}")
        else:
            click.echo("known_hosts est cohérent.")
    elif action == 'fix':
        click.echo("Fonctionnalité 'fix' non implémentée pour known_hosts.")

@cli.command()
def backup():
    """Sauvegarde le fichier ~/.ssh/config."""
    try:
        backup_path = backup_ssh_config()
        click.echo(f"Sauvegarde de {SSH_CONFIG_PATH} effectuée vers {backup_path}")
    except Exception as e:
        click.echo(f"Erreur lors de la sauvegarde: {e}")

if __name__ == '__main__':
    cli()