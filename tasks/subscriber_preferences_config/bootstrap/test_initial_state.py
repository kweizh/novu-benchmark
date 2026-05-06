import os
import subprocess

def test_nodejs_installed():
    result = subprocess.run(["node", "-v"], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.startswith("v")

def test_npm_installed():
    result = subprocess.run(["npm", "-v"], capture_output=True, text=True)
    assert result.returncode == 0

def test_home_user_exists():
    assert os.path.exists("/home/user")
    assert os.path.isdir("/home/user")
