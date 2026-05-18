import os
import subprocess
import json
import time
import socket
import pytest

PROJECT_DIR = "/home/user/app"

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

def test_crm_endpoint(start_app):
    """Priority 1: Use curl to verify the mock CRM endpoint."""
    result = subprocess.run(
        ["curl", "-s", "http://localhost:3000/api/crm/users/123"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"curl failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert data.get("name") == "Alice", f"Expected name 'Alice', got: {data.get('name')}"
    assert data.get("company") == "Acme Corp", f"Expected company 'Acme Corp', got: {data.get('company')}"

def test_novu_bridge_endpoint(start_app):
    """Priority 1: Use curl to verify the Novu bridge endpoint returns the workflow."""
    result = subprocess.run(
        ["curl", "-s", "http://localhost:3000/api/novu?action=discover"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"curl failed: {result.stderr}"
    data = json.loads(result.stdout)
    workflows = data.get("workflows", [])
    workflow_ids = [w.get("workflowId") for w in workflows]
    assert "crm-notification" in workflow_ids, f"Expected 'crm-notification' in workflows, got: {workflow_ids}"

def test_index_js_contents():
    """Priority 3: Verify the workflow definition contains the required steps."""
    index_path = os.path.join(PROJECT_DIR, "index.js")
    assert os.path.isfile(index_path), f"{index_path} does not exist."
    with open(index_path) as f:
        content = f.read()
    
    assert "step.custom" in content, "Expected 'step.custom' in index.js"
    assert "step.email" in content, "Expected 'step.email' in index.js"
    assert "fetch(" in content or "axios" in content or "http.get" in content or "https.get" in content, "Expected an HTTP request (like fetch) in index.js"
