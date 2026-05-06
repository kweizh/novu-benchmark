import os
import shutil
import pytest

PROJECT_DIR = "/home/user/app"

def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_nextjs_app_initialized():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"package.json not found in {PROJECT_DIR}."
    
    with open(package_json) as f:
        content = f.read()
    assert "next" in content, "Next.js is not listed in package.json."

def test_app_router_exists():
    app_dir = os.path.join(PROJECT_DIR, "app")
    assert os.path.isdir(app_dir), f"Next.js app directory not found at {app_dir}."
