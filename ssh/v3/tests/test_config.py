from pathlib import Path
import pytest

from sshkeys.core.config import parse_ssh_config

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
