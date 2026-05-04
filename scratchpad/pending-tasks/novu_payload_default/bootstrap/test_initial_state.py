import os
import pytest
import shutil

PROJECT_DIR = "/home/user/project"

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_exists():
    package_json = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json), f"package.json not found at {package_json}."

def test_novu_framework_installed():
    node_modules_novu = os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework")
    assert os.path.isdir(node_modules_novu), "@novu/framework is not installed in node_modules."

def test_zod_installed():
    node_modules_zod = os.path.join(PROJECT_DIR, "node_modules", "zod")
    assert os.path.isdir(node_modules_zod), "zod is not installed in node_modules."
