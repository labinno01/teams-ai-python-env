# sshkeys Executable (Linux)

This directory contains the standalone `sshkeys` executable for Linux systems.

## Usage

This executable is self-contained and does not require a Python environment to run.

1.  **Copy the executable:**
    Transfer the `sshkeys` file to your target Linux system. You can place it in any directory, but a common location is `/usr/local/bin/` if you want it to be accessible from anywhere in your terminal.

    Example (if copying to `/usr/local/bin/`):
    ```bash
    sudo cp sshkeys /usr/local/bin/
    ```

2.  **Make it executable (if necessary):**
    Ensure the file has execute permissions:
    ```bash
    chmod +x /usr/local/bin/sshkeys
    ```

3.  **Run the command:**
    You can now run `sshkeys` commands directly:
    ```bash
    sshkeys --help
    sshkeys status
    # etc.
    ```
