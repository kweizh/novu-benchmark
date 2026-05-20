import os
import json
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_binary_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_major_version_at_least_20():
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "`node --version` failed to execute."
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Node.js major version must be >= 20, got {version}."


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_package_json_exists():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(pkg_path), f"package.json not found at {pkg_path}."


def test_novu_framework_dependency_installed():
    pkg_path = os.path.join(PROJECT_DIR, "package.json")
    with open(pkg_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    assert "@novu/framework" in deps, "@novu/framework must be listed as a dependency in package.json."
    assert "express" in deps, "express must be listed as a dependency in package.json."


def test_novu_framework_module_present():
    module_path = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework")
    assert os.path.isdir(module_path), f"@novu/framework not installed at {module_path}."


def test_express_module_present():
    module_path = os.path.join(PROJECT_DIR, "node_modules", "express")
    assert os.path.isdir(module_path), f"express not installed at {module_path}."
