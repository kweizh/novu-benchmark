import os
import pytest

PROJECT_DIR = "/home/user/app"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_workflows_file_exists():
    workflows_path = os.path.join(PROJECT_DIR, "app/api/novu/workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflows file {workflows_path} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found in {PROJECT_DIR}"
