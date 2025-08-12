"""Module de gestion des logs et interactions utilisateur pour Git Workflow Tool.

Ce module fournit une interface unifiée pour :
- L'affichage de messages (info, succès, erreur, avertissement)
- La gestion des confirmations utilisateur
- La saisie interactive/non-interactive
- Le logging en mode debug

Classes :
    Logger : Interface abstraite pour les opérations de logging.
    ConsoleLogger : Implémentation concrète pour la sortie console.
    SilentLogger : Implémentation silencieuse (pour les scripts non-interactifs).
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

# --- Constantes de style ---
class Color:
    """Codes ANSI pour la colorisation des sorties console."""
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

# --- Icônes visuelles ---
ICON_SUCCESS = f"{Color.OKGREEN}✓{Color.ENDC}"
ICON_ERROR = f"{Color.FAIL}✗{Color.ENDC}"
ICON_INFO = f"{Color.OKBLUE}ℹ{Color.ENDC}"
ICON_WARN = f"{Color.WARNING}⚠{Color.ENDC}"
ICON_DEBUG = f"{Color.HEADER}🐛{Color.ENDC}"
ICON_INPUT = f"{Color.BOLD}❯{Color.ENDC}"

@runtime_checkable
class Logger(Protocol):
    """Interface pour les opérations de logging et d'interaction utilisateur."""

    def info(self, message: str, newline: bool = True) -> None:
        """Affiche un message informatif."""
        ...

    def success(self, message: str, newline: bool = True) -> None:
        """Affiche un message de succès."""
        ...

    def error(self, message: str, newline: bool = True) -> None:
        """Affiche un message d'erreur."""
        ...

    def warning(self, message: str, newline: bool = True) -> None:
        """Affiche un message d'avertissement."""
        ...

    def debug(self, message: str, newline: bool = True) -> None:
        """Affiche un message de debug (si DEBUG=1)."""
        ...

    def confirm(
        self,
        prompt: str,
        default: Optional[bool] = None,
        abort: bool = False,
    ) -> bool:
        """Demande une confirmation à l'utilisateur.

        Args:
            prompt: Message à afficher.
            default: Valeur par défaut (None = aucune valeur par défaut).
            abort: Si True, quitte le programme en cas de réponse négative.

        Returns:
            bool: True si l'utilisateur a confirmé, False sinon.
        """
        ...

    def prompt(
        self,
        prompt: str,
        default: Optional[str] = None,
        password: bool = False,
    ) -> str:
        """Demande une saisie utilisateur.

        Args:
            prompt: Message à afficher.
            default: Valeur par défaut.
            password: Masquer la saisie (pour les mots de passe).

        Returns:
            str: La saisie utilisateur.
        """
        ...

