import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_binary_available():
    assert shutil.which("node") is not None, "Node.js binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_major_version_is_20_or_above():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version_string = result.stdout.strip()
    assert version_string.startswith("v"), (
        f"Unexpected node --version output: {version_string!r}"
    )
    major = int(version_string.lstrip("v").split(".")[0])
    assert major >= 20, (
        f"Node.js major version must be >= 20, got {version_string!r}."
    )


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Expected project directory {PROJECT_DIR} to exist before the task starts."
    )
