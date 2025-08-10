
import subprocess
import re
from pathlib import Path

def get_project_name() -> str:
    """
    Retrieves the project name from the git remote origin URL.
    
    Returns:
        The project name, or "unknown_project" if not found.
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        # Extract project name from URL (e.g., 'https://github.com/user/project.git' -> 'project')
        match = re.search(r"/([^/]+?)(?:\.git)?$", url)
        if match:
            return match.group(1)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "unknown_project"

def get_agent_config(agent_id: str) -> dict:
    """
    Generates the configuration for a given agent ID.

    Args:
        agent_id: The ID of the agent (e.g., "001").

    Returns:
        A dictionary containing the agent's name, email, and ssh key path.
    """
    project_name = get_project_name()
    agent_name_base = "Gemini_cli"  # For now, we can hardcode this or extend later
    
    agent_name = f"{agent_name_base} {agent_id}"
    agent_email = f"{agent_name_base.lower()}_{agent_id}@{project_name}"
    
    # The key name convention is now more specific
    ssh_key_name = f"github-{project_name}-{agent_id}"
    ssh_key_path = Path.home() / ".ssh" / ssh_key_name
    
    return {
        "name": agent_name,
        "email": agent_email,
        "ssh_key_path": str(ssh_key_path),
    }