class ConsoleLogger:
    """Implémentation concrète de Logger pour la sortie console.

    Gère :
    - La colorisation des messages
    - Les interactions utilisateur
    - Le mode debug (via la variable d'environnement DEBUG)
    - Les confirmations et saisies
    """

    def __init__(self, force_color: bool = False) -> None:
        """Initialise le logger console.

        Args:
            force_color: Forcer l'affichage des couleurs (même si stdout n'est pas un TTY).
        """
        self._force_color = force_color
        self._debug_mode = os.environ.get("DEBUG", "0").lower() in ("1", "true", "yes")

    def _should_colorize(self) -> bool:
        """Détermine si les couleurs doivent être affichées."""
        if self._force_color:
            return True
        return sys.stdout.isatty()

    def _format_message(self, icon: str, message: str, color: str) -> str:
        """Formate un message avec icône et couleur."""
        if not self._should_colorize():
            return f"{icon} {message}"
        return f"{color}{icon}{Color.ENDC} {message}"

    def info(self, message: str, newline: bool = True) -> None:
        """Affiche un message informatif."""
        formatted = self._format_message(ICON_INFO, message, Color.OKBLUE)
        self._print(formatted, newline)

    def success(self, message: str, newline: bool = True) -> None:
        """Affiche un message de succès."""
        formatted = self._format_message(ICON_SUCCESS, message, Color.OKGREEN)
        self._print(formatted, newline)

    def error(self, message: str, newline: bool = True) -> None:
        """Affiche un message d'erreur."""
        formatted = self._format_message(ICON_ERROR, message, Color.FAIL)
        self._print(formatted, newline, file=sys.stderr)

    def warning(self, message: str, newline: bool = True) -> None:
        """Affiche un message d'avertissement."""
        formatted = self._format_message(ICON_WARN, message, Color.WARNING)
        self._print(formatted, newline)

    def debug(self, message: str, newline: bool = True) -> None:
        """Affiche un message de debug (si DEBUG=1)."""
        if not self._debug_mode:
            return
        formatted = self._format_message(ICON_DEBUG, message, Color.HEADER)
        self._print(formatted, newline)

    def _print(self, message: str, newline: bool, file=sys.stdout) -> None:
        """Affiche un message avec gestion des nouvelles lignes."""
        end = "\n" if newline else ""
        print(message, end=end, file=file, flush=True)

    def confirm(
        self,
        prompt: str,
        default: Optional[bool] = None,
        abort: bool = False,
    ) -> bool:
        """Demande une confirmation à l'utilisateur.

        Args:
            prompt: Message à afficher.
            default: Valeur par défaut (None = aucune valeur par défaut).
            abort: Si True, quitte le programme en cas de réponse négative.

        Returns:
            bool: True si l'utilisateur a confirmé, False sinon.

        Raises:
            SystemExit: Si abort=True et que l'utilisateur refuse.
        """
        if default is None:
            choices = "[y/N]"
            default_str = "n"
        elif default:
            choices = "[Y/n]"
            default_str = "y"
        else:
            choices = "[y/N]"
            default_str = "n"

        while True:
            full_prompt = f"{ICON_INPUT} {prompt} {choices} "
            self._print(full_prompt, newline=False)
            choice = input().strip().lower()

            if not choice:
                confirmed = default if default is not None else False
            else:
                confirmed = choice.startswith("y")

            if confirmed:
                return True
            if not abort:
                return False
            self.error("Operation aborted by user.")
            sys.exit(1)

    def prompt(
        self,
        prompt: str,
        default: Optional[str] = None,
        password: bool = False,
    ) -> str:
        """Demande une saisie utilisateur.

        Args:
            prompt: Message à afficher.
            default: Valeur par défaut.
            password: Masquer la saisie (pour les mots de passe).

        Returns:
            str: La saisie utilisateur.
        """
        if default:
            prompt_with_default = f"{prompt} [{default}]"
        else:
            prompt_with_default = prompt

        self._print(f"{ICON_INPUT} {prompt_with_default}", newline=False)

        if password:
            try:
                import getpass
                value = getpass.getpass("")
            except ImportError:
                # Fallback si getpass n'est pas disponible
                value = input()
        else:
            value = input()

        return value.strip() if value.strip() else default if default else ""

class SilentLogger:
    """Implémentation silencieuse pour les scripts non-interactifs.

    Ignore tous les messages sauf les erreurs et les messages de debug.
    """

    def __init__(self) -> None:
        self._debug_mode = os.environ.get("DEBUG", "0").lower() in ("1", "true", "yes")

    def info(self, message: str, newline: bool = True) -> None:
        """Ne fait rien (mode silencieux)."""
        pass

    def success(self, message: str, newline: bool = True) -> None:
        """Ne fait rien (mode silencieux)."""
        pass

    def warning(self, message: str, newline: bool = True) -> None:
        """Ne fait rien (mode silencieux)."""
        pass

    def debug(self, message: str, newline: bool = True) -> None:
        """Affiche un message de debug (si DEBUG=1)."""
        if not self._debug_mode:
            return
        print(f"🐛 [DEBUG] {message}", file=sys.stderr)

    def error(self, message: str, newline: bool = True) -> None:
        """Affiche les erreurs sur stderr."""
        print(f"{ICON_ERROR} {message}", file=sys.stderr)

    def confirm(
        self,
        prompt: str,
        default: Optional[bool] = None,
        abort: bool = False,
    ) -> bool:
        """En mode silencieux, retourne toujours True (sauf si default=False)."""
        if default is False:
            return False
        return True

    def prompt(
        self,
        prompt: str,
        default: Optional[str] = None,
        password: bool = False,
    ) -> str:
        """En mode silencieux, retourne la valeur par défaut ou une chaîne vide."""
        return default if default is not None else ""

def get_logger(non_interactive: bool = False, force_color: bool = False) -> Logger:
    """Fabrique pour obtenir un logger adapté au contexte.

    Args:
        non_interactive: Si True, retourne un SilentLogger.
        force_color: Forcer l'affichage des couleurs.

    Returns:
        Logger: Une instance de Logger appropriée.
    """
    if non_interactive:
        return SilentLogger()
    return ConsoleLogger(force_color=force_color)
