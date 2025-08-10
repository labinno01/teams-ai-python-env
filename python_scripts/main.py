import typer
from . import ssh_setup
import json
import os

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

# Make menu the default command if no command is provided
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, version: bool = typer.Option(False, "--version", help="Show version and exit.")):
    """
    A comprehensive CLI for managing Git workflows.
    """
    if version:
        typer.echo(f"Git Workflow CLI Version: {get_version()}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        # If no subcommand was invoked, run the menu
        menu()

@app.command()
def commit_push():
    """
    Handles committing and pushing changes to the remote repository.
    """
    typer.echo("Running Commit & Push workflow...")
    # Placeholder for future Python implementation of commit-push.sh

@app.command()
def release():
    """
    Manages creating new releases (versioning and tagging).
    """
    typer.echo("Running Release workflow...")
    # Placeholder for future Python implementation of release-version.sh

@app.command()
def sync():
    """
    Synchronizes the local repository with the remote.
    """
    typer.echo("Running Sync workflow...")
    # Placeholder for future Python implementation of sync-remote.sh

@app.command()
def setup_ssh():
    """
    Assists with setting up and troubleshooting SSH authentication for Git (GitHub).
    """
    ssh_setup.run_ssh_setup_workflow()

@app.command()
def menu():
    """
    Displays an interactive menu for Git workflows.
    """
    typer.echo("Welcome to the Git Workflow Menu!")
    typer.echo(f"Version: {get_version()}")
    typer.echo("Please select an option:")
    typer.echo("1. Commit & Push")
    typer.echo("2. Create Release")
    typer.echo("3. Sync with Remote")
    typer.echo("4. Setup SSH")
    typer.echo("5. Exit")

    while True:
        choice = typer.prompt("Enter your choice")
        if choice == "1":
            commit_push()
        elif choice == "2":
            release()
        elif choice == "3":
            sync()
        elif choice == "4":
            setup_ssh()
        elif choice == "5":
            typer.echo("Exiting Git Workflow Menu. Goodbye!")
            break
        else:
            typer.echo("Invalid choice. Please try again.")

if __name__ == "__main__":
    app()