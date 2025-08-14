# Super Replace

Super Replace is an intelligent code replacement tool designed to perform precise and consistent replacements within codebases.

## Features

*   **Autonomous (Rule-based) Replacements:** Utilizes Abstract Syntax Trees (AST) for context-aware replacements in Python code.
*   **LLM Integration (Planned):** Future integration with Large Language Models for complex replacements requiring deep contextual understanding.

## Installation

1.  Navigate to the `super_replace` directory:
    ```bash
    cd /mnt/c/Users/frede/OneDrive/projets/teams-ai-python-env/super_replace
    ```
2.  Activate your Python virtual environment (if you have one):
    ```bash
    source /path/to/your/venv/bin/activate
    ```
3.  Install the package in editable mode:
    ```bash
    pip install -e .
    ```

## Usage (Autonomous Mode)

To use the autonomous replacement feature, you can provide the code as a string, the target to replace, the replacement string, and optional context rules (e.g., specific functions).

```bash
super_replace autonomous \
"""
def example_function():
    x = 10
    y = x + 5
    print(y)

def another_function():
    x = 20
    print(x)
""" \
x \
new_x \
-f example_function
```

This command will replace `x` with `new_x` only within `example_function`.

## Development

### LLM Integration

Future development will focus on integrating LLMs for more complex and nuanced code transformations. This will involve:

*   **`llm_integrator.py`:** For handling API calls and interactions with LLMs.
*   **`context_analyzer.py`:** For extracting and providing rich context to the LLM.

**Note:** LLM integration will require appropriate API keys and environment setup, which are outside the scope of this tool's direct implementation.
