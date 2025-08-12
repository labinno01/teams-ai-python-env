"""Point d'entrée principal pour Git Workflow Tool.

Ce module gère :
- L'analyse des arguments en ligne de commande
- L'initialisation du logger approprié
- Le routage vers les différents workflows
- Le menu interactif (si aucune commande n'est spécifiée)
- Les options globales (--version, --help, --non-interactive)

Usage:
    python -m git_tools [OPTIONS] COMMAND [ARGS]

Options globales:
    --version               Affiche la version et quitte
    --non-interactive       Désactive le mode interactif
    --debug                 Active les messages de debug
    --force-color           Force l'affichage des couleurs
    --help                  Affiche cette aide

Commandes disponibles:
    commit      Effectue un commit et push
    release     Crée une nouvelle release
    sync        Synchronise avec le dépôt distant
    tag         Gère les tags Git
"""

import os
import sys
import argparse
from typing import Optional, Dict, Callable, Any, NoReturn
from importlib.metadata import version, PackageNotFoundError

from git_tools.logger import get_logger, Logger
from git_tools import __version__ as package_version
from git_tools.workflows import (
    commit_and_push_workflow,
    create_release_workflow,
    sync_with_remote_workflow,
    manage_tags_workflow,
)

# --- Constantes ---
DEFAULT_COMMAND = "menu"  # Commande par défaut si aucune n'est spécifiée
COMMAND_MAPPING: Dict[str, Callable[[Logger, argparse.Namespace], None]] = {
    "commit": commit_and_push_workflow,
    "release": create_release_workflow,
    "sync": sync_with_remote_workflow,
    "tag": manage_tags_workflow,
    "menu": None,  # Géré séparément
}

# --- Fonctions utilitaires ---
def get_package_version() -> str:
    """Récupère la version du package depuis les métadonnées."""
    try:
        return version("git-tools")
    except PackageNotFoundError:
        return package_version  # Fallback si pas installé en mode editable

def print_version() -> NoReturn:
    """Affiche la version et quitte le programme."""
    print(f"Git Workflow Tool v{get_package_version()}")
    sys.exit(0)

def print_help() -> NoReturn:
    """Affiche l'aide et quitte le programme."""
    print(__doc__.strip())
    sys.exit(0)

def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """Parse les arguments de la ligne de commande.

    Args:
        args: Liste d'arguments à parser (par défaut sys.argv[1:])

    Returns:
        argparse.Namespace: Objet contenant les arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Git Workflow Tool - Outil avancé pour gérer vos workflows Git",
        add_help=False,  # On gère nous-mêmes --help pour plus de contrôle
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Options globales
    parser.add_argument(
        "--version",
        action="store_true",
        help="Affiche la version et quitte",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Désactive le mode interactif (pour les scripts/CI)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Active les messages de debug",
    )
    parser.add_argument(
        "--force-color",
        action="store_true",
        help="Force l'affichage des couleurs même si stdout n'est pas un TTY",
    )
    parser.add_argument(
        "--help",
        action="store_true",
        help="Affiche cette aide",
    )

    # Sous-commandes
    subparsers = parser.add_subparsers(
        dest="command",
        title="Commandes disponibles",
        metavar="COMMAND",
        required=False,
    )

    # Commande 'commit'
    commit_parser = subparsers.add_parser(
        "commit",
        help="Effectue un commit et push",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commit_parser.add_argument(
        "-m", "--message",
        help="Message de commit (désactive le prompt interactif)",
    )
    commit_parser.add_argument(
        "--amend",
        action="store_true",
        help="Modifie le dernier commit au lieu d'en créer un nouveau",
    )

    # Commande 'release'
    release_parser = subparsers.add_parser(
        "release",
        help="Crée une nouvelle release",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    release_parser.add_argument(
        "--type",
        choices=["major", "minor", "patch"],
        help="Type de release (major/minor/patch)",
    )
    release_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simule la création de release sans appliquer les changements",
    )

    # Commande 'sync'
    subparsers.add_parser(
        "sync",
        help="Synchronise avec le dépôt distant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Commande 'tag'
    tag_parser = subparsers.add_parser(
        "tag",
        help="Gère les tags Git",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    tag_parser.add_argument(
        "action",
        choices=["list", "create", "delete"],
        help="Action à effectuer sur les tags",
    )
    tag_parser.add_argument(
        "--name",
        help="Nom du tag (pour create/delete)",
    )
    tag_parser.add_argument(
        "--message",
        help="Message du tag (pour create)",
    )

    return parser.parse_args(args)

def display_interactive_menu(logger: Logger) -> None:
    """Affiche le menu interactif principal.

    Args:
        logger: Instance de Logger pour les interactions utilisateur
    """
    while True:
        logger.info("\n" + "="*50)
        logger.info("🐙 Git Workflow Tool - Menu Principal")
        logger.info("="*50)
        logger.info("1. Commit & Push")
        logger.info("2. Créer une Release")
        logger.info("3. Synchroniser avec le dépôt distant")
        logger.info("4. Gérer les Tags")
        logger.info("5. Quitter")

        choice = logger.prompt("Choisissez une option (1-5)")

        if choice == "1":
            commit_and_push_workflow(logger, argparse.Namespace())
        elif choice == "2":
            create_release_workflow(logger, argparse.Namespace())
        elif choice == "3":
            sync_with_remote_workflow(logger, argparse.Namespace())
        elif choice == "4":
            manage_tags_workflow(logger, argparse.Namespace())
        elif choice in ("5", "q", "quit", "exit"):
            logger.info("Au revoir !")
            sys.exit(0)
        else:
            logger.warning("Option invalide. Veuillez réessayer.")

def run_command(
    command: str,
    logger: Logger,
    args: argparse.Namespace,
) -> None:
    """Exécute la commande spécifiée.

    Args:
        command: Nom de la commande à exécuter
        logger: Instance de Logger
        args: Arguments parsés

    Raises:
        SystemExit: Si la commande est invalide
    """
    workflow = COMMAND_MAPPING.get(command)

    if workflow is None:
        if command == DEFAULT_COMMAND:
            display_interactive_menu(logger)
        else:
            logger.error(f"Commande inconnue: {command}")
            print_help()

    try:
        workflow(logger, args)
    except Exception as e:
        logger.error(f"Échec de l'exécution de la commande: {str(e)}")
        if logger.confirm("Voulez-vous voir la trace complète de l'erreur?", default=False):
            raise
        sys.exit(1)

def setup_environment(args: argparse.Namespace) -> None:
    """Configure l'environnement en fonction des arguments.

    Args:
        args: Arguments parsés
    """
    if args.debug:
        os.environ["DEBUG"] = "1"
    if args.force_color:
        os.environ["FORCE_COLOR"] = "1"

def main(args: Optional[list] = None) -> None:
    """Point d'entrée principal de l'application.

    Args:
        args: Liste d'arguments (pour les tests). Par défaut sys.argv[1:].
    """
    # Parse les arguments
    args = parse_args(args)

    # Gère les options globales
    if args.version:
        print_version()
    if args.help:
        print_help()

    # Configure l'environnement
    setup_environment(args)

    # Initialise le logger approprié
    logger = get_logger(
        non_interactive=args.non_interactive,
        force_color=args.force_color,
    )

    # Détermine la commande à exécuter
    command = args.command if args.command else DEFAULT_COMMAND

    # Exécute la commande
    run_command(command, logger, args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger = get_logger(non_interactive=True)
        logger.error("\nOpération interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        logger = get_logger(non_interactive=True)
        logger.error(f"Erreur inattendue: {str(e)}")
        sys.exit(1)
