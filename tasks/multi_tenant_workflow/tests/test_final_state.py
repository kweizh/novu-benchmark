import os
import subprocess
import time
import socket
import pytest
import urllib.request
import json

PROJECT_DIR = "/home/user/myproject"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Install dependencies first just in case
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, capture_output=True)

    # Start the app
    process = subprocess.Popen(
        ["node", "index.js"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(3000):
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_novu_bridge_endpoint(start_app):
    """Priority 1: Test the Novu bridge endpoint response."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu", method="GET")
        with urllib.request.urlopen(req) as response:
            assert response.getcode() == 200, f"Expected status code 200, got {response.getcode()}"
            data = json.loads(response.read().decode())
    except Exception as e:
        pytest.fail(f"Failed to fetch from /api/novu: {e}")

    # The response format depends on Novu, but it should contain workflow metadata.
    # Convert to string to easily check for presence of required keys/names.
    data_str = json.dumps(data)
    
    assert "multi-tenant-workflow" in data_str, "Workflow 'multi-tenant-workflow' not found in the bridge endpoint response."
    assert "tenantName" in data_str, "Payload schema does not include 'tenantName'."
    assert "userName" in data_str, "Payload schema does not include 'userName'."
