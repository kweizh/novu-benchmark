import os
import json
import re
import pytest

PROJECT_DIR = "/home/user/novu-project"

def test_project_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_dependencies():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), "package.json does not exist."
    
    with open(package_json_path, "r") as f:
        data = json.load(f)
    
    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}
    
    assert "@novu/framework" in all_deps, "@novu/framework is not installed."
    assert "zod" in all_deps, "zod is not installed."

def test_index_ts_contents():
    index_ts_path = os.path.join(PROJECT_DIR, "index.ts")
    assert os.path.isfile(index_ts_path), "index.ts does not exist."
    
    with open(index_ts_path, "r") as f:
        content = f.read()
    
    assert "premiumNotification" in content, "Workflow is not exported as premiumNotification."
    assert "premium-notification" in content, "Workflow ID premium-notification is missing."
    assert "notify-in-app" in content, "inApp step with ID notify-in-app is missing."
    assert "notify-sms" in content, "sms step with ID notify-sms is missing."
    assert "skip" in content, "Skip function is missing."
    assert "isPremium" in content, "isPremium attribute is not used."
