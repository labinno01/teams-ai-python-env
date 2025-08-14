import tempfile
import pytest
from pathlib import Path
from sshkeys.core.known_hosts import (
    parse_known_hosts,
    add_host_to_known,
    remove_host_from_known,
    verify_known_hosts_consistency
)

@pytest.fixture
def mock_known_hosts(monkeypatch):
    """Crée un fichier known_hosts temporaire pour les tests."""
    content = """
    github.com ssh-rsa AAAAB3NzaC1yc2E...
    mon-serveur.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYT...
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(content)
        f.flush()
        temp_path = Path(f.name)

    # Use monkeypatch to temporarily set KNOWN_HOSTS_PATH
    monkeypatch.setattr("sshkeys.core.known_hosts.KNOWN_HOSTS_PATH", temp_path)

    yield temp_path

    # monkeypatch automatically reverts the change after the test
    temp_path.unlink()

def test_parse_known_hosts(mock_known_hosts):
    hosts = parse_known_hosts()
    assert "github.com" in hosts
    assert "ssh-rsa" in hosts["github.com"][0]
    assert len(hosts["mon-serveur.com"]) == 1

def test_add_and_remove_host(mock_known_hosts):
    # Ajout
    assert add_host_to_known("nouvel-hote.com", "ssh-rsa", "AAAAB3NzaC1yc2E...")
    hosts = parse_known_hosts()
    assert "nouvel-hote.com" in hosts

    # Suppression
    assert remove_host_from_known("nouvel-hote.com")
    hosts = parse_known_hosts()
    assert "nouvel-hote.com" not in hosts

def test_consistency_check():
    # À compléter avec des tests mockant list_ssh_configs()
    pass
