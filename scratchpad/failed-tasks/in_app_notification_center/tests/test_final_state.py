import os
import subprocess
import time
import socket
import pytest
import json
import urllib.request
from pochi_verifier import PochiVerifier

PROJECT_DIR = "/home/user/app"

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
    # Start the app
    process = subprocess.Popen(
        ["npm", "start"],
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

def test_api_novu_endpoint(start_app):
    """Priority 3: Check the API endpoint directly."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected status 200, got {response.status}"
            data = json.loads(response.read().decode('utf-8'))
            
            # The bridge should return discovery metadata containing workflows
            workflows = data.get("workflows", [])
            workflow_names = [w.get("workflowId") for w in workflows]
            assert "welcome-user" in workflow_names, f"Expected 'welcome-user' workflow in discovery data, got: {workflow_names}"
    except Exception as e:
        pytest.fail(f"Failed to fetch or parse /api/novu: {e}")

def test_inbox_ui_rendered(start_app):
    """Priority 2: Use browser verification for the UI."""
    reason = "The frontend page must render the Novu Inbox component."
    truth = "Navigate to http://localhost:3000. Verify that the Novu Inbox component is rendered. Look for elements related to notifications, a bell icon, or a container that indicates the Novu Inbox is present."

    verifier = PochiVerifier()
    result = verifier.verify(
        reason=reason,
        truth=truth,
        use_browser_agent=True,
        trajectory_dir="/logs/verifier/pochi/test_inbox_ui_rendered"
    )
    assert result.status == "pass", f"Browser verification failed: {result.reason}"
