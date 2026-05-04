import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/my-novu-app"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found in {PROJECT_DIR}."

def test_remix_installed():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json_path) as f:
        content = f.read()
    assert "@remix-run/react" in content or "@remix-run/node" in content, \
        "Expected Remix packages to be in package.json."
