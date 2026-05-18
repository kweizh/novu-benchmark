import os
import subprocess
import time
import socket
import urllib.request
import json
import pytest

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

    yield process

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_bridge_endpoint_returns_workflow(start_app):
    """Verify that the Novu Bridge is accessible and returns the workflow definition."""
    req = urllib.request.Request("http://localhost:3000/api/novu?action=discover")
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
            data = json.loads(response.read().decode())
            
            # The bridge endpoint returns workflow definitions
            workflows = data.get("workflows", [])
            workflow_ids = [w.get("workflowId") for w in workflows]
            
            assert "error-handling-workflow" in workflow_ids, \
                f"Expected 'error-handling-workflow' in workflows, got: {workflow_ids}"
                
            workflow = next(w for w in workflows if w.get("workflowId") == "error-handling-workflow")
            
            # Verify steps
            steps = workflow.get("steps", [])
            step_ids = [s.get("stepId") for s in steps]
            assert "fetch-data" in step_ids, f"Expected 'fetch-data' custom step, got: {step_ids}"
            assert "send-email" in step_ids, f"Expected 'send-email' email step, got: {step_ids}"
            
    except Exception as e:
        pytest.fail(f"Failed to fetch from Bridge endpoint: {e}")

def test_workflow_logic_in_code():
    """Fallback to checking the code logic since triggering requires Novu cloud or specific CLI setup."""
    index_path = os.path.join(PROJECT_DIR, "index.js")
    assert os.path.isfile(index_path), f"index.js not found at {index_path}"
    
    with open(index_path, "r") as f:
        content = f.read()
        
    assert "simulateError" in content, "Expected 'simulateError' in payload validation."
    assert "userId" in content, "Expected 'userId' in payload validation."
    assert "External API Failed" in content, "Expected error throwing logic for 'External API Failed'."
    assert "status" in content and "ok" in content, "Expected success return object { status: 'ok' }."
