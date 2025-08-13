# Agent Capabilities and Available Tools

This document outlines the tools and capabilities available to the agent, along with best practices for their use. Understanding these tools is crucial for efficient and effective development, avoiding redundant work, and leveraging existing functionalities.

## Core Principles

*   **Leverage Existing Tools:** Before attempting to re-develop any functionality, check if an existing tool or capability already provides it.
*   **Understand Tool Limitations:** Be aware of the specific limitations and nuances of each tool (e.g., the strictness of the `replace` tool).
*   **Prioritize Safety and Efficiency:** Use tools in a manner that ensures the safety of the codebase and the efficiency of the development process.

## Available Tools

The agent has access to a set of powerful tools to interact with the filesystem, execute shell commands, perform web searches, and manage memory. These tools are exposed via the `default_api`.

### 1. Filesystem Interaction

*   **`default_api.list_directory(path, file_filtering_options, ignore)`**
    *   **Purpose:** Lists files and subdirectories within a specified path.
    *   **Best Practices:** Always use absolute paths. Can filter using glob patterns and respect `.gitignore`.
    *   **Example:** `default_api.list_directory(path='/path/to/project', ignore=['*.log'])`

*   **`default_api.read_file(absolute_path, limit, offset)`**
    *   **Purpose:** Reads the content of a specified file. Supports text, images, and PDF files.
    *   **Best Practices:** Always use absolute paths. Crucial for understanding file content before modification. For large text files, use `limit` and `offset` for pagination.
    *   **Example:** `default_api.read_file(absolute_path='/path/to/file.txt')`

*   **`default_api.read_many_files(paths, exclude, file_filtering_options, include, recursive, useDefaultExcludes)`**
    *   **Purpose:** Reads content from multiple files specified by paths or glob patterns. Useful for gaining context from multiple files simultaneously.
    *   **Best Practices:** Use when a broad understanding of multiple files is needed. Supports glob patterns and exclusions.
    *   **Example:** `default_api.read_many_files(paths=['src/**/*.py', 'docs/*.md'])`

*   **`default_api.search_file_content(pattern, include, path)`**
    *   **Purpose:** Searches for a regular expression pattern within file contents.
    *   **Best Practices:** Efficient for finding specific code snippets or patterns across the codebase. Can filter by glob patterns.
    *   **Example:** `default_api.search_file_content(pattern='function\s+myFunction', include='*.js')`

*   **`default_api.write_file(content, file_path)`**
    *   **Purpose:** Writes content to a specified file.
    *   **Best Practices:** Always use absolute paths. Use with caution as it overwrites existing content. Ensure content is correctly formatted and encoded.
    *   **Example:** `default_api.write_file(content='Hello World', file_path='/path/to/new_file.txt')`

*   **`default_api.replace(file_path, new_string, old_string, expected_replacements)`**
    *   **Purpose:** Replaces text within a file.
    *   **Best Practices:** **Highly sensitive to exact string matching.** Always `read_file` the target content immediately before using `replace` to construct `old_string` precisely. For complex, multi-line, or uncertain changes, prefer the fallback method: `read_file` -> modify in memory -> `write_file`. Avoid escaping `old_string` or `new_string` unless explicitly required by the underlying system.
    *   **Example:** `default_api.replace(file_path='/file.txt', old_string='old text', new_string='new text')`

*   **`default_api.glob(pattern, case_sensitive, path, respect_git_ignore)`**
    *   **Purpose:** Finds files matching specific glob patterns.
    *   **Best Practices:** Efficient for locating files by name or path structure. Can respect `.gitignore`.
    *   **Example:** `default_api.glob(pattern='**/*.py')`

### 2. Shell Command Execution

*   **`default_api.run_shell_command(command, description, directory)`**
    *   **Purpose:** Executes a given shell command.
    *   **Best Practices:** Provide a clear `description` for commands that modify the filesystem or system state. Use `&` for background processes. Avoid interactive commands. Ensure commands are safe and necessary.
    *   **Example:** `default_api.run_shell_command(command='ls -l', description='List files in current directory.')`

### 3. Web Interaction

*   **`default_api.web_fetch(prompt)`**
    *   **Purpose:** Processes content from URLs (including local/private network) based on instructions in the prompt.
    *   **Best Practices:** Include clear instructions and up to 20 URLs. Useful for summarizing web content or extracting specific data.
    *   **Example:** `default_api.web_fetch(prompt='Summarize https://example.com/article')`

*   **`default_api.google_web_search(query)`**
    *   **Purpose:** Performs a web search using Google Search.
    *   **Best Practices:** Use for finding general information on the internet.
    *   **Example:** `default_api.google_web_search(query='Python best practices')`

### 4. Memory Management

*   **`default_api.save_memory(fact)`**
    *   **Purpose:** Saves a specific piece of information or fact to long-term memory.
    *   **Best Practices:** Use only for user-specific facts or preferences that should persist across sessions. Do not use for conversational context or general project information.
    *   **Example:** `default_api.save_memory(fact='User prefers tabs over spaces.')`

## Common Workflows and Best Practices

*   **Code Modification:** Always `read_file` before `replace`. For complex changes, use `read_file` -> in-memory modification -> `write_file` as a robust fallback.
*   **Git Operations:** Use `run_shell_command` for `git status`, `git add`, `git commit`, `git push`, etc. Always check `git status` before committing.
*   **Python Development:** Leverage `run_shell_command` for `pip install`, `poetry install`, `pytest`, `ruff check`, `black`, etc. Always work within virtual environments.
*   **Problem Solving:** Use `search_file_content` and `glob` to understand the codebase. Use `google_web_search` for external knowledge.

### 5. Orchestration of External Python Development Tools

The agent is capable of orchestrating a wide range of external Python development tools by executing them via `default_api.run_shell_command`. This allows the agent to leverage industry-standard tools for various development tasks.

*   **Formatage de Code :** Black, Autopep8
*   **Linting :** Pylint, Flake8, Ruff
*   **Gestion des Dépendances :** Pipenv, Poetry
*   **Tests :** Pytest, Unittest
*   **Environnements Virtuels :** Virtualenv, Conda
*   **Documentation :** Sphinx, MkDocs
*   **Gestion de Version :** Git, GitPython
*   **Construction et Déploiement :** Setuptools, Twine
*   **Profiling et Performance :** cProfile, Py-Spy
*   **Gestion des Erreurs et Logging :** Logging, Sentry
*   **Gestion des Données :** Pandas, SQLAlchemy
*   **Sécurité :** Bandit, Safety

This document will be updated as new tools and capabilities are introduced or refined.
