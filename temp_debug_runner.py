
import os
import sys
import traceback

# Add project root to path to allow module imports
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    from python_scripts import git_commands
except ImportError as e:
    print(f"Failed to import git_commands: {e}")
    print("Please ensure you are running this from the project root and the virtual environment is active.")
    sys.exit(1)

def run_test():
    os.environ["GIT_CLI_AGENT_ID"] = "gemini-cli-agent"
    commit_message = "chore: Sauvegarde avant refactorisation majeure de la CLI Python"
    
    # The workflow function determines non_interactive mode internally from the env var
    non_interactive = "GIT_CLI_AGENT_ID" in os.environ

    print("--- Starting debug runner ---")
    try:
        # The function signature in git_commands expects these arguments
        git_commands.commit_and_push_workflow(
            non_interactive=non_interactive,
            commit_message=commit_message
        )
        print("--- Debug runner finished successfully ---")
    except Exception as e:
        print(f"--- Debug runner caught an exception: {e} ---")
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
