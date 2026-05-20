import json
import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_major_version_at_least_20():
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Failed to invoke node --version."
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, found {version}."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"{package_json} is missing."


def test_node_modules_installed():
    node_modules = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(node_modules), f"{node_modules} should exist (deps preinstalled)."


def test_novu_framework_installed():
    pkg = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework", "package.json")
    assert os.path.isfile(pkg), "@novu/framework is not installed in node_modules."


def test_express_installed():
    pkg = os.path.join(PROJECT_DIR, "node_modules", "express", "package.json")
    assert os.path.isfile(pkg), "express is not installed in node_modules."


def test_zod_installed():
    pkg = os.path.join(PROJECT_DIR, "node_modules", "zod", "package.json")
    assert os.path.isfile(pkg), "zod is not installed in node_modules."


def test_package_json_lists_required_dependencies():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json) as f:
        data = json.load(f)
    deps = data.get("dependencies", {}) or {}
    for name in ("@novu/framework", "express", "zod"):
        assert name in deps, f"package.json dependencies must include {name}."
