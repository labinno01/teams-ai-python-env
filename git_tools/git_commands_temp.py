import typer
import subprocess
import os
import json

from .utils.display import ICON_SUCCESS, ICON_ERROR, ICON_INFO, ICON_WARN, ICON_GIT
from . import config
from .utils.logger import log_workflow

def _get_ssh_env(agent_id: str | None) -> dict | None:
    """Creates the environment dictionary for SSH authentication if an agent_id is provided."""
    if not agent_id:
        return None
    agent_conf = config.get_agent_config(agent_id)
    key_path = agent_conf["ssh_key_path"]
    if not os.path.exists(key_path):
        typer.echo(f"{ICON_ERROR} La clé SSH pour l'agent {agent_id} est introuvable à l'emplacement : {key_path}")
        raise typer.Exit(code=1)
    
    env = os.environ.copy()
    env["GIT_SSH_COMMAND"] = f"ssh -i {key_path} -o StrictHostKeyChecking=no"
    return env

def _set_git_config(agent_id: str):
    """Sets local git user.name and user.email for the agent."""
    agent_conf = config.get_agent_config(agent_id)
    _run_command(["git", "config", "user.name", f'"{agent_conf["name"]}"'])
    _run_command(["git", "config", "user.email", agent_conf["email"]])
    typer.echo(f"{ICON_INFO} Identité Git configurée pour l'agent : {agent_conf['name']}")

def _unset_git_config():
    """Removes local git user.name and user.email."""
    _run_command(["git", "config", "--unset-all", "user.name"], check_error=False)
    _run_command(["git", "config", "--unset-all", "user.email"], check_error=False)
    typer.echo(f"{ICON_INFO} Configuration de l'identité Git de l'agent nettoyée.")

def _run_command(command: list[str], check_error: bool = True, capture_output: bool = False, env: dict | None = None) -> tuple[str | None, str | None]:
    """Helper to run shell commands."""
    print(f"DEBUG: Running command: {' '.join(command)}") # Added debug print
    try:
        result = subprocess.run(command, check=check_error, capture_output=True, text=True, env=env)
        print(f"DEBUG: Command {' '.join(command)} completed. Exit code: {result.returncode}") # Added debug print
        if capture_output:
            return result.stdout, result.stderr
        else:
            return None, None
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Command {' '.join(command)} failed. Return code: {e.returncode}") # Added debug print
        print(f"DEBUG: Stderr: {e.stderr}") # Added debug print
        print(f"DEBUG: Stdout: {e.stdout}") # Added debug print
        typer.echo(f"{ICON_ERROR} Command failed: {' '.join(command)}") # Keep original typer.echo
        if e.stdout:
            typer.echo(f"Stdout: {e.stdout}")
        if e.stderr:
            typer.echo(f"Stderr: {e.stderr}\n")
        raise typer.Exit(e.returncode)

def check_git_repo():
    """
    Checks if the current directory is a Git repository.
    """
    if not os.path.isdir(".git"):
        typer.echo(f"{ICON_ERROR} Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser.")
        raise typer.Exit(1)

# Helper functions for release workflow (get_next_version, get_tag_message)
def get_next_version(current_version: str) -> tuple[str, str] | None:
    base_version = current_version.split('-')[0]
    major, minor, patch = map(int, base_version.split('.'))
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
    stdout, _ = _run_command(["git", "describe", "--tags", "--abbrev=0"], check_error=False, capture_output=True)
    last_tag = stdout.strip() if stdout else ""
    stdout, _ = _run_command(["git", "rev-parse", "--verify", "HEAD"], check_error=False, capture_output=True)
    if stdout: # Check if stdout is not empty, indicating a successful rev-parse
        return f"Version {next_version}\n\nInitial release - No previous commits."

    if version_type == "PATCH":
        typer.echo(f"{ICON_INFO} Génération automatique du message pour le PATCH...")
        if last_tag:
            stdout, _ = _run_command(["git", "log", "--oneline", f"{last_tag}..HEAD"], capture_output=True)
        else:
            stdout, _ = _run_command(["git", "log", "--oneline"], capture_output=True)
        log_messages = stdout.strip()
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
    return ""

