import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from sshkeys.core.known_hosts_migration import (
    parse_known_hosts,
    convert_md5_to_sha256,
    deduplicate_entries,
    is_weak_key,
    migrate_known_hosts,
    KNOWN_HOSTS_PATH,
    BACKUP_PATH
)

@pytest.fixture
def mock_known_hosts_file(monkeypatch):
    """Crée un fichier known_hosts temporaire pour les tests de migration."""
    content = """
    github.com ssh-rsa AAAAB3NzaC1yc2EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA part2 part3
    mon-serveur.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    old-server.com ssh-rsa MD5:xx:yy:zz part2 part3
    duplicate.com ssh-rsa AAAAB3NzaC1yc2EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA part2 part3
    duplicate.com ssh-rsa AAAAB3NzaC1yc2EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA part2 part3
    weak.com ssh-rsa WEAK_RSA_KEY_FOR_TESTING part2 part3 # Assume this is a weak key for testing
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(content)
        f.flush()
        temp_path = Path(f.name)

    monkeypatch.setattr("sshkeys.core.known_hosts_migration.KNOWN_HOSTS_PATH", temp_path)
    monkeypatch.setattr("sshkeys.core.known_hosts_migration.BACKUP_PATH", Path(str(temp_path) + ".bak"))

    yield temp_path

    temp_path.unlink(missing_ok=True)
    Path(str(temp_path) + ".bak").unlink(missing_ok=True)

@pytest.fixture
def mock_subprocess_run(monkeypatch):
    """Mock subprocess.run for ssh-keyscan and ssh-keygen."""
    def mock_run(cmd, **kwargs):
        if "ssh-keyscan" in cmd:
            # Simulate ssh-keyscan output for a given host
            host = cmd[-1]
            if host == "old-server.com":
                return type("obj", (object,), {'stdout': f"{host} ssh-rsa NEW_SHA256_FINGERPRINT_FOR_OLD_SERVER\n", 'stderr': ""})
            else:
                return type("obj", (object,), {'stdout': f"{host} ssh-rsa SOME_SHA256_FINGERPRINT\n", 'stderr': ""})
        elif "ssh-keygen" in cmd and "-lf" in cmd:
            # Simulate ssh-keygen -lf output for SHA256
            return type("obj", (object,), {'stdout': "256 SOME_SHA256_FINGERPRINT user@host\n", 'stderr': ""})
        raise NotImplementedError(f"Unexpected command: {cmd}")

    monkeypatch.setattr("subprocess.run", mock_run)

def test_parse_known_hosts_migration(mock_known_hosts_file):
    hosts = parse_known_hosts(mock_known_hosts_file)
    assert "old-server.com" in hosts

def test_deduplicate_entries():
    hosts = {
        "host1": ["fp1", "fp2", "fp1"],
        "host2": ["fp3"]
    }
    deduped = deduplicate_entries(hosts)
    assert deduped == {"host1": ["fp1", "fp2"], "host2": ["fp3"]}

def test_is_weak_key():
    assert is_weak_key("ssh-rsa", "WEAK_RSA_KEY_FOR_TESTING")
    assert not is_weak_key("ssh-ed25519", "SHA256:...")

@patch('sshkeys.core.known_hosts_migration.click.echo')
def test_migrate_known_hosts_dry_run(mock_echo, mock_known_hosts_file, mock_subprocess_run):
    migrate_known_hosts(dry_run=True)
    # Check that the original file was not modified
    with open(mock_known_hosts_file, "r") as f:
        content = f.read()
        assert "old-server.com ssh-rsa MD5:xx:yy:zz" in content
    # Check echo calls for dry run messages
    mock_echo.assert_any_call("🔍 [Mode simulation] Aucune modification apportée.")

@patch('sshkeys.core.known_hosts_migration.click.echo')
def test_migrate_known_hosts_real_run(mock_echo, mock_known_hosts_file, mock_subprocess_run, capfd):
    migrate_known_hosts(dry_run=False)
    print(f"DEBUG: mock_echo calls: {mock_echo.call_args_list}")
    # Check that the backup file was created
    assert Path(str(mock_known_hosts_file) + ".bak").exists()
    # Check that the original file was modified
    with open(mock_known_hosts_file, "r") as f:
        content = f.read()
        assert "old-server.com ssh-rsa SOME_SHA256_FINGERPRINT" in content
        assert "duplicate.com ssh-rsa SOME_SHA256_FINGERPRINT" in content # Should be deduped to one entry
        assert "weak.com" not in content # Weak key should be removed
    mock_echo.assert_any_call(f"✅ Sauvegarde effectuée dans {str(Path(str(mock_known_hosts_file) + '.bak'))}")
    mock_echo.assert_any_call(f"✅ Migration terminée. 4 hôtes conservés.") # github, mon-serveur, old-server, duplicate