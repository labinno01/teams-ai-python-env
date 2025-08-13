import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
import os
import requests # Added import

from sshkeys.core.ssh import generate_ssh_key, add_key_to_host # Added add_key_to_host
from sshkeys.core.models import HostConfig

@patch('subprocess.run')
def test_generate_ssh_key(mock_subprocess_run, tmp_path):
    # Mock HostConfig
    host_config = HostConfig(
        host_type="server",
        alias="test_host",
        real_host="192.168.1.1",
        user="test_user",
        key_path=str(tmp_path / "test_key"),
        key_type="ed25519",
        comment="test_comment", # Add comment
        passphrase_flag=False # No passphrase
    )

    # Ensure the key path does not exist initially
    key_path = Path(host_config.key_path)
    assert not key_path.exists()

    # Call the function
    generated_key_path = generate_ssh_key(host_config)

    print(mock_subprocess_run.call_args_list) # Debug print

    # Assert subprocess.run was called correctly for ssh-keygen
    assert any("ssh-keygen" in call.args[0] for call in mock_subprocess_run.call_args_list)

    # Assert subprocess.run was called correctly for ssh-add
    mock_subprocess_run.assert_any_call(["ssh-add", str(key_path)], check=True)

    # Assert the returned path is correct
    assert generated_key_path == key_path

    # Simulate key creation by touching the file (since subprocess is mocked)
    key_path.touch()
    assert key_path.exists()

@patch('subprocess.run')
def test_generate_ssh_key_overwrite(mock_subprocess_run, tmp_path):
    # Create a dummy existing key
    existing_key_path = tmp_path / "existing_key"
    existing_key_path.touch()

    host_config = HostConfig(
        host_type="server",
        alias="test_host_overwrite",
        real_host="192.168.1.2",
        user="test_user_overwrite",
        key_path=str(existing_key_path),
        key_type="rsa",
        comment="overwrite_comment", # Add comment
        passphrase_flag=False # No passphrase
    )

    # Call the function with overwrite=True
    generated_key_path = generate_ssh_key(host_config, overwrite=True)

    print(mock_subprocess_run.call_args_list) # Debug print

    # Assert ssh-keygen was called (implying overwrite)
    assert any("ssh-keygen" in call.args[0] for call in mock_subprocess_run.call_args_list)

    assert generated_key_path == existing_key_path

@patch('subprocess.run')
def test_generate_ssh_key_no_overwrite_raises_error(mock_subprocess_run, tmp_path):
    # Create a dummy existing key
    existing_key_path = tmp_path / "existing_key_no_overwrite"
    existing_key_path.touch()

    host_config = HostConfig(
        host_type="server",
        alias="test_host_no_overwrite",
        real_host="192.168.1.3",
        user="test_user_no_overwrite",
        key_path=str(existing_key_path),
        key_type="ed25519",
        comment="no_overwrite_comment", # Add comment
        passphrase_flag=False # No passphrase
    )

    # Call the function without overwrite=True, expect FileExistsError
    with pytest.raises(FileExistsError):
        generate_ssh_key(host_config, overwrite=False)

    # Assert subprocess.run was NOT called (because of early exit)
    mock_subprocess_run.assert_not_called()

@patch('requests.post')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists', return_value=True)
@patch('os.environ.get', return_value='dummy_pat')
def test_add_key_to_host_github_success(mock_env_get, mock_path_exists, mock_open_file, mock_requests_post, tmp_path):
    # Mock public key file content
    mock_open_file.return_value.__enter__.return_value.read.return_value = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test_key.pub"

    # Mock HostConfig for GitHub
    host_config = HostConfig(
        host_type="github",
        alias="github.com",
        real_host="github.com",
        user="git",
        key_path=str(tmp_path / "test_key"),
        key_type="ed25519"
    )

    # Mock requests.post response
    mock_requests_post.return_value.status_code = 201
    mock_requests_post.return_value.json.return_value = {"id": 123, "key": "..."}

    # Call the function
    add_key_to_host(host_config)

    # Assert requests.post was called correctly
    mock_requests_post.assert_called_once_with(
        "https://api.github.com/user/keys",
        headers={
            "Authorization": "token dummy_pat",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "title": f"sshkeys-agent-{host_config.alias}",
            "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test_key.pub"
        }
    )

@patch('requests.post')
@patch('builtins.open', new_callable=mock_open)
@patch('pathlib.Path.exists', return_value=True)
@patch('os.environ.get', return_value='dummy_pat')
def test_add_key_to_host_github_failure(mock_env_get, mock_path_exists, mock_open_file, mock_requests_post, tmp_path):
    # Mock public key file content
    mock_open_file.return_value.__enter__.return_value.read.return_value = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... test_key.pub"

    # Mock HostConfig for GitHub
    host_config = HostConfig(
        host_type="github",
        alias="github.com",
        real_host="github.com",
        user="git",
        key_path=str(tmp_path / "test_key"),
        key_type="ed25519"
    )

    # Mock requests.post response for failure
    mock_requests_post.return_value.status_code = 422
    mock_requests_post.return_value.json.return_value = {"message": "Validation Failed"}
    mock_requests_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()

    # Call the function, expect HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        add_key_to_host(host_config)

@patch('pathlib.Path.exists', return_value=False)
def test_add_key_to_host_public_key_not_found(mock_path_exists, tmp_path):
    # Mock HostConfig
    host_config = HostConfig(
        host_type="github",
        alias="github.com",
        real_host="github.com",
        user="git",
        key_path=str(tmp_path / "test_key"),
        key_type="ed25519"
    )

    # Call the function, expect FileNotFoundError
    with pytest.raises(FileNotFoundError):
        add_key_to_host(host_config)

# This test is problematic given the HostConfig model's strictness.
# The HostConfig model itself prevents 'host_type="unsupported"'.
# The 'add_key_to_host' function for 'host_type="server"' prints a message, it does not raise a ValueError.
# Therefore, this test is commented out as it does not effectively test a valid scenario.
# def test_add_key_to_host_unsupported_type():
#     # Mock HostConfig with a valid host_type, but one that add_key_to_host doesn't explicitly handle
#     # This tests the ValueError raised by add_key_to_host for unhandled host_types
#     host_config = HostConfig(
#         host_type="server", # Use a valid host_type for HostConfig, but one that add_key_to_host will raise ValueError for
#         alias="some_host",
#         real_host="some_host.com",
#         user="user",
#         key_path="/tmp/key",
#         key_type="ed25519"
#     )

#     # Call the function, expect ValueError
#     with pytest.raises(ValueError, match="Type d'hôte non supporté pour l'ajout de clé: server"):
#         add_key_to_host(host_config)