import os
import json
from datetime import datetime, timezone
import uuid
import time
import sys
from functools import wraps
from typing import List, Dict, Any, Optional, Callable

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "execution_log.jsonl")
MAX_LOG_FILE_SIZE_MB = 10 # Max size before rotation

def ensure_log_dir_exists():
    """Ensures the log directory exists."""
    os.makedirs(LOG_DIR, exist_ok=True)

def _check_and_rotate_log_file():
    """
    Checks if the current log file exceeds MAX_LOG_FILE_SIZE_MB and rotates it if necessary.
    """
    ensure_log_dir_exists()
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_FILE_SIZE_MB * 1024 * 1024:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        rotated_log_file = os.path.join(LOG_DIR, f"execution_log_{timestamp}.jsonl")
        try:
            os.rename(LOG_FILE, rotated_log_file)
            print(f"Log file rotated: {LOG_FILE} -> {rotated_log_file}", file=sys.stderr)
        except OSError as e:
            print(f"Error rotating log file: {e}", file=sys.stderr)

def log_execution(
    log_level: int,
    agent_id: str,
    executed_script: str,
    parameters: List[str],
    exit_code: int,
    status: str,
    duration: float,
    run_id: str,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    error_message: Optional[str] = None,
):
    """Writes a structured log entry to the execution log file."""
    if log_level == 0:
        return

    _check_and_rotate_log_file() # Check and rotate before writing

    log_record: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "agent_id": agent_id or "interactive_user",
        "executed_script": executed_script,
        "parameters": parameters,
        "status": status,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 2),
    }

    if log_level >= 2: # DEBUG level
        log_record["stdout"] = stdout
        log_record["stderr"] = stderr
    
    if error_message:
        log_record["error_message"] = error_message

    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_record) + '\n')
    except IOError as e:
        print(f"Failed to write to log file {LOG_FILE}: {e}", file=sys.stderr)

def log_workflow(func: Callable) -> Callable:
    """Decorator to log the execution of a workflow function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        run_id = str(uuid.uuid4())
        error = None
        exit_code = 0
        status = "SUCCESS"

        # Extract log_level and agent_id from environment variables
        agent_id = os.environ.get("GIT_CLI_AGENT_ID")
        log_level = int(os.environ.get("GIT_CLI_LOG_LEVEL", "1"))

        try:
            # The decorated function might call sys.exit, which raises SystemExit
            func(*args, **kwargs)
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 1
            if exit_code == 0:
                status = "SUCCESS"
            else:
                status = "FAILURE"
                error = f"Script exited with code {exit_code}"
        except Exception as e:
            exit_code = 1
            status = "FAILURE"
            error = str(e)
        finally:
            duration = time.time() - start_time
            log_execution(
                log_level=log_level,
                agent_id=agent_id,
                executed_script=f"python_scripts.main.{func.__name__}",
                parameters=sys.argv[1:], # Basic parameter logging
                exit_code=exit_code,
                status=status,
                duration=duration,
                run_id=run_id,
                error_message=error,
            )
            # Re-raise the exit exception to stop the script
            if exit_code != 0:
                sys.exit(exit_code)

    return wrapper
