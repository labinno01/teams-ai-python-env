import typer
import subprocess
import os
import sys
from .utils.display import ICON_SUCCESS, ICON_ERROR, ICON_INFO, ICON_WARN, ICON_KEY

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
        raise

def check_and_start_ssh_agent():
    """
    Checks if ssh-agent is running and guides the user to start it if not.
    """
    typer.echo(f"{ICON_INFO} Étape 1: Vérification et démarrage de l'agent SSH.")

    ssh_agent_pid = os.environ.get("SSH_AGENT_PID")
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")

    agent_running = False
    if ssh_agent_pid and ssh_auth_sock:
        try:
            # Check if the process exists
            _run_command(["ps", "-p", ssh_agent_pid], check_error=True, capture_output=True)
            agent_running = True
        except subprocess.CalledProcessError:
            agent_running = False

    if not agent_running:
        typer.echo(f"{ICON_WARN} L'agent SSH ne semble pas être en cours d'exécution ou ses variables d'environnement ne sont pas chargées.")
        typer.echo(f"{ICON_INFO} Veuillez exécuter la commande suivante dans votre terminal pour démarrer l'agent et charger ses variables :")
        typer.echo("   eval \"$(ssh-agent -s)\"")
        
        agent_started_confirm = typer.prompt("Avez-vous exécuté la commande ci-dessus et l'agent SSH a-t-il démarré avec succès ? (oui/non)")
        
        if agent_started_confirm.lower() == "oui":
            typer.echo(f"{ICON_SUCCESS} Agent SSH démarré et variables chargées (confirmé par l'utilisateur).")
            # Re-check environment variables after user confirmation
            # This part is tricky as Python script's env won't change,
            # but we assume user's shell env is updated for subsequent manual commands.
        else:
            typer.echo(f"{ICON_ERROR} L'agent SSH n'a pas été démarré ou confirmé. Impossible de continuer sans un agent SSH fonctionnel.")
            typer.echo(f"{ICON_INFO} Pistes de résolution :")
            typer.echo("   - Assurez-vous que 'ssh-agent' est installé sur votre système.")
            typer.echo("   - Redémarrez votre terminal et réessayez.")
            typer.echo("   - Vérifiez les messages d'erreur lors de l'exécution de 'eval \"$(ssh-agent -s)\"' .")
            sys.exit(1)
    else:
        typer.echo(f"{ICON_SUCCESS} L'agent SSH est déjà en cours d'exécution et ses variables sont chargées.")

def add_ssh_key_to_agent():
    """
    Guides the user to add their SSH key to the agent.
    """
    typer.echo("\n" + f"{ICON_INFO} Étape 2: Ajout de votre clé SSH à l'agent.")
    typer.echo("   Nous allons essayer d'ajouter la clé par défaut ou celle que vous spécifiez.")

    default_key_path = os.path.expanduser("~/.ssh/github-teams-ai-python-env")
    ssh_key_path = typer.prompt(f"Entrez le chemin complet de votre clé privée SSH (laissez vide pour la clé par défaut {default_key_path})", default=default_key_path)

    if not os.path.exists(ssh_key_path):
        typer.echo(f"{ICON_ERROR} Le fichier de clé privée '{ssh_key_path}' n'existe pas.")
        typer.echo(f"{ICON_INFO} Veuillez vous assurer que la clé existe ou générez-en une nouvelle avec 'setup-git-ssh.sh'.")
        sys.exit(1)

    # Check if key is already added
    try:
        list_keys_result = _run_command(["ssh-add", "-l"], capture_output=True)
        key_fingerprint_result = _run_command(["ssh-keygen", "-lf", ssh_key_path], capture_output=True)
        
        # Extract fingerprint from ssh-keygen output (e.g., "2048 SHA256:XXXXX noadresse@noname.com (RSA)")
        key_fingerprint = key_fingerprint_result.stdout.split()[1] # Get the SHA256:XXXXX part

        if key_fingerprint in list_keys_result.stdout:
            typer.echo(f"{ICON_SUCCESS} La clé '{ssh_key_path}' est déjà chargée dans l'agent SSH.")
            return
    except Exception:
        # If ssh-add -l fails or keygen fails, assume key is not added or agent is not ready
        pass

    typer.echo(f"{ICON_INFO} Ajout de la clé '{ssh_key_path}' à l'agent SSH...")
    try:
        _run_command(["ssh-add", ssh_key_path])
        typer.echo(f"{ICON_SUCCESS} Clé ajoutée à l'agent SSH.")
    except subprocess.CalledProcessError:
        typer.echo(f"{ICON_ERROR} Échec de l'ajout de la clé à l'agent SSH. Vérifiez votre mot de passe ou les permissions de la clé.")
        sys.exit(1)

