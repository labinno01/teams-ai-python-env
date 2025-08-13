import click
from .core.detect import detect_host
from .core.config import add_to_ssh_config, list_ssh_configs
from .core.ssh import generate_ssh_key, test_ssh_connection
from .core.known_hosts import (
    parse_known_hosts,
    add_host_to_known,
    remove_host_from_known,
    verify_known_hosts_consistency
)
from .core.known_hosts_migration import migrate_known_hosts

@click.group()
def cli():
    """Outil de gestion des clés SSH pour GitHub et serveurs."""
    pass

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

@cli.command()
def config_list():
    """Liste les hôtes configurés dans ~/.ssh/config."""
    hosts = list_ssh_configs()
    if not hosts:
        click.echo("Aucun hôte configuré.")
    else:
        for host in hosts:
            click.echo(f"- {host.alias} ({host.host_type}): {host.user}@{host.real_host}:{host.port}")

@cli.group()
def known():
    """Gestion des hôtes connus (~/.ssh/known_hosts)."""
    pass

@known.command()
@click.argument("host", required=False)
def list(host: str):
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