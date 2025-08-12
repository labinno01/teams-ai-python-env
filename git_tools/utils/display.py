# ANSI color codes (from chat_utils.py)
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"

# Icons (from git_commands.py and ssh_setup.py)
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"
ICON_INFO = "ℹ️"
ICON_WARN = "⚠️"
ICON_CLIPBOARD = "📋"
ICON_KEY = "🔑"
ICON_GIT = "" # No specific icon for GIT, can be customized later

# You can also define colored strings for common messages
def colored_success(text: str) -> str:
    return f"{COLOR_GREEN}{text}{COLOR_RESET}"

def colored_error(text: str) -> str:
    return f"{COLOR_RED}{text}{COLOR_RESET}"

def colored_info(text: str) -> str:
    return f"{COLOR_BLUE}{text}{COLOR_RESET}"

def colored_warn(text: str) -> str:
    return f"{COLOR_YELLOW}{text}{COLOR_RESET}"

# Example of a styled title
def styled_title(text: str) -> str:
    return f"{COLOR_CYAN}--- {text} ---{COLOR_RESET}"

# Function to wrap text (from chat_utils.py)
def wrap_text(text, width):
    lines = []
    words = text.split(' ')
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > width and current_line:
            lines.append(current_line.strip())
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    lines.append(current_line.strip())
    return lines