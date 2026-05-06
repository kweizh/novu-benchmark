import os
import subprocess
import time
import socket
import pytest
import urllib.request
import urllib.error

PROJECT_DIR = "/home/user/novu-app"

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
    # Install dependencies if not already installed (to be safe)
    if not os.path.exists(os.path.join(PROJECT_DIR, "node_modules")):
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
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_api_endpoint(start_app):
    """Priority 3: Verify the Novu Bridge endpoint is up and responds correctly."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu", method="GET")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected status 200, got {response.status}"
            body = response.read().decode("utf-8")
            assert "workflows" in body, f"Expected 'workflows' in response body, got: {body}"
    except urllib.error.URLError as e:
        pytest.fail(f"Failed to connect to /api/novu endpoint: {e}")

def test_digest_step_configuration():
    """Priority 3: Verify the code contains the digest step with 5 minutes."""
    index_path = os.path.join(PROJECT_DIR, "index.js")
    assert os.path.isfile(index_path), f"index.js not found at {index_path}"
    
    with open(index_path, "r") as f:
        content = f.read()
        
    assert "step.digest" in content, "Expected 'step.digest' to be used in index.js"
    assert "amount" in content and "5" in content, "Expected amount 5 in the digest step"
    assert "unit" in content and ("'minutes'" in content or "\"minutes\"" in content or "`minutes`" in content), "Expected unit 'minutes' in the digest step"
    assert "events.length" in content, "Expected the email step to reference 'events.length'"
