import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "Node.js binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_version_is_20_or_higher():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, got {version}."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_strict_authentication_env_disabled():
    value = os.environ.get("NOVU_STRICT_AUTHENTICATION_ENABLED")
    assert value == "false", (
        "NOVU_STRICT_AUTHENTICATION_ENABLED must be set to 'false' in the environment, "
        f"got {value!r}."
    )
