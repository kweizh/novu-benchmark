import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_node_version_supported():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, got {version}."


def test_novu_framework_installed():
    pkg_path = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework", "package.json")
    assert os.path.isfile(pkg_path), (
        "@novu/framework is not pre-installed in /home/user/app/node_modules."
    )


def test_express_installed():
    pkg_path = os.path.join(PROJECT_DIR, "node_modules", "express", "package.json")
    assert os.path.isfile(pkg_path), (
        "express is not pre-installed in /home/user/app/node_modules."
    )


def test_zod_installed():
    pkg_path = os.path.join(PROJECT_DIR, "node_modules", "zod", "package.json")
    assert os.path.isfile(pkg_path), (
        "zod is not pre-installed in /home/user/app/node_modules."
    )
