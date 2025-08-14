import pytest
from pydantic import ValidationError
from sshkeys.core.models import HostConfig
from pathlib import Path

def test_host_config_valid_minimal():
    config = HostConfig(host_type="server", alias="myhost")
    assert config.host_type == "server"
    assert config.alias == "myhost"
    assert config.port == 22 # Default value

def test_host_config_valid_full():
    config = HostConfig(
        host_type="github",
        alias="git-test",
        real_host="github.com",
        user="git",
        port=2222,
        key_path="~/.ssh/id_rsa_test",
        key_type="rsa",
        comment="Test key",
        passphrase_flag=True
    )
    assert config.host_type == "github"
    assert config.alias == "git-test"
    assert config.real_host == "github.com"
    assert config.user == "git"
    assert config.port == 2222
    assert config.key_path == "~/.ssh/id_rsa_test"
    assert config.key_type == "rsa"
    assert config.comment == "Test key"
    assert config.passphrase_flag is True

def test_host_config_missing_host_type():
    with pytest.raises(ValidationError) as excinfo:
        HostConfig(alias="myhost")
    assert "host_type" in str(excinfo.value)
    assert "field required" in str(excinfo.value)

def test_host_config_invalid_host_type():
    with pytest.raises(ValidationError) as excinfo:
        HostConfig(host_type="invalid_type", alias="myhost")
    assert "host_type" in str(excinfo.value)
    assert "unexpected value; permitted: 'github', 'server', 'gitlab'" in str(excinfo.value)

def test_host_config_invalid_port_type():
    with pytest.raises(ValidationError) as excinfo:
        HostConfig(host_type="server", alias="myhost", port="not_a_number")
    assert "port" in str(excinfo.value)
    assert "value is not a valid integer" in str(excinfo.value)

def test_host_config_identity_file_path_conversion():
    config = HostConfig(host_type="server", alias="test", identity_file="/tmp/key")
    assert isinstance(config.identity_file, Path)
    assert str(config.identity_file) == "/tmp/key"

def test_host_config_identity_file_none():
    config = HostConfig(host_type="server", alias="test", identity_file=None)
    assert config.identity_file is None