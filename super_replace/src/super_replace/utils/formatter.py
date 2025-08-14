import subprocess
import tempfile
from pathlib import Path

def format_code_with_black(code: str) -> str:
    """Formats the given Python code string using Black.

    Args:
        code: The Python code string to format.

    Returns:
        The formatted code string.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as tmp_file:
        tmp_file.write(code)
    tmp_file_path = Path(tmp_file.name)

    try:
        # Run Black on the temporary file
        result = subprocess.run(
            ['black', str(tmp_file_path)],
            capture_output=True,
            text=True,
            check=False # Do not raise an exception for non-zero exit codes
        )
        # Read the formatted content back from the file
        formatted_code = tmp_file_path.read_text()
        if result.stderr:
            print(f"Black stderr: {result.stderr}")
        return formatted_code
    finally:
        tmp_file_path.unlink() # Clean up the temporary file

def lint_code_with_ruff(code: str) -> str:
    """Lints the given Python code string using Ruff.

    Args:
        code: The Python code string to lint.

    Returns:
        The linting output from Ruff.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py') as tmp_file:
        tmp_file.write(code)
    tmp_file_path = Path(tmp_file.name)

    try:
        # Run Ruff on the temporary file
        result = subprocess.run(
            ['ruff', 'check', str(tmp_file_path)],
            capture_output=True,
            text=True,
            check=False # Do not raise an exception for non-zero exit codes
        )
        if result.stdout:
            return result.stdout
        return ""
    finally:
        tmp_file_path.unlink() # Clean up the temporary file
