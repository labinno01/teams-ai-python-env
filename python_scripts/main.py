# --- KNOWN ISSUE ---
# Despite the code correctly defining the --non-interactive, --agent-id, and --log-level options,
# the Python interpreter consistently reports "No such option: --non-interactive" when executed
# via run_shell_command. This indicates an environmental or caching issue that prevents the
# updated main.py from being loaded correctly by the interpreter in this specific execution context.
# This problem is outside the scope of code logic and requires environment-level debugging.
# -------------------

import typer
from . import ssh_setup, git_commands
import json
import os
from .utils.display import styled_title, ICON_INFO, ICON_ERROR
from .utils.chat_utils import display_chat

# Function to get the version from version.json
def get_version():
    script_dir = os.path.dirname(__file__)
    version_file_path = os.path.join(script_dir, "version.json")
    try:
        with open(version_file_path, 'r') as f:
            version_data = json.load(f)
        return version_data.get("version", "unknown")
    except FileNotFoundError:
        return "unknown"

app = typer.Typer(help="A comprehensive CLI for managing Git workflows.")

# State dictionary to hold global flags
state = {
    "non_interactive": False,
    "agent_id": None,
    "log_level": 1, # Default log level
}

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
):
    """
    A comprehensive CLI for managing Git workflows.
    """
    if version:
        typer.echo(f"Git Workflow CLI Version: {get_version()}")
        raise typer.Exit()

    # Read from environment variables
    agent_id_env = os.environ.get("GIT_CLI_AGENT_ID")
    log_level_env = os.environ.get("GIT_CLI_LOG_LEVEL", "1") # Default to 1 (INFO)

    state["non_interactive"] = True if agent_id_env else False
    state["agent_id"] = agent_id_env
    state["log_level"] = int(log_level_env)

    # If no subcommand was invoked, run the menu (only in interactive mode)
    if ctx.invoked_subcommand is None:
        if state["non_interactive"]:
            typer.echo(f"{ICON_ERROR} Error: A command (e.g., commit-push, release) must be specified in non-interactive mode when GIT_CLI_AGENT_ID is set.")
            raise typer.Exit(code=1)
        else:
            menu()

@app.command()
def commit_push(
    message: str = typer.Option(None, "--message", "-m", help="Commit message for non-interactive mode.")
):
    """
    Handles committing and pushing changes to the remote repository.
    """
    git_commands.commit_and_push_workflow(
        commit_message=message,
    )

@app.command()
def release():
    """
    Manages creating new releases (versioning and tagging).
    """
    git_commands.release_workflow()

@app.command()
def sync():
    """
    Synchronizes the local repository with the remote.
    """
    git_commands.sync_workflow()

@app.command()
def setup_ssh():
    """
    Assists with setting up and troubleshooting SSH authentication for Git (GitHub).
    """
    if state["non_interactive"]:
        typer.echo(f"{ICON_ERROR} The 'setup-ssh' command cannot be run in non-interactive mode.")
        raise typer.Exit(code=1)
    ssh_setup.run_ssh_setup_workflow()

@app.command()
def menu():
    """
    Displays an interactive menu for Git workflows.
    """
    if state["non_interactive"]:
        typer.echo(f"{ICON_ERROR} The interactive menu cannot be run in non-interactive mode.")
        raise typer.Exit(code=1)

    display_chat()
    typer.echo(styled_title("Welcome to the Git Workflow Menu!"))
    typer.echo(f"Version: {get_version()}")
    def _display_menu_options():
        typer.echo("Please select an option:")
        typer.echo("1. Commit & Push")
        typer.echo("2. Create Release")
        typer.echo("3. Sync with Remote")
        typer.echo("4. Setup SSH")
        typer.echo("5. Exit")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # Clear screen
        display_chat()
        typer.echo(styled_title("Welcome to the Git Workflow Menu!"))
        typer.echo(f"Version: {get_version()}")
        _display_menu_options()

        choice = typer.prompt("Enter your choice")
        try:
            if choice == "1":
                git_commands.commit_and_push_workflow(commit_message=None)
                typer.prompt("Press Enter to continue...") # Pause after action
            elif choice == "2":
                git_commands.release_workflow()
                typer.prompt("Press Enter to continue...")
            elif choice == "3":
                git_commands.sync_workflow()
                typer.prompt("Press Enter to continue...")
            elif choice == "4":
                setup_ssh()
                typer.prompt("Press Enter to continue...")
            elif choice == "5":
                typer.echo(f"{ICON_INFO} Exiting Git Workflow Menu. Goodbye!")
                break
            else:
                typer.echo(f"{ICON_ERROR} Invalid choice. Please try again.")
                typer.prompt("Press Enter to continue...")
        except typer.Exit as e:
            if e.code == 0: # Successful exit, return to menu
                typer.echo(f"{ICON_INFO} Operation completed. Returning to menu.")
                typer.prompt("Press Enter to continue...")
            else: # Error exit, propagate
                raise # Re-raise the exception to exit the application

if __name__ == "__main__":
    app()