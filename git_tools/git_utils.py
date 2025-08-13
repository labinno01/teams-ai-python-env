import subprocess
import os
import sys
from .logger import Logger

def run_command(command: list[str], logger: Logger, check_error: bool = True, capture_output: bool = False) -> tuple[str | None, str | None]:
    logger.debug(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check_error, capture_output=capture_output, text=True)
        if capture_output:
            return result.stdout, result.stderr
        return None, None
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        sys.exit(e.returncode)

def check_git_repo(logger: Logger):
    if not os.path.isdir(".git"):
        logger.error("Ce n'est pas un dépôt Git. Veuillez d'abord l'initialiser.")
        sys.exit(1)

def get_next_version(current_version: str, logger: Logger) -> tuple[str, str] | None:
    base_version = current_version.split('-')[0]
    major, minor, patch = map(int, base_version.split('.'))
    logger.info(f"Version actuelle : {current_version}")
    logger.info("Quel type de version est-ce ?")
    logger.info(f"  1) PATCH (correction de bug, ex: {major}.{minor}.{patch + 1})")
    logger.info(f"  2) MINOR (ajout de fonctionnalité, ex: {major}.{minor + 1}.0)")
    logger.info(f"  3) MAJOR (changement majeur, ex: {major + 1}.0.0)")
    version_choice = logger.prompt("Votre choix (1, 2, 3)")
    if version_choice == "1": return f"{major}.{minor}.{patch + 1}", "PATCH"
    if version_choice == "2": return f"{major}.{minor + 1}.0", "MINOR"
    if version_choice == "3": return f"{major + 1}.0.0", "MAJOR"
    logger.error("Choix invalide.")
    return None

def get_tag_message(version_type: str, next_version: str, logger: Logger) -> str:
    try:
        last_tag, _ = run_command(["git", "describe", "--tags", "--abbrev=0"], logger=logger, check_error=False, capture_output=True)
    except Exception:
        last_tag = None

    if not last_tag:
        return f"Version {next_version}\n\nInitial release."

    log_messages, _ = run_command(["git", "log", "--oneline", f"{last_tag.strip()}..HEAD"], logger=logger, capture_output=True)
    if not log_messages.strip():
        return f"Version {next_version}\n\nAucun commit depuis le dernier tag."
    return f"Version {next_version}\n\nChangements inclus :\n{log_messages.strip()}"