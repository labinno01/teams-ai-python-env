import os
import json
import subprocess
import sys

CONFIG_FILE = os.path.expanduser("~/.python_env_config.json")

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def is_valid_python(path):
    """Checks if a path is a valid Python executable."""
    if not path or not isinstance(path, str):
        return False

    command = []
    if path.startswith("wsl:"):
        command = ["wsl", "-e", path[4:], "--version"]
    else:
        if not os.path.exists(path):
            return False
        command = [path, "--version"]

    try:
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=2)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def detect_windows_envs():
    """Detects Python environments on Windows."""
    envs = []
    try:
        result = subprocess.run(["where", "python"], capture_output=True, text=True, check=True)
        paths = result.stdout.strip().split(os.linesep)
        for path in paths:
            if is_valid_python(path):
                envs.append(path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return envs

def detect_wsl_envs():
    """Detects Python environments in WSL."""
    envs = []
    try:
        subprocess.run(["wsl", "-e", "true"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return envs

    try:
        result = subprocess.run(
            ["wsl", "-e", "bash", "-c", "which -a python python3"],
            capture_output=True, text=True, check=True, timeout=10
        )
        paths = result.stdout.strip().split(os.linesep)
        for path in paths:
            wsl_path = f"wsl:{path}"
            if is_valid_python(wsl_path):
                envs.append(wsl_path)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    return envs

def detect_python_envs(log_fn):
    """Detects all Python environments on Windows and WSL."""
    log_fn("Detecting Python environments...")
    windows_envs = detect_windows_envs()
    wsl_envs = detect_wsl_envs()
    all_envs = sorted(list(set(windows_envs + wsl_envs)))
    log_fn(f"Found {len(all_envs)} environments.")
    return all_envs

def prompt_user_choice(env_list, log_fn):
    """Prompts the user to choose a Python environment."""
    if not env_list:
        log_fn("No Python environments found.")
        return None

    log_fn("\nSelect a Python environment:")
    for i, env in enumerate(env_list):
        log_fn(f"  [{i+1}] {env}")

    while True:
        try:
            choice = input(f"Enter your choice (1-{len(env_list)}): ")
            if choice.isdigit() and 1 <= int(choice) <= len(env_list):
                return env_list[int(choice) - 1]
            else:
                log_fn("Invalid choice. Please try again.")
        except (ValueError, IndexError):
            log_fn("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            log_fn("\nOperation cancelled by user.")
            return None

def load_selected_env():
    """Loads the selected environment from the config file."""
    config = get_config()
    selected_env = config.get("selected_env")

    if is_valid_python(selected_env):
        return selected_env

    return None

def reset_env_choice(log_fn):
    """Resets the environment choice."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        log_fn("Environment choice has been reset.")
    else:
        log_fn("No environment choice to reset.")

def main():
    """Main function to manage Python environment selection."""
    import argparse
    parser = argparse.ArgumentParser(description="Manage Python environments.")
    parser.add_argument("--reset", action="store_true", help="Reset the selected environment.")
    parser.add_argument("--force", action="store_true", help="Force re-detection of environments.")
    parser.add_argument("--quiet", action="store_true", help="Suppress informational output.")
    args = parser.parse_args()

    def log(message):
        if not args.quiet:
            print(message, file=sys.stderr)

    if args.reset:
        reset_env_choice(log)
        args.force = True

    selected_env = load_selected_env()
    final_env = None

    if not selected_env or args.force:
        envs = detect_python_envs(log)
        chosen_env = prompt_user_choice(envs, log)
        if chosen_env:
            save_config({"selected_env": chosen_env})
            log(f"Selected environment: {chosen_env}")
            final_env = chosen_env
        else:
            log("No environment selected.")
            exit(1)
    else:
        log(f"Using cached environment: {selected_env}")
        final_env = selected_env

    if final_env:
        print(final_env)

if __name__ == "__main__":
    main()