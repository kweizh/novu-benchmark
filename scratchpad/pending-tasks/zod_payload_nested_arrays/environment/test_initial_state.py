import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_version_20_or_higher():
    result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, got {version}."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_node_modules_contains_novu_framework():
    novu_pkg = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework", "package.json")
    assert os.path.isfile(novu_pkg), (
        f"@novu/framework dependency not pre-installed at {novu_pkg}."
    )


def test_node_modules_contains_express():
    express_pkg = os.path.join(PROJECT_DIR, "node_modules", "express", "package.json")
    assert os.path.isfile(express_pkg), (
        f"express dependency not pre-installed at {express_pkg}."
    )


def test_node_modules_contains_zod():
    zod_pkg = os.path.join(PROJECT_DIR, "node_modules", "zod", "package.json")
    assert os.path.isfile(zod_pkg), f"zod dependency not pre-installed at {zod_pkg}."
