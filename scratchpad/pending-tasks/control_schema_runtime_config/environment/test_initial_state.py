import os
import shutil


PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_strict_auth_env_disabled():
    value = os.environ.get("NOVU_STRICT_AUTHENTICATION_ENABLED")
    assert value == "false", (
        "Expected NOVU_STRICT_AUTHENTICATION_ENABLED to be 'false' in the environment, "
        f"got {value!r}."
    )
