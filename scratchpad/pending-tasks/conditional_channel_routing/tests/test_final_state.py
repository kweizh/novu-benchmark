import os
import subprocess
import time
import socket
import urllib.request
import urllib.error
import pytest

PROJECT_DIR = "/home/user/project"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Install dependencies
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)
    
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
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_api_endpoint_responds(start_app):
    """Verify that the /api/novu endpoint is accessible."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu", method="GET")
        response = urllib.request.urlopen(req)
        assert response.status in [200, 400, 404, 405], f"Unexpected status code: {response.status}"
    except urllib.error.HTTPError as e:
        # Novu framework might return 400 or 405 for a plain GET without correct headers, which is fine
        assert e.code in [400, 404, 405], f"Expected endpoint to be active, got HTTP {e.code}"
    except urllib.error.URLError as e:
        pytest.fail(f"Failed to connect to /api/novu: {e.reason}")

def test_skip_logic_implemented():
    """Verify that the code contains the skip logic for the email step based on payload.critical."""
    index_path = os.path.join(PROJECT_DIR, "index.js")
    assert os.path.isfile(index_path), f"index.js not found at {index_path}"
    
    with open(index_path, "r") as f:
        content = f.read()
        
    # Check for email step definition
    assert "step.email" in content, "Expected 'step.email' to be defined in the workflow."
    
    # Check for skip logic
    assert "skip" in content, "Expected 'skip' function to be used in the step configuration."
    assert "payload.critical" in content, "Expected 'payload.critical' to be evaluated for skipping."
