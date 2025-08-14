import pytest
from pathlib import Path
from sshkeys.core.config import parse_ssh_config, list_ssh_configs
from sshkeys.core.models import HostConfig

@pytest.fixture
def temp_ssh_config(tmp_path):
    config_path = tmp_path / "config"
    yield config_path
    # Cleanup is handled by tmp_path fixture

@pytest.fixture
def minimal_valid_config_path(tmp_path):
    config_content = """
Host test_server
    HostName 192.168.1.1
    User user1
    Port 22
    IdentityFile ~/.ssh/id_rsa
"""
    config_file = tmp_path / "valid_config.txt"
    config_file.write_text(config_content)
    return config_file

@pytest.fixture
def minimal_invalid_config_path(tmp_path):
    config_content = """
Host my_test_host
    HostName example.com
    User testuser
    Port 22
"""
    config_file = tmp_path / "minimal_invalid_config.txt"
    config_file.write_text(config_content)
    return config_file


def test_list_ssh_configs_empty_file(temp_ssh_config):
    temp_ssh_config.touch()
    hosts = list_ssh_configs(config_path=temp_ssh_config)
    assert len(hosts) == 0

def test_list_ssh_configs_no_file():
    hosts = list_ssh_configs(config_path=Path("/nonexistent/path/config"))
    assert len(hosts) == 0

def test_list_ssh_configs_minimal_valid(minimal_valid_config_path):
    hosts = list_ssh_configs(config_path=minimal_valid_config_path)
    assert len(hosts) == 1
    host = hosts[0]
    assert host.alias == "test_server"
    assert host.real_host == "192.168.1.1"
    assert host.user == "user1"
    assert host.port == 22
    assert host.key_path == "~/.ssh/id_rsa"
    assert host.host_type == "server" # This is the default we added

def test_list_ssh_configs_regression_host_type(minimal_invalid_config_path):
    # This test specifically checks if the fix for missing host_type works
    hosts = list_ssh_configs(config_path=minimal_invalid_config_path)
    assert len(hosts) == 1
    host = hosts[0]
    assert host.alias == "my_test_host"
    assert host.host_type == "server" # Should now default to "server"

def test_parse_ssh_config_minimal_valid(minimal_valid_config_path):
    hosts = parse_ssh_config(config_path=minimal_valid_config_path)
    assert len(hosts) == 1
    host = hosts[0]
    assert host.alias == "test_server"
    assert host.real_host == "192.168.1.1"
    assert host.user == "user1"
    assert host.port == 22
    assert host.identity_file == Path.home() / ".ssh" / "id_rsa"
    assert host.host_type == "server"

def test_parse_ssh_config_multiple_hosts(tmp_path):
    config_content = """
Host host1
    HostName 1.1.1.1
Host host2
    HostName 2.2.2.2
"""
    config_file = tmp_path / "multiple_hosts.txt"
    config_file.write_text(config_content)
    hosts = parse_ssh_config(config_path=config_file)
    assert len(hosts) == 2
    assert hosts[0].alias == "host1"
    assert hosts[1].alias == "host2"

def test_parse_ssh_config_with_comments_and_empty_lines(tmp_path):
    config_content = """
# This is a comment

Host host_commented
    HostName 3.3.3.3 # Inline comment
    User test

Host another_host
    Port 22
"""
    config_file = tmp_path / "commented_config.txt"
    config_file.write_text(config_content)
    hosts = parse_ssh_config(config_path=config_file)
    assert len(hosts) == 2
    assert hosts[0].alias == "host_commented"
    assert hosts[0].real_host == "3.3.3.3"
    assert hosts[1].alias == "another_host"