def verify_github_public_key():
    """
    Guides the user to verify their public key on GitHub.
    """
    typer.echo("\n" + f"{ICON_INFO} Étape 3: Vérification de votre clé publique sur GitHub.")
    typer.echo("   Ceci est une étape MANUELLE. Vous devez vous assurer que la clé publique")
    typer.echo("   correspondante à votre clé privée est bien ajoutée à votre compte GitHub.")
    
    default_key_path = os.path.expanduser("~/.ssh/github-teams-ai-python-env")
    public_key_path = default_key_path + ".pub"
    
    typer.echo(f"   Votre clé publique est généralement située à '{public_key_path}'.")
    typer.echo("\n   Pour vérifier :")
    typer.echo("   1. Copiez le contenu de votre clé publique :")
    typer.echo(f"      cat '{public_key_path}'")
    typer.echo("   2. Allez sur GitHub.com -> Settings -> SSH and GPG keys.")
    typer.echo("   3. Assurez-vous que la clé copiée est présente dans la liste.")
    
    confirm_github_key = typer.prompt("Avez-vous vérifié que votre clé publique est sur GitHub ? (oui/non)")
    if confirm_github_key.lower() != "oui":
        typer.echo(f"{ICON_WARN} Veuillez ajouter votre clé publique à GitHub pour que l'authentification fonctionne.")
        sys.exit(0) # Exit gracefully if user doesn't confirm

def test_ssh_connection_to_github():
    """
    Tests the SSH connection to GitHub.
    """
    typer.echo("\n" + f"{ICON_INFO} Étape 4: Acceptation de la clé d'hôte de GitHub.")
    typer.echo("   Nous allons tenter une connexion test à GitHub pour ajouter leur clé d'hôte à vos 'known_hosts'.")
    typer.echo("   Si vous êtes invité à confirmer, tapez 'yes'.")
    
    try:
        # ssh -T git@github.com returns exit code 1 on success for non-shell access
        result = _run_command(["ssh", "-T", "git@github.com"], check_error=False, capture_output=True)
        
        if result.returncode == 1:
            typer.echo(f"{ICON_SUCCESS} Authentification SSH à GitHub réussie (code 1 est normal pour ssh -T).")
        elif result.returncode == 255:
            typer.echo(f"{ICON_ERROR} Échec de la connexion SSH à GitHub (code 255). Cela peut indiquer un problème de réseau ou de pare-feu.")
            sys.exit(1)
        else:
            typer.echo(f"{ICON_WARN} La connexion SSH à GitHub a retourné un code inattendu ({result.returncode}).")
            typer.echo(f"{ICON_INFO} Veuillez vérifier votre configuration SSH manuellement.")
            sys.exit(1)
    except Exception as e:
        typer.echo(f"{ICON_ERROR} Une erreur inattendue est survenue lors du test SSH: {e}")
        sys.exit(1)

def run_ssh_setup_workflow():
    """
    Runs the complete SSH setup workflow.
    """
    typer.echo(f"{ICON_KEY} Assistant de configuration SSH pour Git (GitHub)")
    typer.echo("-------------------------------------------------")
    
    check_and_start_ssh_agent()
    add_ssh_key_to_agent()
    verify_github_public_key()
    test_ssh_connection_to_github()
    
    typer.echo("\n" + f"{ICON_SUCCESS} Configuration SSH pour Git terminée. Vous devriez maintenant pouvoir pousser vos changements.")

if __name__ == "__main__":
    typer.run(run_ssh_setup_workflow)
