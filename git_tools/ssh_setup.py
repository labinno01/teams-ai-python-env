import subprocess
import os
import sys
from .logger import Logger

def _run_command(command: list[str], logger: Logger, check_error: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Helper to run shell commands."""
    logger.debug(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check_error, capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        raise

def check_and_start_ssh_agent(logger: Logger):
    """
    Checks if ssh-agent is running and guides the user to start it if not.
    """
    logger.info("Étape 1: Vérification et démarrage de l'agent SSH.")

    ssh_agent_pid = os.environ.get("SSH_AGENT_PID")
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")

    agent_running = False
    if ssh_agent_pid and ssh_auth_sock:
        try:
            _run_command(["ps", "-p", ssh_agent_pid], logger=logger, check_error=True, capture_output=True)
            agent_running = True
        except subprocess.CalledProcessError:
            agent_running = False

    if not agent_running:
        logger.warning("L'agent SSH ne semble pas être en cours d'exécution ou ses variables d'environnement ne sont pas chargées.")
        logger.info("Veuillez exécuter la commande suivante dans votre terminal pour démarrer l'agent et charger ses variables :")
        logger.info("   eval \"$(ssh-agent -s)\"")
        
        if logger.confirm("Avez-vous exécuté la commande ci-dessus et l'agent SSH a-t-il démarré avec succès ?", default=True):
            logger.success("Agent SSH démarré et variables chargées (confirmé par l'utilisateur).")
        else:
            logger.error("L'agent SSH n'a pas été démarré ou confirmé. Impossible de continuer sans un agent SSH fonctionnel.")
            logger.info("Pistes de résolution :")
            logger.info("   - Assurez-vous que 'ssh-agent' est installé sur votre système.")
            logger.info("   - Redémarrez votre terminal et réessayez.")
            logger.info("   - Vérifiez les messages d'erreur lors de l'exécution de 'eval \"$(ssh-agent -s)\"'.")
            sys.exit(1)
    else:
        logger.success("L'agent SSH est déjà en cours d'exécution et ses variables sont chargées.")

def add_ssh_key_to_agent(logger: Logger):
    """
    Guides the user to add their SSH key to the agent.
    """
    logger.info("\nÉtape 2: Ajout de votre clé SSH à l'agent.")
    logger.info("   Nous allons essayer d'ajouter la clé par défaut ou celle que vous spécifiez.")

    default_key_path = os.path.expanduser("~/.ssh/github-teams-ai-python-env")
    ssh_key_path = logger.prompt(f"Entrez le chemin complet de votre clé privée SSH", default=default_key_path)

    if not os.path.exists(ssh_key_path):
        logger.error(f"Le fichier de clé privée '{ssh_key_path}' n'existe pas.")
        logger.info("Veuillez vous assurer que la clé existe ou générez-en une nouvelle avec 'setup-git-ssh.sh'.")
        sys.exit(1)

    try:
        list_keys_result = _run_command(["ssh-add", "-l"], logger=logger, capture_output=True)
        key_fingerprint_result = _run_command(["ssh-keygen", "-lf", ssh_key_path], logger=logger, capture_output=True)
        key_fingerprint = key_fingerprint_result.stdout.split()[1]

        if key_fingerprint in list_keys_result.stdout:
            logger.success(f"La clé '{ssh_key_path}' est déjà chargée dans l'agent SSH.")
            return
    except Exception:
        pass

    logger.info(f"Ajout de la clé '{ssh_key_path}' à l'agent SSH...")
    try:
        _run_command(["ssh-add", ssh_key_path], logger=logger)
        logger.success("Clé ajoutée à l'agent SSH.")
    except subprocess.CalledProcessError:
        logger.error("Échec de l'ajout de la clé à l'agent SSH. Vérifiez votre mot de passe ou les permissions de la clé.")
        sys.exit(1)

def verify_github_public_key(logger: Logger):
    """
    Guides the user to verify their public key on GitHub.
    """
    logger.info("\nÉtape 3: Vérification de votre clé publique sur GitHub.")
    logger.info("   Ceci est une étape MANUELLE. Vous devez vous assurer que la clé publique")
    logger.info("   correspondante à votre clé privée est bien ajoutée à votre compte GitHub.")
    
    default_key_path = os.path.expanduser("~/.ssh/github-teams-ai-python-env")
    public_key_path = default_key_path + ".pub"
    
    logger.info(f"   Votre clé publique est généralement située à '{public_key_path}'.")
    logger.info("\n   Pour vérifier :")
    logger.info("   1. Copiez le contenu de votre clé publique :")
    logger.info(f"      cat '{public_key_path}'")
    logger.info("   2. Allez sur GitHub.com -> Settings -> SSH and GPG keys.")
    logger.info("   3. Assurez-vous que la clé copiée est présente dans la liste.")
    
    if not logger.confirm("Avez-vous vérifié que votre clé publique est sur GitHub ?", default=True):
        logger.warning("Veuillez ajouter votre clé publique à GitHub pour que l'authentification fonctionne.")
        sys.exit(0)

def test_ssh_connection_to_github(logger: Logger):
    """
    Tests the SSH connection to GitHub.
    """
    logger.info("\nÉtape 4: Acceptation de la clé d'hôte de GitHub.")
    logger.info("   Nous allons tenter une connexion test à GitHub pour ajouter leur clé d'hôte à vos 'known_hosts'.")
    logger.info("   Si vous êtes invité à confirmer, tapez 'yes'.")
    
    try:
        result = _run_command(["ssh", "-T", "git@github.com"], logger=logger, check_error=False, capture_output=True)
        
        if result.returncode == 1:
            logger.success("Authentification SSH à GitHub réussie (code 1 est normal pour ssh -T).")
        elif result.returncode == 255:
            logger.error("Échec de la connexion SSH à GitHub (code 255). Cela peut indiquer un problème de réseau ou de pare-feu.")
            sys.exit(1)
        else:
            logger.warning(f"La connexion SSH à GitHub a retourné un code inattendu ({result.returncode}).")
            logger.info("Veuillez vérifier votre configuration SSH manuellement.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Une erreur inattendue est survenue lors du test SSH: {e}")
        sys.exit(1)

def run_ssh_setup_workflow(logger: Logger):
    """
    Runs the complete SSH setup workflow.
    """
    logger.info("Assistant de configuration SSH pour Git (GitHub)")
    logger.info("-------------------------------------------------")
    
    check_and_start_ssh_agent(logger)
    add_ssh_key_to_agent(logger)
    verify_github_public_key(logger)
    test_ssh_connection_to_github(logger)
    
    logger.success("\nConfiguration SSH pour Git terminée. Vous devriez maintenant pouvoir pousser vos changements.")
