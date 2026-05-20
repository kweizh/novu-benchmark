import os
import shutil


PROJECT_DIR = "/home/user/app"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_node_modules_installed():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(node_modules), (
        f"node_modules directory {node_modules} does not exist; dependencies must be pre-installed."
    )


def test_novu_framework_installed():
    novu_pkg = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework", "package.json")
    assert os.path.isfile(novu_pkg), (
        f"@novu/framework is not installed at {novu_pkg}."
    )


def test_express_installed():
    express_pkg = os.path.join(PROJECT_DIR, "node_modules", "express", "package.json")
    assert os.path.isfile(express_pkg), (
        f"express is not installed at {express_pkg}."
    )


def test_zod_installed():
    zod_pkg = os.path.join(PROJECT_DIR, "node_modules", "zod", "package.json")
    assert os.path.isfile(zod_pkg), f"zod is not installed at {zod_pkg}."


def test_strict_auth_env_disabled():
    val = os.environ.get("NOVU_STRICT_AUTHENTICATION_ENABLED")
    assert val is not None and val.lower() == "false", (
        "NOVU_STRICT_AUTHENTICATION_ENABLED must be set to 'false' in the environment."
    )
