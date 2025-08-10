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

def get_next_version(current_version: str) -> tuple[str, str] | None:
    major, minor, patch = map(int, current_version.split('.'))

    typer.echo(f"{ICON_INFO} Version actuelle : {current_version}")
    typer.echo("Quel type de version est-ce ?")
    typer.echo(f"  1) PATCH (correction de bug, ex: {major}.{minor}.{patch + 1})")
    typer.echo(f"  2) MINOR (ajout de fonctionnalité, ex: {major}.{minor + 1}.0)")
    typer.echo(f"  3) MAJOR (changement majeur, ex: {major + 1}.0.0)")

    version_choice = typer.prompt("Votre choix (1, 2, 3)")

    next_version = ""
    version_type = ""

    if version_choice == "1":
        next_version = f"{major}.{minor}.{patch + 1}"
        version_type = "PATCH"
    elif version_choice == "2":
        next_version = f"{major}.{minor + 1}.0"
        version_type = "MINOR"
    elif version_choice == "3":
        next_version = f"{major + 1}.0.0"
        version_type = "MAJOR"
    else:
        typer.echo(f"{ICON_ERROR} Choix invalide.")
        return None

    return next_version, version_type

def get_tag_message(version_type: str, next_version: str) -> str:
    last_tag_result = _run_command(["git", "describe", "--tags", "--abbrev=0"], check_error=False, capture_output=True)
    last_tag = last_tag_result.stdout.strip() if last_tag_result.returncode == 0 else ""

    if _run_command(["git", "rev-parse", "--verify", "HEAD"], check_error=False).returncode != 0:
        return f"Version {next_version}\n\nInitial release - No previous commits."

    if version_type == "PATCH":
        typer.echo(f"{ICON_INFO} Génération automatique du message pour le PATCH...")
        if last_tag:
            log_messages_result = _run_command(["git", "log", "--oneline", f"{last_tag}..HEAD"], capture_output=True)
        else:
            log_messages_result = _run_command(["git", "log", "--oneline"], capture_output=True)
        
        log_messages = log_messages_result.stdout.strip()
        
        if not log_messages:
            return f"Version {next_version}\n\nAucun commit depuis le dernier tag."
        else:
            return f"Version {next_version}\n\nChangements inclus dans ce patch :\n{log_messages}"
    elif version_type == "MINOR":
        typer.echo(f"{ICON_INFO} Veuillez décrire la nouvelle fonctionnalité :")
        user_message = typer.prompt(">")
        return f"feat: Version {next_version}\n\n{user_message}"
    elif version_type == "MAJOR":
        typer.echo(f"{ICON_WARN} Les versions majeures indiquent des changements non rétrocompatibles.")
        typer.echo(f"{ICON_INFO} Veuillez justifier ce changement majeur :")
        user_message = typer.prompt(">")
        return f"BREAKING CHANGE: Version {next_version}\n\n{user_message}"
    return "" # Should not happen

def release_workflow():
    """
    Handles the release (versioning and tagging) workflow.
    """
    typer.echo(f"{ICON_GIT} Assistant de création de Release")
    typer.echo("-----------------------------------------")

    check_git_repo()
    check_git_config()

    # Check if working directory is clean
    status_result = _run_command(["git", "status", "--porcelain"], capture_output=True).stdout.strip()
    if status_result:
        typer.echo(f"{ICON_ERROR} Votre répertoire de travail n'est pas propre. Veuillez commiter ou ranger vos changements.")
        _run_command(["git", "status"])
        sys.exit(1)
    typer.echo(f"{ICON_SUCCESS} Le répertoire de travail est propre.")

    # Get current version from version.json (assuming it's in the project root for Bash scripts)
    # For Python project, we'll use the version from python_scripts/version.json
    # This needs to be dynamic based on which version.json is relevant.
    # For now, let's assume we're releasing the Python project itself.
    
    # Read version from python_scripts/version.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_file_path = os.path.join(script_dir, "version.json")
    
    if not os.path.exists(version_file_path):
        typer.echo(f"{ICON_ERROR} Fichier de version non trouvé: {version_file_path}")
        sys.exit(1)

    with open(version_file_path, 'r') as f:
        version_data = json.load(f)
    current_version = version_data.get("version", "0.0.0") # Default if not found

    version_info = get_next_version(current_version)
    if version_info is None:
        typer.echo(f"{ICON_ERROR} Détermination de la prochaine version annulée ou échouée. Opération annulée.")
        sys.exit(1)
    
    next_version, version_type = version_info
    typer.echo(f"{ICON_INFO} La nouvelle version sera : {next_version}")

    tag_message = get_tag_message(version_type, next_version)

    typer.echo(f"""
{ICON_WARN} --- Résumé de la Release ---""")
    typer.echo(f"""
  Nouvelle version : {next_version}
  Message du tag   :
{tag_message}""")
    typer.echo("---------------------------")

    confirm_release = typer.confirm("Confirmez-vous la création de cette release ?")
    if not confirm_release:
        typer.echo(f"{ICON_INFO} Opération annulée.")
        sys.exit(0)

    typer.echo(f"{ICON_INFO} Mise à jour de version.json...")
    version_data["version"] = next_version
    with open(version_file_path, 'w') as f:
        json.dump(version_data, f, indent=4)

    typer.echo(f"{ICON_INFO} Création du commit pour la version...")
    _run_command(["git", "add", version_file_path])
    _run_command(["git", "commit", "-m", f"chore(release): Bump version to {next_version}"])

    typer.echo(f"{ICON_INFO} Création du tag Git annoté...")
    _run_command(["git", "tag", "-a", f"v{next_version}", "-m", tag_message])

    typer.echo(f"{ICON_INFO} Poussée du commit et du tag vers le distant...")
    # SSH authentication check is handled by ssh_setup.py before this workflow
    _run_command(["git", "push"])
    _run_command(["git", "push", "--tags"])

    typer.echo(f"""
{ICON_SUCCESS} Release v{next_version} créée et poussée avec succès !""")

if __name__ == "__main__":
    typer.run(commit_and_push_workflow)
