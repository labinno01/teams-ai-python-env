import os
import sys

# Add the parent directory to the Python path to allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python_scripts')))

from python_scripts import git_commands

# Set environment variables for the workflow
os.environ["GIT_CLI_AGENT_ID"] = "test_agent"
os.environ["GIT_CLI_LOG_LEVEL"] = "2"

print("--- Starting direct commit_and_push_workflow execution ---")

try:
    git_commands.commit_and_push_workflow(non_interactive=True, commit_message="feat: Direct debug commit")
    print("--- commit_and_push_workflow completed successfully ---")
except Exception as e:
    print(f"--- commit_and_push_workflow failed: {e} ---")
    import traceback
    traceback.print_exc()

print("--- Finished direct commit_and_push_workflow execution ---")