import typer
import subprocess
import os
import sys

# Define icons (similar to _common.sh)
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"
ICON_INFO = "ℹ️"
ICON_WARN = "⚠️"
ICON_GIT = ""

def _run_command(command: list[str], check_error: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Helper to run shell commands."""
    try:
        result = subprocess.run(command, check=check_error, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        typer.echo(f"{ICON_ERROR} Command failed: {' '.join(command)}")
        if e.stdout:
            typer.echo(f"Stdout: {e.stdout}")
        if e.stderr:
            typer.echo(f"Stderr: {e.stderr}")
        sys.exit(e.returncode)

def check_git_repo():
    """
    Checks if the current directory is a Git repository.
    """
    if not os.path.isdir(".git"):
        typer.echo(f"{ICON_ERROR} Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser.")
        sys.exit(1)

def check_git_config():
    """
    Checks and sets Git user.name and user.email if not configured.
    """
    local_user = _run_command(["git", "config", "user.name"], capture_output=True, check_error=False).stdout.strip()
    local_email = _run_command(["git", "config", "user.email"], capture_output=True, check_error=False).stdout.strip()

    if not local_user or not local_email:
        typer.echo(f"{ICON_WARN} L'identité Git (nom et email) n'est pas configurée pour ce dépôt.")
        git_user = typer.prompt("Entrez votre nom d'utilisateur Git")
        git_email = typer.prompt("Entrez votre email Git")
        _run_command(["git", "config", "user.name", git_user])
        _run_command(["git", "config", "user.email", git_email])
        typer.echo(f"{ICON_SUCCESS} Identité Git configurée localement pour ce projet.")

def commit_and_push_workflow():
    """
    Handles the commit and push workflow.
    """
    typer.echo(f"{ICON_GIT} Assistant de commit et push")
    typer.echo("------------------------------------")

    check_git_repo()
    check_git_config()

    # Check for changes to commit
    status_result = _run_command(["git", "status", "--porcelain"], capture_output=True).stdout.strip()
    if not status_result:
        typer.echo(f"{ICON_SUCCESS} Aucun changement à commiter. Le dépôt est à jour.")
        sys.exit(0)

    typer.echo(f"{ICON_INFO} Statut actuel du dépôt :")
    _run_command(["git", "status"])
    
    confirm_add = typer.confirm("Voulez-vous indexer tous les changements et créer un commit ?")
    if not confirm_add:
        typer.echo(f"{ICON_INFO} Opération annulée.")
        sys.exit(0)
    
    _run_command(["git", "add", "."])
    typer.echo(f"{ICON_SUCCESS} Tous les changements ont été indexés.")

    typer.echo(f"{ICON_INFO} Rédaction du message de commit.")
    typer.echo("Astuce : utilisez un préfixe comme 'feat:', 'fix:', 'docs:', 'refactor:'...")
    commit_message = typer.prompt("Entrez le message de commit")
    if not commit_message:
        typer.echo(f"{ICON_ERROR} Le message de commit ne peut pas être vide.")
        _run_command(["git", "reset"], check_error=False) # Unstage changes
        sys.exit(1)

    typer.echo(f"{ICON_INFO} Création du commit...")
    try:
        _run_command(["git", "commit", "-m", commit_message])
        typer.echo(f"{ICON_SUCCESS} Commit créé avec le message : \"{commit_message}\"" )
    except subprocess.CalledProcessError:
        typer.echo(f"{ICON_ERROR} La création du commit a échoué.")
        _run_command(["git", "reset"], check_error=False) # Unstage changes
        sys.exit(1)

    confirm_push = typer.confirm("Voulez-vous pousser les changements maintenant ?")
    if confirm_push:
        typer.echo(f"{ICON_INFO} Poussée vers le dépôt distant...")
        try:
            # Note: SSH authentication check is handled by ssh_setup.py before this workflow
            _run_command(["git", "push"])
            typer.echo(f"{ICON_SUCCESS} Les changements ont été poussés avec succès.")
        except subprocess.CalledProcessError:
            typer.echo(f"{ICON_ERROR} La poussée a échoué. Votre branche locale n'est peut-être pas synchronisée avec la branche distante.")
            typer.echo(f"{ICON_INFO} Essayez d'utiliser la fonction 'Sync with Remote' pour synchroniser.")
            sys.exit(1)
    else:
        typer.echo(f"{ICON_INFO} Opération de push annulée.")

    typer.echo(f"{ICON_SUCCESS} Opération terminée.")

if __name__ == "__main__":
    typer.run(commit_and_push_workflow)
