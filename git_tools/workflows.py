import os
import sys
import json
import subprocess
import argparse

from .logger import Logger, SilentLogger
from . import git_utils

def commit_and_push_workflow(logger: Logger, args: argparse.Namespace):
    agent_id = os.environ.get("GIT_CLI_AGENT_ID")
    git_utils.check_git_repo(logger)
    ssh_env = git_utils.get_ssh_env(agent_id, logger)

    if not isinstance(logger, SilentLogger):
        stdout, _ = git_utils.run_command(["git", "config", "user.name"], logger=logger, capture_output=True, check_error=False)
        if not stdout.strip():
            git_user = logger.prompt("Entrez votre nom d'utilisateur Git")
            git_utils.run_command(["git", "config", "user.name", git_user], logger=logger)
        stdout, _ = git_utils.run_command(["git", "config", "user.email"], logger=logger, capture_output=True, check_error=False)
        if not stdout.strip():
            git_email = logger.prompt("Entrez votre email Git")
            git_utils.run_command(["git", "config", "user.email", git_email], logger=logger)

    commit_message = getattr(args, 'message', None)
    if isinstance(logger, SilentLogger) and not commit_message:
        logger.error("Erreur : Le message de commit est obligatoire en mode non interactif (--message).")
        sys.exit(1)
    
    if agent_id:
        git_utils.set_git_config(agent_id, logger)

    try:
        stdout, _ = git_utils.run_command(["git", "status", "--porcelain"], logger=logger, capture_output=True)
        if not stdout.strip():
            logger.success("Aucun changement à commiter. Le dépôt est à jour.")
            return

        logger.info("Statut actuel du dépôt :")
        git_utils.run_command(["git", "status"], logger=logger)

        stdout, _ = git_utils.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], logger=logger, capture_output=True)
        current_branch = stdout.strip()

        if not isinstance(logger, SilentLogger) and current_branch in ["main", "master"]:
            if not logger.confirm(f"Vous êtes sur la branche '{current_branch}'. Voulez-vous vraiment commiter directement sur cette branche ?", default=False, abort=True):
                return

        if logger.confirm("Voulez-vous indexer tous les changements et créer un commit ?", default=True):
            git_utils.run_command(["git", "add", "."], logger=logger)
            logger.success("Tous les changements ont été indexés.")
            
            msg = commit_message or logger.prompt("Entrez le message de commit", default="chore: Update")

            if not msg:
                logger.error("Le message de commit ne peut pas être vide.")
                git_utils.run_command(["git", "reset"], logger=logger, check_error=False)
                sys.exit(1)
            
            commit_command = ["git", "commit", "-m", msg]
            if getattr(args, 'amend', False):
                commit_command.append('--amend')

            git_utils.run_command(commit_command, logger=logger)
            logger.success("Commit créé.")

            if logger.confirm("Voulez-vous pousser les changements maintenant ?", default=True):
                logger.info("Poussée vers le dépôt distant...")
                git_utils.run_command(["git", "push"], logger=logger, env=ssh_env)
                logger.success("Les changements ont été poussés.")
    finally:
        if agent_id:
            git_utils.unset_git_config(logger)

def create_release_workflow(logger: Logger, args: argparse.Namespace):
    agent_id = os.environ.get("GIT_CLI_AGENT_ID")
    git_utils.check_git_repo(logger)
    ssh_env = git_utils.get_ssh_env(agent_id, logger)
    version_type = getattr(args, 'type', None)

    if isinstance(logger, SilentLogger) and not version_type:
        logger.error("Erreur : Le type de version (--type) est obligatoire en mode non interactif.")
        sys.exit(1)

    if agent_id:
        git_utils.set_git_config(agent_id, logger)

    try:
        logger.info("Assistant de création de Release")
        stdout, _ = git_utils.run_command(["git", "status", "--porcelain"], logger=logger, capture_output=True)
        if stdout.strip():
            logger.error("Votre répertoire de travail n'est pas propre. Veuillez commiter ou ranger vos changements.")
            sys.exit(1)
        logger.success("Le répertoire de travail est propre.")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        version_file_path = os.path.join(script_dir, "version.json")
        
        with open(version_file_path, 'r') as f:
            current_version = json.load(f).get("version", "0.0.0")

        if not version_type:
            version_info = git_utils.get_next_version(current_version, logger)
            if not version_info: sys.exit(1)
            next_version, version_type = version_info
        else:
            base_version = current_version.split('-')[0]
            major, minor, patch = map(int, base_version.split('.'))
            if version_type == "patch": next_version = f"{major}.{minor}.{patch + 1}"
            elif version_type == "minor": next_version = f"{major}.{minor + 1}.0"
            else: next_version = f"{major + 1}.0.0"

        logger.info(f"La nouvelle version sera : {next_version}")
        tag_message = git_utils.get_tag_message(version_type, next_version, logger)

        if getattr(args, 'dry_run', False):
            logger.warning("DRY RUN: Aucune modification ne sera appliquée.")
            return

        if not logger.confirm("Confirmez-vous la création de cette release ?", default=True, abort=True):
            return

        with open(version_file_path, 'w') as f:
            json.dump({"version": next_version}, f, indent=4)

        git_utils.run_command(["git", "add", version_file_path], logger=logger)
        git_utils.run_command(["git", "commit", "-m", f"chore(release): Bump version to {next_version}"], logger=logger)
        git_utils.run_command(["git", "tag", "-a", f"v{next_version}", "-m", tag_message], logger=logger)
        git_utils.run_command(["git", "push"], logger=logger, env=ssh_env)
        git_utils.run_command(["git", "push", "--tags"], logger=logger, env=ssh_env)

        logger.success(f"Release v{next_version} créée et poussée avec succès !")

    finally:
        if agent_id:
            git_utils.unset_git_config(logger)

def sync_with_remote_workflow(logger: Logger, args: argparse.Namespace):
    # ... (implementation)
    logger.info("Sync workflow coming soon...")

def manage_tags_workflow(logger: Logger, args: argparse.Namespace):
    # ... (implementation)
    logger.info("Tag management workflow coming soon...")
