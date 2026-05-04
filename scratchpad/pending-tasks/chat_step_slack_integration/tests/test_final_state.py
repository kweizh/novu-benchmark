import os
import subprocess
import time
import socket
import pytest
import json
import urllib.request

PROJECT_DIR = "/home/user/myproject"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(2)
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

def test_api_novu_endpoint(start_app):
    url = "http://localhost:3000/api/novu"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected status 200, got {response.status}"
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        pytest.fail(f"Failed to fetch {url}: {e}")

    assert "workflows" in data, "Expected 'workflows' array in the response."
    workflows = data["workflows"]
    
    slack_workflow = next((w for w in workflows if w.get("workflowId") == "slack-notification"), None)
    assert slack_workflow is not None, "Workflow 'slack-notification' not found in the registered workflows."
    
    steps = slack_workflow.get("steps", [])
    chat_step = next((s for s in steps if s.get("stepId") == "send-to-slack"), None)
    
    assert chat_step is not None, "Step 'send-to-slack' not found in the workflow steps."
    assert chat_step.get("type") == "chat", f"Expected step type to be 'chat', got {chat_step.get('type')}."
