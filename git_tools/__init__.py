import json
import os

_version_file = os.path.join(os.path.dirname(__file__), "version.json")

if os.path.exists(_version_file):
    with open(_version_file) as f:
        _version_info = json.load(f)
        __version__ = _version_info.get("version", "0.0.0-dev")
else:
    __version__ = "0.0.0-dev"
