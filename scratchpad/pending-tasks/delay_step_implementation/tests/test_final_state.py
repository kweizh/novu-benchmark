import os
import subprocess
import time
import socket
import pytest
import json
import urllib.request
import urllib.error

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

def test_workflows_discovered(start_app):
    url = "http://localhost:3000/api/novu?action=discover"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            assert response.getcode() == 200, f"Expected status code 200, got {response.getcode()}"
            data = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        pytest.fail(f"Failed to connect to the bridge endpoint: {e}")

    workflows = data.get("workflows", [])
    assert isinstance(workflows, list), "Expected 'workflows' to be a list in the response."
    
    workflow = next((w for w in workflows if w.get("workflowId") == "follow-up-workflow"), None)
    assert workflow is not None, "Workflow 'follow-up-workflow' not found in the discovered workflows."

    steps = workflow.get("steps", [])
    
    # Check for delay step
    delay_step = next((s for s in steps if s.get("type") == "delay" and s.get("stepId") == "reminder-delay"), None)
    assert delay_step is not None, "Delay step 'reminder-delay' not found in the workflow steps."

    # Check for email step
    email_step = next((s for s in steps if s.get("type") == "email" and s.get("stepId") == "follow-up-email"), None)
    assert email_step is not None, "Email step 'follow-up-email' not found in the workflow steps."
