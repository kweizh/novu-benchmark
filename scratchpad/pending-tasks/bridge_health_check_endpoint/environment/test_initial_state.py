import json
import os
import shutil
import subprocess

PROJECT_DIR = "/home/user/app"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_major_version_at_least_20():
    result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Expected Node.js >= 20, found {version}."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg), f"package.json not found at {pkg}."


def test_node_modules_installed():
    nm = os.path.join(PROJECT_DIR, "node_modules")
    assert os.path.isdir(nm), f"node_modules directory not found at {nm}."


def test_novu_framework_dependency_installed():
    novu_pkg = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework", "package.json")
    assert os.path.isfile(novu_pkg), (
        f"@novu/framework not installed at {novu_pkg}."
    )


def test_express_dependency_installed():
    express_pkg = os.path.join(PROJECT_DIR, "node_modules", "express", "package.json")
    assert os.path.isfile(express_pkg), f"express not installed at {express_pkg}."


def test_package_json_declares_novu_framework_and_express():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    assert "@novu/framework" in deps, "package.json must declare @novu/framework as a dependency."
    assert "express" in deps, "package.json must declare express as a dependency."
