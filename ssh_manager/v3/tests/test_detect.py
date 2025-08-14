from sshkeys.core.detect import detect_host, get_hosts_from_github_ssh_url
from sshkeys.core.models import HostConfig

def test_detect_github():
    host = detect_host("git@github.com:user/repo.git")
    assert host.host_type == "github"
    assert host.alias == "github.com"
    assert host.user == "git"

def test_detect_server():
    host = detect_host("user@mon-serveur.com:2222")
    assert host.host_type == "server"
    assert host.port == 2222
    assert host.key_path == "~/.ssh/mon-serveur.com"

def test_get_hosts_from_github_ssh_url():
    url = "git@github.com:octocat/Hello-World.git"
    host = get_hosts_from_github_ssh_url(url)
    assert host.real_host == "github.com"
    assert host.user == "git"
    assert host.host_type == "github"