@log_workflow
def commit_and_push_workflow(non_interactive: bool, commit_message: str | None):
    agent_id = os.environ.get("GIT_CLI_AGENT_ID") # Read from env
    check_git_repo()
    ssh_env = _get_ssh_env(agent_id)

    if non_interactive:
        if not commit_message:
            typer.echo(f"{ICON_ERROR} Erreur : Le message de commit est obligatoire en mode non interactif (--message).")
            raise typer.Exit(code=1)
        
        _set_git_config(agent_id)
        try:
            typer.echo(f"{ICON_INFO} Mode non interactif activé.")
            # Debugging: Print git status output directly
            debug_stdout, debug_stderr = _run_command(["git", "status"], capture_output=True)
            print(f"DEBUG GIT STATUS STDOUT: {debug_stdout}")
            print(f"DEBUG GIT STATUS STDERR: {debug_stderr}")

            _run_command(["git", "add", "."])
            _run_command(["git", "commit", "-m", commit_message])
            typer.echo(f"{ICON_INFO} Poussée vers le dépôt distant...")
            _run_command(["git", "push"], env=ssh_env)
            typer.echo(f"{ICON_SUCCESS} Opération non interactive terminée avec succès.")
        finally:
            _unset_git_config()
    else:
        # Interactive mode
        typer.echo(f"{ICON_GIT} Assistant de commit et push")
        typer.echo("------------------------------------")
        
        # Check git config for interactive user
        stdout, _ = _run_command(["git", "config", "user.name"], capture_output=True, check_error=False)
        local_user = stdout.strip()
        if not local_user:
            git_user = typer.prompt("Entrez votre nom d'utilisateur Git")
            _run_command(["git", "config", "user.name", git_user])
        stdout, _ = _run_command(["git", "config", "user.email"], capture_output=True, check_error=False)
        local_email = stdout.strip()
        if not local_email:
            git_email = typer.prompt("Entrez votre email Git")
            _run_command(["git", "config", "user.email", git_email])

        stdout, _ = _run_command(["git", "status", "--porcelain"], capture_output=True)
        status_result = stdout.strip()
        if not status_result:
            typer.echo(f"{ICON_SUCCESS} Aucun changement à commiter. Le dépôt est à jour.")
            return

        typer.echo(f"{ICON_INFO} Statut actuel du dépôt :")
        _run_command(["git", "status"])
        
        # Get current branch name
        stdout, _ = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
        current_branch = stdout.strip()

        if current_branch in ["main", "master"]:
            typer.echo(f"{ICON_WARN} Vous êtes sur la branche '{current_branch}'. Il est recommandé de travailler sur une branche de fonctionnalité.")
            if not typer.confirm("Voulez-vous vraiment commiter directement sur cette branche ?"):
                typer.echo(f"{ICON_INFO} Opération annulée. Veuillez créer une nouvelle branche pour vos modifications.")
                return

        if typer.confirm("Voulez-vous indexer tous les changements et créer un commit ?"):
            _run_command(["git", "add", "."])
            typer.echo(f"{ICON_SUCCESS} Tous les changements ont été indexés.")
            
            typer.echo("Astuce : utilisez un préfixe comme 'feat:', 'fix:', 'docs:', 'refactor:'...")
            msg = typer.prompt("Entrez le message de commit")
            if not msg:
                typer.echo(f"{ICON_ERROR} Le message de commit ne peut pas être vide.")
                _run_command(["git", "reset"], check_error=False)
                raise typer.Exit(1)
            
            _run_command(["git", "commit", "-m", msg])
            typer.echo(f"{ICON_SUCCESS} Commit créé.")

            if typer.confirm("Voulez-vous pousser les changements maintenant ?"):
                typer.echo(f"{ICON_INFO} Poussée vers le dépôt distant...")
                _run_command(["git", "push"], env=ssh_env)
                typer.echo(f"{ICON_SUCCESS} Les changements ont été poussés.")
            else:
                typer.echo(f"{ICON_INFO} Opération de push annulée.")
        else:
            typer.echo(f"{ICON_INFO} Opération annulée.")

