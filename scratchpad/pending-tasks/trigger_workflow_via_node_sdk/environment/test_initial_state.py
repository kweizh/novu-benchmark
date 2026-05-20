import os
import shutil
import subprocess


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_major_version_is_recent():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, (
        f"Expected Node.js major version >= 20 for compatibility with @novu/api, "
        f"got {version!r}."
    )


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_home_user_directory_exists():
    assert os.path.isdir("/home/user"), "/home/user directory does not exist."


def test_requests_module_available():
    # The verifier uses `requests` to drive the mock server / SDK end-to-end.
    import importlib

    assert importlib.util.find_spec("requests") is not None, (
        "Python module 'requests' is required by the verifier but is not installed."
    )
