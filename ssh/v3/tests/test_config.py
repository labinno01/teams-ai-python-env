from pathlib import Path
import pytest
import shutil # Added
from datetime import datetime # Added
from unittest.mock import patch # Added for monkeypatching os.name

from sshkeys.core.config import parse_ssh_config, backup_ssh_config, DEFAULT_SSH_CONFIG_PATH, BACKUP_DIR # Added backup_ssh_config, DEFAULT_SSH_CONFIG_PATH, BACKUP_DIR

# Existing test
def test_parse_ssh_config(tmp_path):
    config_content = """
    Host github.com
        User git
        IdentityFile ~/.ssh/github_key
    Host myserver
        HostName 192.168.1.10
        Port 2222
    """
    config_file = tmp_path / "config"
    config_file.write_text(config_content)

    hosts = parse_ssh_config(config_file)
    assert len(hosts) == 2
    assert hosts[0].alias == "github.com"
    assert hosts[0].user == "git"
    assert hosts[1].real_host == "192.168.1.10"
    assert hosts[1].port == 2222

# New tests for backup_ssh_config
def test_backup_ssh_config_success(tmp_path):
    """Test une sauvegarde réussie (simule WSL/Linux)."""
    # Setup
    config = tmp_path / "config"
    config.write_text("Host github.com\n    User git")
    backup_dir = tmp_path / "backups"

    # Action
    backup_path = backup_ssh_config(config_path=config, backup_dir=backup_dir)

    # Assertions
    assert backup_path.exists()
    assert backup_path.read_text() == "Host github.com\n    User git"
    assert "config_backup_" in backup_path.name

def test_backup_ssh_config_missing_file():
    """Test l'échec si le fichier config est introuvable."""
    with pytest.raises(FileNotFoundError):
        backup_ssh_config(config_path=Path("/inexistant/config"))

def test_backup_ssh_config_windows_error(monkeypatch):
    """Test le refus sous Windows natif."""
    monkeypatch.setattr("os.name", "nt")  # Simule Windows
    with pytest.raises(RuntimeError) as excinfo:
        backup_ssh_config()
    assert "WSL" in str(excinfo.value)

@patch('sshkeys.core.config.is_wsl', return_value=False) # Mock is_wsl to simulate Linux/macOS
def test_backup_ssh_config_permissions(mock_is_wsl, tmp_path):
    """Test les permissions du fichier de backup (Linux/macOS)."""
    config = tmp_path / "config"
    config.write_text("Host test")
    backup_path = backup_ssh_config(config_path=config, backup_dir=tmp_path)

    # Sous Linux/macOS, vérifie que les permissions sont 600
    # if not is_wsl():  # Ignore sous WSL (permissions non appliquées) - This check is now handled by the mock
    assert backup_path.stat().st_mode & 0o777 == 0o600