@log_workflow
def release_workflow(non_interactive: bool, version_type: str | None = None):
    agent_id = os.environ.get("GIT_CLI_AGENT_ID") # Read from env
    check_git_repo()
    ssh_env = _get_ssh_env(agent_id)

    if non_interactive:
        if not version_type:
            typer.echo(f"{ICON_ERROR} Erreur : Le type de version (--type) est obligatoire en mode non interactif.")
            raise typer.Exit(code=1)
        if version_type not in ["major", "minor", "patch"]:
            typer.echo(f"{ICON_ERROR} Erreur : Le type de version doit être 'major', 'minor' ou 'patch'.")
            raise typer.Exit(code=1)

        _set_git_config(agent_id)
        try:
            typer.echo(f"{ICON_INFO} Mode non interactif activé pour la release.")

            stdout, _ = _run_command(["git", "status", "--porcelain"], capture_output=True)
            status_result = stdout.strip()
            if status_result:
                typer.echo(f"{ICON_ERROR} Votre répertoire de travail n'est pas propre. Veuillez commiter ou ranger vos changements.")
                _run_command(["git", "status"])
                raise typer.Exit(1)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            version_file_path = os.path.join(script_dir, "version.json")
            
            if not os.path.exists(version_file_path):
                typer.echo(f"{ICON_ERROR} Fichier de version non trouvé: {version_file_path}")
                raise typer.Exit(1)

            with open(version_file_path, 'r') as f:
                version_data = json.load(f)
            current_version = version_data.get("version", "0.0.0")

            base_version = current_version.split('-')[0]
            major, minor, patch = map(int, base_version.split('.'))
            
            next_version = ""
            if version_type == "patch":
                next_version = f"{major}.{minor}.{patch + 1}"
            elif version_type == "minor":
                next_version = f"{major}.{minor + 1}.0"
            elif version_type == "major":
                next_version = f"{major + 1}.0.0"

            tag_message = f"Release v{next_version}"

            typer.echo(f"{ICON_INFO} Préparation de la release {next_version} ({version_type})...")

            version_data["version"] = next_version
            with open(version_file_path, 'w') as f:
                json.dump(version_data, f, indent=4)

            _run_command(["git", "add", version_file_path])
            _run_command(["git", "commit", "-m", f"chore(release): Bump version to {next_version}"])
            _run_command(["git", "tag", "-a", f"v{next_version}", "-m", tag_message])

            _run_command(["git", "push"], env=ssh_env)
            _run_command(["git", "push", "--tags"], env=ssh_env)

            typer.echo(f"{ICON_SUCCESS} Release v{next_version} créée et poussée avec succès (mode non interactif)!")
        finally:
            _unset_git_config()
    else:
        typer.echo(f"{ICON_GIT} Assistant de création de Release")
        typer.echo("-----------------------------------------")

        check_git_repo()

        stdout, _ = _run_command(["git", "status", "--porcelain"], capture_output=True)
        status_result = stdout.strip()
        if status_result:
            typer.echo(f"{ICON_ERROR} Votre répertoire de travail n'est pas propre. Veuillez commiter ou ranger vos changements.")
            _run_command(["git", "status"])
            raise typer.Exit(1)
        typer.echo(f"{ICON_SUCCESS} Le répertoire de travail est propre.")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        version_file_path = os.path.join(script_dir, "version.json")
        
        if not os.path.exists(version_file_path):
            typer.echo(f"{ICON_ERROR} Fichier de version non trouvé: {version_file_path}")
            raise typer.Exit(1)

        with open(version_file_path, 'r') as f:
            version_data = json.load(f)
        current_version = version_data.get("version", "0.0.0")

        version_info = get_next_version(current_version)
        if version_info is None:
            typer.echo(f"{ICON_ERROR} Détermination de la prochaine version annulée ou échouée.")
            raise typer.Exit(1)
        
        next_version, version_type = version_info
        typer.echo(f"{ICON_INFO} La nouvelle version sera : {next_version}")

        tag_message = get_tag_message(version_type, next_version)

        typer.echo(f'''
{ICON_WARN} --- Résumé de la Release ---
''')
        typer.echo(f'''
  Nouvelle version : {next_version}
  Message du tag   :
{tag_message}
''')
        typer.echo("---------------------------")

        if not typer.confirm("Confirmez-vous la création de cette release ?"):
            typer.echo(f"{ICON_INFO} Opération annulée.")
            raise typer.Exit(0)

        version_data["version"] = next_version
        with open(version_file_path, 'w') as f:
            json.dump(version_data, f, indent=4)

        _run_command(["git", "add", version_file_path])
        _run_command(["git", "commit", "-m", f"chore(release): Bump version to {next_version}"])
        _run_command(["git", "tag", "-a", f"v{next_version}", "-m", tag_message])

        _run_command(["git", "push"], env=ssh_env)
        _run_command(["git", "push", "--tags"], env=ssh_env)

        typer.echo(f'''
{ICON_SUCCESS} Release v{next_version} créée et poussée avec succès !''')

@log_workflow
def sync_workflow(non_interactive: bool, target_directory: str | None = None):
    original_directory = os.getcwd() # Store original directory
    if target_directory:
        try:
            os.chdir(target_directory)
            typer.echo(f"DEBUG: Changed directory to: {os.getcwd()}")
        except OSError as e:
            typer.echo(f"{ICON_ERROR} Erreur: Impossible de changer de répertoire vers {target_directory}. {e}")
            raise typer.Exit(1)

    try: # Wrap existing code in try...finally
        agent_id = os.environ.get("GIT_CLI_AGENT_ID") # Read from env
        check_git_repo()
        ssh_env = _get_ssh_env(agent_id)
        remote_name = "origin"

    if non_interactive:
        typer.echo(f"{ICON_INFO} Mode non interactif activé pour la synchronisation.\n")
        _set_git_config(agent_id)
        try:
            _run_command(["git", "fetch", remote_name], env=ssh_env)
            
            stdout, _ = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
            current_branch = stdout.strip()

            stdout, _ = _run_command(["git", "rev-parse", f"{remote_name}/{current_branch}"], capture_output=True, check_error=False)
            remote_hash = stdout.strip()
            if not remote_hash:
                typer.echo(f"{ICON_WARN} La branche distante '{remote_name}/{current_branch}' n'existe pas. Impossible de synchroniser.\n")
                raise typer.Exit(0)

            stdout, _ = _run_command(["git", "rev-parse", "HEAD"], capture_output=True)
            local_hash = stdout.strip()
            
            if local_hash == remote_hash:
                typer.echo(f"{ICON_SUCCESS} Votre branche locale '{current_branch}' est déjà à jour avec '{remote_name}/{current_branch}'.\n")
                return
            
            typer.echo(f"{ICON_INFO} Intégration des changements depuis {remote_name}/{current_branch}...\n")
            _run_command(["git", "pull", "--ff-only"], env=ssh_env)
            typer.echo(f"{ICON_SUCCESS} Synchronisation non interactive terminée avec succès.\n")

        except subprocess.CalledProcessError as e:
            typer.echo(f"{ICON_ERROR} La synchronisation non interactive a échoué. Des conflits ou une divergence nécessitent une intervention manuelle.\n")
            typer.echo(f"Erreur: {e.stderr}\n")
            raise typer.Exit(1)
        finally:
            _unset_git_config()
    else:
        typer.echo(f"{ICON_GIT} Assistant de synchronisation avec le distant\n")
        typer.echo("-----------------------------------------------------\n")

        check_git_repo()
        ssh_env = _get_ssh_env(agent_id)
        remote_name = "origin"

        stdout, _ = _run_command(["git", "remote", "get-url", remote_name], capture_output=True, check_error=False)
        if not stdout: # Corrected condition
            typer.echo(f"{ICON_WARN} Le remote '{remote_name}' n'est pas configuré. Impossible de synchroniser.\n")
            raise typer.Exit(0)

        stdout, _ = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
        current_branch = stdout.strip()

        typer.echo(f"{ICON_INFO} Récupération des dernières informations du dépôt distant ({remote_name})...\n")
        _run_command(["git", "fetch", remote_name], env=ssh_env)

        stdout, _ = _run_command(["git", "rev-parse", "HEAD"], capture_output=True)
        local_hash = stdout.strip()
        stdout, _ = _run_command(["git", "rev-parse", f"{current_branch}..{remote_name}/{current_branch}"], capture_output=True, check_error=False)
        remote_hash = stdout.strip()

        if not remote_hash:
            typer.echo(f"{ICON_WARN} La branche distante '{remote_name}/{current_branch}' n'existe pas. Impossible de comparer.\n")
            raise typer.Exit(0)

        if local_hash == remote_hash:
            typer.echo(f"{ICON_SUCCESS} Votre branche locale '{current_branch}' est déjà à jour avec '{remote_name}/{current_branch}'.\n")
            raise typer.Exit(0)

        stdout, _ = _run_command(["git", "log", f"..{remote_name}/{current_branch}", "--oneline"], capture_output=True)
        local_ahead_result = stdout.strip()
        if local_ahead_result:
            typer.echo(f"{ICON_INFO} Votre branche locale est en avance sur la branche distante. Vous devriez pousser vos changements.\n")

        stdout, _ = _run_command(["git", "log", f"{current_branch}..{remote_name}/{current_branch}", "--oneline"], capture_output=True)
        remote_behind_result = stdout.strip()
        if remote_behind_result:
            typer.echo(f"{ICON_WARN} La branche distante contient des changements qui ne sont pas dans votre branche locale.\n")
            typer.echo("Changements distants :\n")
            _run_command(["git", "log", "--oneline", "--graph", "--decorate", f"{current_branch}..{remote_name}/{current_branch}"])

            if typer.confirm("Voulez-vous intégrer (pull) ces changements maintenant ?"):
                typer.echo(f"{ICON_INFO} Intégration des changements depuis {remote_name}/{current_branch}...\n")
                try:
                    _run_command(["git", "pull", "--rebase", remote_name], env=ssh_env)
                    typer.echo(f"{ICON_SUCCESS} Votre branche a été mise à jour avec succès.\n")
                except subprocess.CalledProcessError:
                    typer.echo(f"{ICON_ERROR} Le pull en rebase a échoué. Votre branche locale a probablement des commits divergents ou des conflits.\n")
                    typer.echo(f"{ICON_INFO} Un rebase ou un merge manuel est nécessaire pour résoudre les conflits.\n")
                    raise typer.Exit(1)
            else:
                typer.echo(f"{ICON_INFO} Opération annulée.\n")
        elif not local_ahead_result: # This condition means diverged
            typer.echo(f"{ICON_INFO} Votre branche locale et la branche distante ont divergé. Un rebase ou un merge est nécessaire.\n")

        typer.echo(f"{ICON_SUCCESS} Opération de synchronisation terminée.\n")

    finally:
        if target_directory:
            os.chdir(original_directory) # Change back to original directory
            typer.echo(f"DEBUG: Changed back to original directory: {os.getcwd()}")

